from django.contrib import admin
from .models import Pattern, ScannedMessage

@admin.register(Pattern)
class PatternAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

@admin.register(ScannedMessage)
class ScannedMessageAdmin(admin.ModelAdmin):
    list_display = ('content', 'detected', 'matched_pattern', 'scanned_at')
    list_filter = ('detected', 'matched_pattern')
    search_fields = ('content',)
