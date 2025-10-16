from django.contrib import admin

# Register your models here.

from news_letter.models.case_study_subscriber import CaseStudySubscriber
@admin.register(CaseStudySubscriber)
class CaseStudySubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "project_title", "is_subscribed")
    list_filter = ("is_subscribed", "project_title")