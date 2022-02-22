from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"real-time/", consumers.StreamConsumer.as_asgi()),
]
