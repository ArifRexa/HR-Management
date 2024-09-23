from django.urls import path

from . import consumers

websocket_urlpatterns = [
    # path("ws/chat/lobby/", consumers.ActivityConsumer.as_asgi()),
    path(
        "ws/chat/",
        consumers.ChatConsumer.as_asgi(),
    ),
]