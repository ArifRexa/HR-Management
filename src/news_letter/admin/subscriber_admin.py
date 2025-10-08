from django.contrib import admin

# Register your models here.

from news_letter.models.subscriber import Subscriber

@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "is_subscribed", "is_verified", "segment")
    list_filter = ("is_subscribed", "is_verified", "segment")