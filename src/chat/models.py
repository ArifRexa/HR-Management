import uuid
from django.db import models
from django.contrib.auth import get_user_model
from config.model.TimeStampMixin import TimeStampMixin

# Create your models here.
User = get_user_model()


class ChatUser(TimeStampMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
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
    chat_id = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
    agent = models.ForeignKey(
        User, related_name="chats", on_delete=models.SET_NULL, null=True, blank=True
    )
    sender = models.ForeignKey(
        ChatUser, related_name="chats", on_delete=models.CASCADE, null=True, blank=True
    )
    status = models.SmallIntegerField(
        choices=ChatStatus.choices, default=ChatStatus.WAITING
    )

    def __str__(self):
        return f"Message {self.chat_id} from {self.sender} at {self.timestamp}"

    class Meta:
        verbose_name = "Chat"
        verbose_name_plural = "Chat"


class Message(TimeStampMixin):
    chat = models.ForeignKey(Chat, related_name="messages", on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    # seen_by = models.ManyToManyField(User, blank=True)
    # content_object = GenericForeignKey("content_type", "object_id")

    def __str__(self):
        return f"Message {self.id} from {self.sender} at {self.timestamp}"

    class Meta:
        ordering = ["-id"]


class MessageAttachment(models.Model):
    message = models.ForeignKey(
        Message, related_name="attachments", on_delete=models.CASCADE
    )
    attachment = models.FileField(upload_to="chat/attachments")
