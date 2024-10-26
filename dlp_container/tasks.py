import os
import re
import requests

# Example task: Scan for sensitive patterns (e.g., credit card numbers)
async def scan_for_sensitive_data(message_content):
    # Fetch patterns from the Django API
    response = requests.get(os.getenv('DLP_API_PATTERNS_URL'))
    patterns = response.json()

    for pattern in patterns:
        regex = re.compile(pattern['regex'])
        match = regex.search(message_content)
        if match:
            # Found sensitive data, send results to Django API
            requests.post(os.getenv('DLP_API_SAVE_MATCH_URL'), json={
                "content": message_content,
                "detected": True,
                "matched_pattern": pattern['id']
            })
            return
    # No sensitive data found
    requests.post(os.getenv('DLP_API_SAVE_MATCH_URL'), json={
        "content": message_content,
        "detected": False
    })

tasks = [
    scan_for_sensitive_data,
]