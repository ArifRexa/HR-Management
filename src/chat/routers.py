from django.urls import path

from . import consumers

websocket_urlpatterns = [
    # path("ws/chat/lobby/", consumers.ActivityConsumer.as_asgi()),
    path(
        "ws/chat/<str:chat_id>/",consumers.ChatConsumer.as_asgi()),
    path(
        "ws/new-chat/",consumers.ActivityConsumer.as_asgi()),
]