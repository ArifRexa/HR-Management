from django.contrib import admin

from academy.models import (
    MarketingSlider,
    Training,
    TrainingLearningTopic,
    TrainingOutline,
    TrainingProject,
    TrainingStructure,
    TrainingTechnology,
)

# Register your models here.


@admin.register(MarketingSlider)
class MarketingSliderAdmin(admin.ModelAdmin):
    list_display = ("id", "title")
    date_hierarchy = "created_at"
    search_fields = ["title"]


class TrainingProjectInline(admin.StackedInline):
    model = TrainingProject
    extra = 1


class TrainingOutlineInline(admin.StackedInline):
    model = TrainingOutline
    extra = 1


class TrainingStructureInline(admin.StackedInline):
    model = TrainingStructure
    extra = 1


class TrainingLearningTopicInline(admin.StackedInline):
    model = TrainingLearningTopic
    extra = 1


@admin.register(TrainingTechnology)
class TrainingTechnologyAdmin(admin.ModelAdmin):
    list_display = ("id", "title")
    date_hierarchy = "created_at"
    search_fields = ["title"]


@admin.register(Training)
class TrainingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "description",
        "duration",
    )
    date_hierarchy = "created_at"
    search_fields = ["title"]
    inlines = [
        TrainingLearningTopicInline,
        TrainingProjectInline,
        TrainingOutlineInline,
        TrainingStructureInline,
    ]
