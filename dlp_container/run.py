import os
import asyncio
from dlp_manager import DLPManager
from tasks import tasks

queue_name = os.getenv('QUEUE_NAME')
environment = os.getenv('QUEUE_SERVICE')

if __name__ == '__main__':
    manager = DLPManager(queue_name=queue_name, environment=environment, tasks=tasks)
    asyncio.run(manager.main())