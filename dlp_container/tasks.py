import os
import re
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Example task: Scan for sensitive patterns (e.g., credit card numbers)
async def scan_for_sensitive_data(*args, **kwargs):
    logger.info("Starting scan for sensitive data.")
    logger.info(f"Args: {args}")
    logger.info(f"Kwargs: {kwargs}")

    message_content = kwargs.get('message')
    
    # Fetch patterns from the Django API
    try:
        response = requests.get(os.getenv('DLP_API_PATTERNS_URL'))
        response.raise_for_status()
        patterns = response.json()
        logger.info("Fetched patterns from the Django API.")
    except requests.RequestException as e:
        logger.error(f"Failed to fetch patterns: {e}")
        return

    for pattern in patterns:
        regex = re.compile(pattern['regex'])
        match = regex.search(message_content)
        if match:
            logger.info(f"Sensitive data found: {match.group()}")
            # Found sensitive data, send results to Django API
            try:
                requests.post(os.getenv('DLP_API_SAVE_MATCH_URL'), json={
                    "content": message_content,
                    "detected": True,
                    "matched_pattern": pattern['id']
                })
                logger.info("Reported sensitive data to the Django API.")
            except requests.RequestException as e:
                logger.error(f"Failed to report sensitive data: {e}")
            return

    # No sensitive data found
    try:
        requests.post(os.getenv('DLP_API_SAVE_MATCH_URL'), json={
            "content": message_content,
            "detected": False
        })
        logger.info("No sensitive data found, reported to the Django API.")
    except requests.RequestException as e:
        logger.error(f"Failed to report no sensitive data: {e}")

tasks = {
    "dlp": scan_for_sensitive_data
}