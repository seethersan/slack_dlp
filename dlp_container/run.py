import os
import asyncio
import logging
import traceback
from manager import Manager
from tasks import tasks

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

queue_name = os.getenv('QUEUE_NAME')
environment = os.getenv('QUEUE_SERVICE')

logger.info(f"Starting Manager with queue: {queue_name}, environment: {environment}")

manager = Manager(queue_name=queue_name, environment=environment, tasks=tasks)
try:
    asyncio.run(manager.main())
except Exception as e:
    print(traceback.format_exc())
    logger.error(f"An error occurred while running Manager: {e}")