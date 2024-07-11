from django.contrib import admin

from academy.models import (
    HomePageWhyBest,
    InstructorFeedback,
    MarketingSlider,
    SuccessStory,
    Training,
    TrainingLearningTopic,
    TrainingOutline,
    TrainingProject,
    TrainingStructure,
    TrainingStructureModule,
    TrainingTechnology,
    Student,
)


from django import forms
from project_management.models import ProjectTechnology


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "email", "phone"]
    search_fields = ["name", "email"]
    date_hierarchy = "created_at"


class ProjectTechnologyInlineForm(forms.ModelForm):
    title = forms.CharField(label="Title", widget=forms.TextInput)

    class Meta:
        model = TrainingTechnology
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate choices with distinct titles
        distinct_titles = ProjectTechnology.objects.values_list(
            "title", flat=True
        ).distinct()
        choices = [(title, title) for title in distinct_titles]
        self.fields["title"].widget = forms.Select(choices=[("", "---")] + choices)
        self.fields["title"].widget.attrs.update({"class": "select2"})


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
    form = ProjectTechnologyInlineForm


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
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "created_at"
    search_fields = ["title"]
    inlines = [
        TrainingLearningTopicInline,
        TrainingProjectInline,
        TrainingOutlineInline,
        TrainingStructureModuleInline,
        TrainingTechnologyInline,
    ]


@admin.register(SuccessStory)
class SuccessStoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    date_hierarchy = "created_at"
    search_fields = ["name"]


@admin.register(InstructorFeedback)
class InstructorFeedbackAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    date_hierarchy = "created_at"
    search_fields = ["name"]


@admin.register(HomePageWhyBest)
class HomePageWhyBestAdmin(admin.ModelAdmin):
    list_display = ("id", "title")
    date_hierarchy = "created_at"
    search_fields = ["title"]
