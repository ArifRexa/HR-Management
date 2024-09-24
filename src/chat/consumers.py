import os
import base64
import logging
from channels.generic.websocket import (
    AsyncJsonWebsocketConsumer,
)
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.core.files.base import ContentFile
from django.contrib.contenttypes.models import ContentType

from chat.models import Chat


class ChatConsumer(AsyncJsonWebsocketConsumer):
    receiver_id: int

    # @database_sync_to_async
    # async def get_user(self, user_id):
    #     return User.objects.aget(id=user_id)

    async def connect(self):
        print("connected")
        receiver_id = int(self.scope["url_route"]["kwargs"].get("receiver")) # get uuid for unique channel
        self.receiver_id = receiver_id
        self.room_name = receiver_id
        self.room_group_name = f"chat_{self.room_name}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        participants = {receiver_id, self.scope["user"].id}
        # existing_chat = (
        #     await Chat.objects.annotate(
        #         count_participants=Count(
        #             "participants",
        #             filter=Q(participants__id__in=list(participants)),
        #         )
        #     )
        #     .filter(count_participants=len(participants))
        #     .afirst()
        # )
        # if existing_chat:
        #     self.chat = existing_chat
        # else:
        if (
            receiver_id
            and self.scope["user"].id
            and (receiver_id != self.scope["user"].id)
        ):
            chat = Chat(chat_id=self.receiver_id)
            await chat.asave()
            await chat.participants.aadd(*participants)
            self.chat = chat
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )
        print("disconnected")

    async def receive(self, text_data, *args, **kwargs):
        event = await self.decode_json(text_data)
        attachments = event.get("attachments", [])
        message_attachments = []
        user = self.scope["user"]
        # user_image = (ws_media_baseurl + user.image.url) if user.image else None
        print("event,", event)
        if event.get("type") == "chat_message":
            print("chat_message", event)
            # tagged_item = event.get("tagged_item", {})
            # message = await Message.objects.acreate(
            #     message=event.get("message"),
            #     sender=user,
            #     chat=self.chat,
            #     content_type_id=tagged_item.get("content_type"),
            #     object_id=tagged_item.get("object_id"),
            # )
            # self.chat.last_message = message
            # for attachment in attachments:
            #     if attachment.get("name") and attachment.get("base64"):
            #         name = attachment.get("name")
            #         message_attachments.append(
            #             MessageAttachment(
            #                 message=message,
            #                 attachment=ContentFile(
            #                     base64.b64decode(attachment.get("base64")),
            #                     name=name,
            #                 ),
            #             )
            #         )
            # attachments = await MessageAttachment.objects.abulk_create(
            #     message_attachments
            # )
            # await self.chat.asave()
            # if content_type := await ContentType.objects.filter(
            #     id=tagged_item.get("content_type")
            # ).afirst():
            #     tagged_item = {
            #         "app_label": content_type.app_label,
            #         "model": content_type.model,
            #         "object_id": message.object_id,
            #     }

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat.message",
                    "message": event.get("message"),
                    "username": "username",
                },
            )

        elif event.get("type") == "message_seen":
            pass
        print("receive", text_data)

    async def chat_message(self, event):
        message = event["message"]
        username = event["username"]

        # Send message to WebSocket
        # await self.send(text_data=json.dumps({
        #     'message': message,
        #     'username': username
        # }))
        await self.send_json({"message": message, "username": username})

    # async def chat_message(self, event):
    #     message = event["message"]
    #     sender = event["sender"]
    #     chat_id = event["chat_id"]
    #     message_id = event["message_id"]
    #     await self.send_json(
    #         {
    #             "type": "chat_message",
    #             "user_id": sender.get("id"),
    #             "chat_id": chat_id,
    #             "message_id": message_id,
    #             "timestamp": event["timestamp"],
    #             "message": message,
    #             "attachments": event.get("attachments", []),
    #             "has_attachment": bool(event.get("attachments", [])),
    #             "tagged_item": event.get("tagged_item", None),
    #             "sender": {
    #                 **sender,
    #                 "is_me": self.scope["user"].id == sender.get("id"),
    #             },
    #         }
    #     )

    async def user_offline(self, event):
        await self.send_json("user offline")

    async def message_seen(self, event):
        sender = event["sender"]
        await self.send_json(
            {
                "type": "message_seen",
                # "message_id": message_id,
                # "message": message,
                "sender": {
                    **sender,
                    "is_me": self.scope["user"].id == sender.get("id"),
                },
            }
        )
