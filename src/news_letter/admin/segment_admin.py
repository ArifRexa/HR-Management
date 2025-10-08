from django.contrib import admin

# Register your models here.

from news_letter.models.segments import Segment


@admin.register(Segment)
class SegmentAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active")