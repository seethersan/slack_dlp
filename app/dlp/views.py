import hashlib
import hmac
import json
import time
import os
import logging
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import pika
import boto3

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Verify Slack Request
def verify_slack_request(request):
    slack_signature = request.headers.get('X-Slack-Signature')
    slack_request_timestamp = request.headers.get('X-Slack-Request-Timestamp')

    if abs(time.time() - int(slack_request_timestamp)) > 60 * 5:
        logger.warning("Slack request timestamp is too old.")
        return False

    sig_basestring = f'v0:{slack_request_timestamp}:{request.body.decode("utf-8")}'
    calculated_signature = 'v0=' + hmac.new(
        settings.SLACK_SIGNING_SECRET.encode(),
        sig_basestring.encode(),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(calculated_signature, slack_signature):
        logger.warning("Slack request signature mismatch.")
        return False

    logger.info("Slack request verified successfully.")
    return True

# Push message to RabbitMQ or SQS
def push_to_queue(message):
    message_body = json.dumps({
        "task": "dlp",
        "kwargs": message
    })
    if settings.QUEUE_SERVICE == 'rabbitmq':
        try:
            queue = os.getenv('QUEUE_NAME')
            connection = pika.BlockingConnection(pika.URLParameters(os.getenv('RABBITMQ_URL')))
            channel = connection.channel()
            channel.queue_declare(queue=queue, durable=True)
            logger.info(f"Pushing message: {message}")
            channel.basic_publish(exchange='',
                                  routing_key=queue,
                                  body=message_body,
                                  properties=pika.BasicProperties(
                                      delivery_mode=2,
                                  ))
            connection.close()
            logger.info("Message pushed to RabbitMQ queue.")
        except Exception as e:
            logger.error(f"Failed to push message to RabbitMQ: {e}")
    elif settings.QUEUE_SERVICE == 'sqs':
        try:
            sqs = boto3.client('sqs')
            queue_url = os.getenv('AWS_SQS_QUEUE_URL')
            sqs.send_message(
                QueueUrl=queue_url,
                MessageBody=message_body
            )
            logger.info("Message pushed to SQS queue.")
        except Exception as e:
            logger.error(f"Failed to push message to SQS: {e}")

@csrf_exempt
def slack_event_listener(request):
    if request.method == 'POST':
        if not verify_slack_request(request):
            return HttpResponseForbidden("Invalid Slack request.")

        slack_event = json.loads(request.body)
        logger.info(f"Received Slack event: {slack_event}")

        # Handle URL verification (Slack challenge request)
        if "challenge" in slack_event:
            logger.info("Handling Slack challenge request.")
            return JsonResponse({"challenge": slack_event["challenge"]})

        # Handle message events
        if 'event' in slack_event:
            event = slack_event['event']

            # Check if it's a message from a channel
            if event.get('type') == 'message' and 'subtype' not in event:
                message_content = event.get('text')
                logger.info(f"Received message: {message_content}")
                # Push message content to the queue
                push_to_queue({"message": message_content})

        return JsonResponse({"status": "ok"})

    logger.warning("Invalid request method.")
    return JsonResponse({"status": "invalid method"}, status=405)
