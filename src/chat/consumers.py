import logging
import base64
from channels.generic.websocket import (
    AsyncJsonWebsocketConsumer,
)
from django.core.files.base import ContentFile

from chat.models import Chat, ChatStatus, Message, MessageAttachment

from channels.db import database_sync_to_async

logger = logging.getLogger(__name__)


class ActivityConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        print("connected")
        self.group_name = "chat_agent"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        print("disconnected")

    async def receive_json(self, content):
        print(content)

    async def new_chat(self, event):
        await self.send_json(event)

    async def new_message(self, event):
        await self.send_json(event)


class ChatConsumer(AsyncJsonWebsocketConsumer):
    @database_sync_to_async
    def get_chat(self, chat_id):
        return Chat.objects.get(chat_id=chat_id)

    @database_sync_to_async
    def update_chat(self, chat: Chat, **kwargs):
        return Chat.objects.filter(chat_id=chat.chat_id).update(**kwargs)

    @database_sync_to_async
    def add_agent(self, chat: Chat, user_id):
        chat.status = ChatStatus.ACTIVE
        chat.save()
        return chat.agent.add(user_id)

    @database_sync_to_async
    def get_last_message(self, chat: Chat):
        return chat.messages.last()

    async def connect(self):
        print("connected")
        self.chat_id = self.scope["url_route"]["kwargs"].get(
            "chat_id"
        )  # get uuid for unique channel
        # self.receiver_id = chat_id
        self.room_name = self.chat_id
        self.room_group_name = f"chat_{self.room_name}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        self.chat = await self.get_chat(chat_id=self.chat_id)
        self.is_first = await self.get_last_message(self.chat)
        self.agent = self.scope["user"]
        if self.agent.id:
            await self.add_agent(self.chat, self.agent.id)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )
        print("disconnected")

    @database_sync_to_async
    def add_message(self, message):
        creator_name = None
        if self.agent.id:
            creator_name = self.agent.employee.full_name
        else:
            creator_name = self.chat.client.name
        return Message.objects.create(
            chat=self.chat, message=message, creator_name=creator_name
        )

    @database_sync_to_async
    def get_message_count(self, chat: Chat):
        return chat.messages.count()

    @database_sync_to_async
    def get_client(self, chat: Chat):
        return chat.client

    @database_sync_to_async
    def add_attachments(self, attachments):
        return MessageAttachment.objects.bulk_create(attachments)

    async def receive_json(self, content):
        action = content.get("type")
        if action == "chat_message":
            message = content.get("message")
            attachments = content.get("attachments", [])
            message_attachments = []
            message_obj = await self.add_message(message)
            for attachment in attachments:
                if attachment.get("fileName") and attachment.get("base64"):
                    name = attachment.get("fileName")
                    message_attachments.append(
                        MessageAttachment(
                            message=message_obj,
                            attachment=ContentFile(
                                base64.b64decode(attachment.get("base64")),
                                name=name,
                            ),
                        )
                    )

            
            attachments_obj = await self.add_attachments(message_attachments)
            message_count = await self.get_message_count(self.chat)
            client = await self.get_client(self.chat)
            if message_count <= 1:
                await self.channel_layer.group_send(
                    "chat_agent",
                    {
                        "type": "new_chat",
                        "message": message,
                        "agent": self.agent.employee.full_name
                        if self.agent.id
                        else None,
                        "chat_id": str(self.chat.chat_id),
                        "timestamp": message_obj.timestamp.strftime(
                            "%b %d %Y, %I:%M %p"
                        ),
                        "is_first": True if self.is_first else False,
                        "client": client.name or client.email,
                        "status": self.chat.get_status_display(),
                        "attachment": [item.attachment.url for item in attachments_obj if item.attachment],
                    },
                )
            # New message to
            await self.channel_layer.group_send(
                "chat_agent",
                {
                    "type": "new_message",
                    "message": message,
                    "agent": self.agent.employee.full_name if self.agent.id else None,
                    "chat_id": str(self.chat.chat_id),
                    "timestamp": message_obj.timestamp.strftime("%b %d %Y, %I:%M %p"),
                    "is_first": True if self.is_first else False,
                    "client": self.chat.client.name or self.chat.client.email,
                    "status": self.chat.get_status_display(),
                    "attachment": [item.attachment.url for item in attachments_obj if item.attachment],
                },
            )
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": message,
                    "agent": self.agent.employee.full_name if self.agent.id else None,
                    "message_id": message_obj.id,
                    "timestamp": message_obj.timestamp.strftime("%b %d %Y, %I:%M %p"),
                    "is_first": True if self.is_first else False,
                    "attachment": [item.attachment.url for item in attachments_obj if item.attachment],
                },
            )
        elif action == "close":
            await self.update_chat(chat=self.chat, status=ChatStatus.CLOSED)
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name,
            )
        elif action == "message_seen":
            print("message_seen")
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "message_seen",
                    # "sender": self.agent.employee.full_name if self.agent.id else None,
                },
            )

    async def chat_message(self, event):
        await self.send_json(
            {
                "message": event["message"],
                "agent": event["agent"],
                "message_id": event["message_id"],
                "timestamp": event["timestamp"],
                "is_first": event["is_first"],
                "attachment": [item for item in event["attachment"]],
            }
        )

    async def user_offline(self, event):
        await self.send_json("user offline")

    @database_sync_to_async
    def update_message(self, message, **kwargs):
        return Message.objects.filter(id=message.id).update(**kwargs)

    async def message_seen(self, event):
        await self.update_message(self.chat.messages.last(), is_seen=True)
        await self.send_json(
            {
                "type": "message_seen",
            }
        )
