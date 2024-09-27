import re
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.http.response import HttpResponse
from django.template.loader import get_template
from django.contrib import admin
from django.template.response import TemplateResponse
from django.utils.timesince import timesince
from chat.models import Chat, ChatPrompt, ChatUser, Message
from django.utils.html import format_html
from django.db.models import OuterRef, Subquery, DateTimeField
from django.db.models.functions import Coalesce
from django.utils import timezone
# Register your models here.


@admin.register(ChatUser)
class ChatUserAdmin(admin.ModelAdmin):
    list_display = ["email", "name"]
    search_fields = ["email", "name"]


class MessageInline(admin.TabularInline):
    model = Message
    fields = ["message", "creator_name", "is_seen"]
    extra = 0


class ChatReadUnreadFilter(admin.SimpleListFilter):
    title = "Read Status"
    parameter_name = "message__is_seen"

    def lookups(self, request, model_admin):
        return (
            (True, "Read"),
            (False, "Unread"),
        )

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        last_message = (
            Message.objects.filter(chat=OuterRef("pk"))
            .order_by("-id")
            .values("is_seen")[:1]
        )
        return queryset.annotate(last_message=Subquery(last_message)).filter(
            last_message=self.value()
        )


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ["get_client", "status"]
    inlines = [MessageInline]
    list_filter = ["status", ChatReadUnreadFilter]
    change_form_template = "admin/chat.html"
    change_list_template = "admin/chat_list.html"

    def change_view(self, request, object_id, form_url='', extra_context=None):
        context = extra_context or {}
        obj = self.get_object(request=request, object_id=object_id)
        message = Message.objects.filter(chat=obj).order_by("timestamp")
        last_message = message.last()
        if not last_message.is_seen:
            last_message.is_seen = True
            last_message.save()
        context["messages"] = message
        context["chat"] = obj
        return super().change_view(request, object_id, form_url, context)

    @admin.display(description="Client")
    def get_client(self, obj):
        from django.contrib.humanize.templatetags.humanize import naturaltime

        time = naturaltime(obj.messages.last().timestamp or timezone.now())

        html_str = (
            f"{obj.client.email}<p>{obj.messages.last().message}</p><p>{time}</p>"
        )
        return format_html(html_str)

    def changelist_view(self, request, extra_context=None):
        context = extra_context or {}
        last_message = (
            Message.objects.filter(chat=OuterRef("pk"))
            .order_by("-id")
            .values("is_seen")[:1]
        )
        d = (
            Chat.objects.annotate(last_message_seen=Subquery(last_message))
            .filter(last_message_seen=False)
            .values("last_message_seen")
        )
        context["unseen_message_count"] = (
            Chat.objects.annotate(last_message_seen=Subquery(last_message))
            .filter(last_message_seen=False)
            .count()
        )
        return super().changelist_view(request, context)

    def get_queryset(self, request):
        message_subquery = (
            Message.objects.filter(chat=OuterRef("pk"))
            .order_by("-id")
            .values("timestamp")[:1]
        )
        qs = (
            super()
            .get_queryset(request)
            .annotate(last_message=Subquery(message_subquery))
            .prefetch_related("messages")
            .order_by("-last_message")
        )

        return qs

    @admin.display(description="sender")
    def get_sender(self, obj):
        return obj.client.email

    @admin.display(description="Chat Link")
    def get_receiver(self, obj):
        html_template = get_template("chat_link.html")
        context = {"chat": obj}
        return format_html(html_template.render(context))
    
@admin.register(ChatPrompt)
class ChatPromptAdmin(admin.ModelAdmin):
    list_display = ["id", "prompt"]
