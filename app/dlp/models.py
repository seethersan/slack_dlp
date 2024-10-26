from django.db import models

class Pattern(models.Model):
    name = models.CharField(max_length=255)
    regex = models.TextField(help_text="Regular expression pattern to detect sensitive data")
    description = models.TextField(null=True, blank=True, help_text="Description of the pattern")

    def __str__(self):
        return self.name

class ScannedMessage(models.Model):
    content = models.TextField(help_text="The content of the message or file scanned")
    detected = models.BooleanField(default=False, help_text="Whether sensitive data was detected")
    matched_pattern = models.ForeignKey(Pattern, on_delete=models.SET_NULL, null=True, blank=True)
    scanned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Scanned on {self.scanned_at} - Detected: {self.detected}"
