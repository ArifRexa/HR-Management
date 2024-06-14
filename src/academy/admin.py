from django.contrib import admin

from academy.models import (
    MarketingSlider,
    Training,
    TrainingLearningTopic,
    TrainingOutline,
    TrainingProject,
    TrainingStructure,
    TrainingStructureModule,
    TrainingTechnology,
)


@admin.register(TrainingStructureModule)
class TrainingStructureModuleAdmin(admin.ModelAdmin):
    list_display = ("id", "training_structure")


# Register your models here.
@admin.register(TrainingStructure)
class TrainingStructureAdmin(admin.ModelAdmin):
    list_display = ("id", "week")
    date_hierarchy = "created_at"
    search_fields = ["week"]


@admin.register(MarketingSlider)
class MarketingSliderAdmin(admin.ModelAdmin):
    list_display = ("id", "title")
    date_hierarchy = "created_at"
    search_fields = ["title"]


class TrainingProjectInline(admin.StackedInline):
    model = TrainingProject
    extra = 1


class TrainingTechnologyInline(admin.StackedInline):
    model = TrainingTechnology
    extra = 1


class TrainingOutlineInline(admin.StackedInline):
    model = TrainingOutline
    extra = 1


class TrainingStructureModuleInline(admin.StackedInline):
    model = TrainingStructureModule
    extra = 1
    autocomplete_fields = ("training_structure",)


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
        TrainingStructureModuleInline,
        TrainingTechnologyInline,
    ]
