from django.core.management.base import BaseCommand
from dlp.models import Pattern

class Command(BaseCommand):
    help = 'Create default regex patterns for detecting sensitive information'

    def handle(self, *args, **kwargs):
        patterns = [
            {
                "name": "Credit Card Number",
                "regex": r"(?:\d[ -]*?){13,16}",
                "description": "Matches Visa, MasterCard, Amex, and Discover card numbers."
            },
            {
                "name": "Social Security Number",
                "regex": r"\b\d{3}-\d{2}-\d{4}\b",
                "description": "Matches US Social Security Numbers (SSNs)."
            },
            {
                "name": "Passport Number",
                "regex": r"\b[A-PR-WYa-pr-wy][1-9]\d\s?\d{4}[1-9]\b",
                "description": "Matches generic passport numbers."
            },
            {
                "name": "Driver's License Number",
                "regex": r"\b[A-Z0-9]{1,9}\b",
                "description": "Matches US driver's license numbers."
            }
        ]

        for pattern_data in patterns:
            pattern, created = Pattern.objects.get_or_create(
                name=pattern_data['name'],
                regex=pattern_data['regex'],
                description=pattern_data['description']
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created pattern: {pattern.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Pattern already exists: {pattern.name}"))
