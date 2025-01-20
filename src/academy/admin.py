from django.contrib import admin

from academy.models import (
    AllTrainingBanner,
    HomeBanner,
    HomePageWhyBest,
    InstructorBanner,
    InstructorFeedback,
    MarketingSlider,
    PageBanner,
    SuccessStory,
    SuccessStoryBanner,
    Training,
    TrainingLearningTopic,
    TrainingOutline,
    TrainingProject,
    TrainingStructure,
    TrainingStructureModule,
    TrainingTechnology,
    Student,
    OurAchievement,
    FAQ,
    TrainingProgram,
    TrainingReason,
    TrainingFor,
    Training_Outline,
    PracticeProject,
    ProjectShowcase,
    StudentReview,
    TrainingFAQ,
    Instructor,
    FeatureHighlight,
)


from django import forms
from project_management.models import ProjectTechnology


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("id", "question")
    list_display_links = ("id", "question")


@admin.register(OurAchievement)
class OurAchievementAdmin(admin.ModelAdmin):
    list_display = ("title", "number")


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


class TrainingReasonInline(admin.TabularInline):
    model = TrainingReason
    extra = 1


class TrainingForInline(admin.TabularInline):
    model = TrainingFor
    extra = 1


class TrainingOutlineInline(admin.TabularInline):
    model = Training_Outline
    extra = 1


class ProjectShowcaseInline(admin.TabularInline):
    model = ProjectShowcase
    extra = 1


class StudentReviewInline(admin.TabularInline):
    model = StudentReview
    extra = 1


class TrainingFAQInline(admin.TabularInline):
    model = TrainingFAQ
    extra = 1


@admin.register(TrainingProgram)
class TrainingProgramAdmin(admin.ModelAdmin):
    inlines = [
        TrainingReasonInline,
        TrainingForInline,
        TrainingOutlineInline,
        ProjectShowcaseInline,
        StudentReviewInline,
        TrainingFAQInline,
    ]
    list_display = ("title", "course_fee", "video", "status")  # Adjust fields as needed
    search_fields = ("title", "description")  # Adjust fields as needed
    list_filter = ("course_fee", "program_active_status")

    # Custom method for "status"
    def status(self, obj):
        return obj.program_active_status

    status.short_description = "Status"  # Set the display name in the admin

    # Custom actions
    actions = ["make_active", "make_deactive", "make_pending"]

    def make_active(self, request, queryset):
        queryset.update(program_active_status='active')
        self.message_user(request, "Selected programs have been marked as Active.")

    def make_deactive(self, request, queryset):
        queryset.update(program_active_status='deactive')
        self.message_user(request, "Selected programs have been marked as Deactive.")

    def make_pending(self, request, queryset):
        queryset.update(program_active_status='pending')
        self.message_user(request, "Selected programs have been marked as Pending.")

    make_active.short_description = "Mark selected programs as Active"
    make_deactive.short_description = "Mark selected programs as Deactive"
    make_pending.short_description = "Mark selected programs as Pending"


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ("name", "designation", "rating")  # Adjust fields as needed


class FeatureHighlightInline(admin.TabularInline):
    model = FeatureHighlight
    extra = 1


@admin.register(PracticeProject)
class PracticeProjectAdmin(admin.ModelAdmin):
    inlines = (FeatureHighlightInline,)
    list_display = ("title", "description", "slug")


class BaseBannerInline(admin.StackedInline):
    extra = 1
    can_delete = False


class HomeBannerInline(BaseBannerInline):
    model = HomeBanner
    verbose_name = "Home Banner"


class AllTrainingsInline(BaseBannerInline):
    model = AllTrainingBanner
    verbose_name = "All Trainings Banner"


class InstructorBannerInline(BaseBannerInline):
    model = InstructorBanner
    verbose_name = "Instructor Banner"


class SuccessStoryBannerInline(BaseBannerInline):
    model = SuccessStoryBanner
    verbose_name = "Success Story Banner"


@admin.register(PageBanner)
class PageBannerAdmin(admin.ModelAdmin):
    inlines = (
        HomeBannerInline,
        AllTrainingsInline,
        InstructorBannerInline,
        SuccessStoryBannerInline,
    )
