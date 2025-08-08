from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns
from job_board.views.apis.job_preference_request import JobPreferenceRequestAPIView
from rest_framework.routers import DefaultRouter
from website.models import LifeAtMediusware
from website.views import (
    AwardListView,
    BenefitsOfEmploymentListAPIView,
    ClientListAPIView,
    ClientLogoListView,
    ClientReviewListAPIView,
    ContactFormView,
    ContactModelViewSet,
    EmployeeTestimonialListAPIView,
    GalleryListView,
    IndustryWeServeListAPIView,
    InquiryModelViewSet,
    LeadershipAPIView,
    LifeAtMediuswareListView,
    OfficeLocationListView,
    PageBannerListAPIView,
    PostCredentialCreateView,
    PreviewBlogRetrieveAPIView,
    ProjectTechnologyListAPIView,
    ProjectVideoListAPIView,
    ServiceList,
    ServiceDetails,
    ProjectList,
    ProjectSitemapView,
    ProjectDetails,
    EmployeeList,
    SubscriptionModelViewSet,
    TechnologyNavigationView,
    VideoTestimonialListAPIView,
    index,
    EmployeeDetails,
    CategoryListView,
    CategoryListViewWithBlogCount,
    TagListView,
    BlogListView,
    BlogSitemapView,
    BlogDetailsView,
    VerifyDocuments,
    BlogCommentAPIView,
    BlogCommentDetailAPIView,
    BlogNextCommentDetailAPIView,
    DesignationListView,
    EmployeeWithDesignationView,
    AvailableTagsListView,
    OurTechnologyListView,
    FAQListView,
    OurClientsFeedbackList,
    OurAchievementListView,
    OurGrowthListView,
    OurJourneyListView,
    EmployeePerspectiveListView,
    BlogCommentDeleteAPIView,
    MostPopularBlogListView,
    FeaturedBlogListView,
    BlogListByAuthorAPIView,
    IndustryListView,
    MainEmployeeListView,
    SkillListView,
    LeadCreateAPIView,
    SpecialProjectListView,BrandListCreateAPIView,WebsiteTitleView,
    plagiarism_webhook, export_pdf, plagiarism_webhook_export
)
from website.views_v2.hire_views import (
    HireResourcePageDetailView,
    HireResourcePageListView,
    HireResourcePageSitemapView,
)
from website.views_v2.industries_we_serve import (
    IndustryServeDetailView,
    IndustryServeListView,
    IndustryServeSitemapListView,
)
from website.views_v2.services import ServiceListView, ServicePageDetailView,ServicePageSitemapListView
from website.views_v2.woman_empowerments_views import WomanEmpowermentView
from website.views_v2.csr_views import CSRListAPIView


api_urls = [
    path("services/", ServiceList.as_view(), name="service.list"),
    path("services/<str:slug>/", ServiceDetails.as_view(), name="service.details"),
    path("service-page/", ServiceListView.as_view(), name="service.list"),
    path("service-page/sitemap/",ServicePageSitemapListView.as_view(),name='service-page.sitemap'),
    path(
        "service-page/<str:slug>/",
        ServicePageDetailView.as_view(),
        name="service.details",
    ),
    path("industries/", IndustryListView.as_view(), name="industry-list"),
    path("projects/", ProjectList.as_view(), name="project.list"),
    path("projects/sitemap", ProjectSitemapView.as_view(), name="project.sitemap"),
    path(
        "projects/available_tags/", 
        AvailableTagsListView.as_view(),
        name="available.tags",
    ),

    path("projects/<str:slug>/", ProjectDetails.as_view(), name="project.details"),
    path(
        "special_projects/", SpecialProjectListView.as_view(), name="special_projects"
    ),
    path("employees/", EmployeeList.as_view(), name="employee.list"),
    path(
        "employees/operation",
        MainEmployeeListView.as_view(),
        name="employee.operation.list",
    ),
    path("employee/<str:slug>/", EmployeeDetails.as_view(), name="employee.details"),
    path(
        "employees/designations/", DesignationListView.as_view(), name="all-designation"
    ),
    path("employees/skills/", SkillListView.as_view(), name="all-skills"),
    path(
        "employees/designations/<str:designation>/",
        EmployeeWithDesignationView.as_view(),
        name="employee-skill-list",
    ),
    # path("categories/", CategoryListView.as_view(), name="blog.category.list"),
    path(
        "blogs/categories/",
        CategoryListViewWithBlogCount.as_view(),
        name="blog.category.list",
    ),
    path("blogs/tags/", TagListView.as_view(), name="blog.tag.list"),
    path("blogs/", BlogListView.as_view(), name="blog.list"),
    path("blogs/sitemap", BlogSitemapView.as_view(), name="blog.sitemap"),
    path(
        "blogs/most_popular",
        MostPopularBlogListView.as_view(),
        name="blog.list.most.popular",
    ),
    path(
        "blogs/featured_blogs",
        FeaturedBlogListView.as_view(),
        name="blog.list.featured",
    ),
    path("blogs/comments/", BlogCommentAPIView.as_view(), name="blog-comments"),
    path(
        "blogs/<int:pk>/comments/",
        BlogCommentDetailAPIView.as_view(),
        name="blog-comment",
    ),
    path(
        "blogs/<int:blog_id>/comments/<int:comment_id>/delete",
        BlogCommentDeleteAPIView.as_view(),
        name="blog-comment-delete",
    ),
    path(
        "blogs/<int:blog_id>/comments/<int:comment_parent_id>/replies/",
        BlogNextCommentDetailAPIView.as_view(),
        name="blog-next-comment",
    ),
    path(
        "blogs/author/<int:author_id>/",
        BlogListByAuthorAPIView.as_view(),
        name="blog-list-by-author",
    ),
    path("blogs/<str:slug>/", BlogDetailsView.as_view(), name="blog.details"),
    path(
        "verify/<str:document_type>/<uuid:uuid>/",
        VerifyDocuments.as_view(),
        name="verifydocuments",
    ),
    path("our_technology/", OurTechnologyListView.as_view(), name="our.technology"),
    path("faq/", FAQListView.as_view(), name="faq"),
    path("our_clients/", OurClientsFeedbackList.as_view(), name="our.clients"),
    path(
        "our_achievement/", OurAchievementListView.as_view(), name=("our.achievement")
    ),
    path("our_growth/", OurGrowthListView.as_view(), name=("our.growth")),
    path("our_journey/", OurJourneyListView.as_view(), name=("our.journey")),
    path(
        "employee_perspective/",
        EmployeePerspectiveListView.as_view(),
        name=("employee.perspective"),
    ),
    path(
        "job_preference_request/",
        JobPreferenceRequestAPIView.as_view(),
        name="job_preference_request",
    ),
    path("leads/", LeadCreateAPIView.as_view(), name="lead-create"),
    path("client/logo/", ClientLogoListView.as_view(), name="client-logo-list"),
    path("gallery/", GalleryListView.as_view(), name="gallery"),
    path(
        "life-at-mediusware/",
        LifeAtMediuswareListView.as_view(),
        name="life-at-mediusware",
    ),
    path("awards/", AwardListView.as_view(), name="awards"),
    path("clients/", ClientListAPIView.as_view(), name="client-list"),
    path("page-banner/", PageBannerListAPIView.as_view(), name="page-banner"),
]

web_url = [path("", index)]

api_v2_urls = [
    path("hire-resource/", HireResourcePageListView.as_view(), name="hire_resource"),
    path("hire-resource/sitemap", HireResourcePageSitemapView.as_view(), name="hire_resource"),
    path(
        "hire-resource/<slug:slug>/",
        HireResourcePageDetailView.as_view(),
        name="hire_resource_detail",
    ),
    path(
        "woman-empowerment/", WomanEmpowermentView.as_view(), name="woman_empowerment"
    ),
    path("csr/", CSRListAPIView.as_view(), name="csr"),
    path("industry-serve/", IndustryServeListView.as_view(), name="industry-serve"),
    path("industry-serve/sitemap",  IndustryServeSitemapListView.as_view(), name="industry-serve"),
    path(
        "industry-serve/<slug:slug>/",
        IndustryServeDetailView.as_view(),
        name="industry-serve",
    ),
    path("projects/videos", ProjectVideoListAPIView.as_view(), name="project_video"),
    path(
        "video-testimonial/",
        VideoTestimonialListAPIView.as_view(),
        name="video_testimonial",
    ),
    path(
        "industry-we-serve/",
        IndustryWeServeListAPIView.as_view(),
        name="industry_we_serve",
    ),
    path("office-location/", OfficeLocationListView.as_view(), name="office_location"),
    path("post-credential/", PostCredentialCreateView.as_view(), name="post_credential"),
    path('brands_photo/', BrandListCreateAPIView.as_view(), name='brand-list-create'),
    path('website-title/', WebsiteTitleView.as_view(), name='website-title'),
    path("project/technologies/", ProjectTechnologyListAPIView.as_view(), name="project_technology"),
    path("client-review/", ClientReviewListAPIView.as_view(), name="client_review"),
    path("blog/preview/<slug:slug>/", PreviewBlogRetrieveAPIView.as_view(), name="blog_preview"),
    path("leadership/", LeadershipAPIView.as_view(), name="leadership"),
    path("employee-testimonial/", EmployeeTestimonialListAPIView.as_view(), name="employee_testimonial"),
    path("benefits/", BenefitsOfEmploymentListAPIView.as_view(), name="benefits"),
]


router = DefaultRouter()
router.register("contact", ContactModelViewSet)
router.register("inquiry", InquiryModelViewSet)
router.register("subscription", SubscriptionModelViewSet)

urlpatterns = [
    path("api/website/", include(api_urls + api_v2_urls)),
    path("website/", include(web_url)),
    path("plagiarism/webhook/", plagiarism_webhook, name="plagiarism_webhook"),
    path("plagiarism/webhook/export/", plagiarism_webhook_export, name="plagiarism_webhook_export"),
    path("export/<slug:scan_id>/<slug:export_id>/pdf-report/", export_pdf, name="pdf_export"),
    path("website/contact-form/", ContactFormView.as_view(), name="contact_form"),
    path("website/technology-navigation/", TechnologyNavigationView.as_view(), name="technology_navigation"),
]

urlpatterns = format_suffix_patterns(urlpatterns)

urlpatterns += [path("api/website/", include(router.urls)),]
