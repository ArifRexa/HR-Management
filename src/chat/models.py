import uuid
import mimetypes
from django.db import models
from django.contrib.auth import get_user_model

from config.model.TimeStampMixin import TimeStampMixin

# Create your models here.
User = get_user_model()


class ChatUser(TimeStampMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Chat User"
        verbose_name_plural = "Chat Users"


class ChatStatus(models.IntegerChoices):
    WAITING = 1, "Waiting"
    ACTIVE = 2, "Active"
    CLOSED = 3, "Closed"


class Chat(TimeStampMixin):
    chat_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent = models.ManyToManyField(User, related_name="chats", blank=True)
    client = models.OneToOneField(
        ChatUser, related_name="chats", on_delete=models.CASCADE, null=True, blank=True
    )
    status = models.SmallIntegerField(
        choices=ChatStatus.choices, default=ChatStatus.WAITING
    )

    def __str__(self):
        return f"Message {self.chat_id} from {self.client} at {self.created_at}"

    class Meta:
        verbose_name = "Chat"
        verbose_name_plural = "Chat"


class Message(TimeStampMixin):
    chat = models.ForeignKey(Chat, related_name="messages", on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    creator_name = models.CharField(max_length=255, null=True, blank=True)
    is_seen = models.BooleanField(default=False)
    # seen_by = models.ManyToManyField(User, blank=True)
    # content_object = GenericForeignKey("content_type", "object_id")

    def __str__(self):
        return f"Message {self.id} from {self.chat} at {self.timestamp}"

    class Meta:
        ordering = ["-id"]


class MessageAttachment(models.Model):
    message = models.ForeignKey(
        Message, related_name="attachments", on_delete=models.CASCADE
    )
    attachment = models.FileField(upload_to="chat/attachments")

    @property
    def content_type(self):
        return mimetypes.guess_type(self.attachment.name)[0]

    @property
    def is_image(self):
        return self.content_type.startswith("image/")


class ChatPrompt(TimeStampMixin):
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="childrens",
    )
    prompt = models.TextField()

    def __str__(self):
        return self.prompt[:30]
