import asyncio
import json
import os
import pika
import boto3
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Manager:

    def __init__(self, queue_name: str, tasks: dict, environment: str = 'rabbitmq'):
        self.queue = queue_name
        self.tasks = tasks
        self.environment = environment
        self.connection = None
        self.channel = None

        if self.environment == 'sqs':
            self.sqs = boto3.client('sqs')

        logger.info(f"Manager initialized with queue: {queue_name}, environment: {environment}")

    async def _get_messages_rabbitmq(self):
        if not self.connection:
            self.connection = pika.BlockingConnection(pika.URLParameters(os.getenv('RABBITMQ_URL')))
            logger.info("RabbitMQ connection established.")
        if not self.channel:
            self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue, durable=True)
        logger.info(f"RabbitMQ queue declared: {self.queue}")

        method_frame, header_frame, body = self.channel.basic_get(queue=self.queue)
        if method_frame:
            self.channel.basic_ack(method_frame.delivery_tag)
            logger.info(f"Message received from RabbitMQ: {body}")
            return [body]
        logger.info("No messages in RabbitMQ queue.")
        return []

    async def _get_messages_sqs(self):
        response = self.sqs.receive_message(
            QueueUrl=os.getenv('AWS_SQS_QUEUE_URL'),
            MaxNumberOfMessages=10
        )
        messages = response.get('Messages', [])
        logger.info(f"Messages received from SQS: {messages}")
        return messages

    async def _get_messages(self):
        if self.environment == 'rabbitmq':
            return await self._get_messages_rabbitmq()
        elif self.environment == 'sqs':
            return await self._get_messages_sqs()

    async def main(self):
        while True:
            messages = await self._get_messages()
            for message in messages:
                body = message['Body'] if self.environment == 'sqs' else message
                body = json.loads(body)

                task_name = body.get('task')
                args = body.get('args', ())
                kwargs = body.get('kwargs', {})

                task = self.tasks.get(task_name)
                if task:
                    logger.info(f"Executing task: {task_name} with args: {args} and kwargs: {kwargs}")
                    asyncio.create_task(task(*args, **kwargs))
                else:
                    logger.warning(f"Task not found: {task_name}")

            await asyncio.sleep(1)
