from django.urls import path
from core import consumers

websocket_urlpatterns = [
    path('ws/transport/', consumers.YourConsumer.as_asgi()),
]
