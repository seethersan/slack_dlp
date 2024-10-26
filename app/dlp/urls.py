from django.urls import path
from dlp import views
from dlp.api import views as api_views

urlpatterns = [
    path('slack/events/', views.slack_event_listener, name='slack_event_listener'),
    path('api/patterns/', api_views.get_patterns, name='get_patterns'),
    path('api/save_match/', api_views.save_scan_result, name='save_scan_result'),
]
