from django.urls import path
from . import views

urlpatterns = [
    path('slack/events/', views.slack_event_listener, name='slack_event_listener'),
]
