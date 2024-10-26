import asyncio
import json
import os
import pika
import boto3

class DLPManager:

    def __init__(self, queue_name: str, tasks: dict, environment: str = 'rabbitmq'):
        self.loop = asyncio.get_event_loop()
        self.queue = queue_name
        self.tasks = tasks
        self.environment = environment
        self.connection = None

        if self.environment == 'sqs':
            self.sqs = boto3.client('sqs')

    async def _get_messages_rabbitmq(self):
        if not self.connection:
            self.connection = pika.BlockingConnection(pika.URLParameters(os.getenv('RABBITMQ_URL')))
        channel = self.connection.channel()
        channel.queue_declare(queue=self.queue, durable=True)

        method_frame, header_frame, body = channel.basic_get(queue=self.queue)
        if method_frame:
            channel.basic_ack(method_frame.delivery_tag)
            return [json.loads(body)]
        return []

    async def _get_messages_sqs(self):
        response = self.sqs.receive_message(
            QueueUrl=os.getenv('AWS_SQS_QUEUE_URL'),
            MaxNumberOfMessages=10
        )
        return response.get('Messages', [])

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
                self.loop.create_task(task(*args, **kwargs))

            await asyncio.sleep(1)
