from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns


from website.views import (
    ServiceList,
    ServiceDetails,
    ProjectList,
    ProjectDetails,
    EmployeeList,
    index,
    EmployeeDetails,
    CategoryListView,
    CategoryListViewWithBlogCount,
    TagListView,
    BlogListView,
    BlogDetailsView,
    VerifyDocuments,
    BlogCommentAPIView,
    BlogCommentDetailAPIView,
    BlogNextCommentDetailAPIView, DesignationListView, EmployeeWithDesignationView,
    AvailableTagsListView,
    ProjectHighlightedList,
    OurTechnologyListView,
    FAQListView,
    OurClientsFeedbackList,
    OurAchievementListView,
    OurGrowthListView,
    OurJourneyListView
    
)


api_urls = [
    path("services/", ServiceList.as_view(), name="service.list"),
    path("service/<str:slug>/", ServiceDetails.as_view(), name="service.details"),
    path("projects/", ProjectList.as_view(), name="project.list"),
    path("projects/available_tags/", AvailableTagsListView.as_view(), name="available.tags"),
    path("projects/available_tags/<str:tag_name>/", ProjectList.as_view(), name='project.list.by.tag'),
    path("projects/highlighted_projects/",ProjectHighlightedList.as_view(),name='projects.highlighted'),
    path("project/<str:slug>/", ProjectDetails.as_view(), name="project.details"),
    path("employees/", EmployeeList.as_view(), name="employee.list"),
    path("employee/<str:slug>/", EmployeeDetails.as_view(), name="employee.details"),
    path("employees/designations/", DesignationListView.as_view(), name="all-skills"),
    path('employees/designations/<str:designation>/', EmployeeWithDesignationView.as_view(), name='employee-skill-list'),
    # path("categories/", CategoryListView.as_view(), name="blog.category.list"),
    path(
        "categories/",
        CategoryListViewWithBlogCount.as_view(),
        name="blog.category.list",
    ),
    path("tags/", TagListView.as_view(), name="blog.tag.list"),
    path("blogs/", BlogListView.as_view(), name="blog.list"),
    path("blog/comments/", BlogCommentAPIView.as_view(), name="blog-comments"),
    path(
        "blog/comments/<int:pk>/",
        BlogCommentDetailAPIView.as_view(),
        name="blog-comment",
    ),
    path(
        "blog/next-comments/<int:blog_id>/<int:comment_parent_id>/",
        BlogNextCommentDetailAPIView.as_view(),
        name="blog-next-comment",
    ),
    path("blog/<str:slug>/", BlogDetailsView.as_view(), name="blog.details"),
    path(
        "verify/<str:document_type>/<uuid:uuid>/",
        VerifyDocuments.as_view(),
        name="verifydocuments",
    ),
    path("our_technology/",OurTechnologyListView.as_view(),name="our.technology"),
    path("faq/",FAQListView.as_view(),name="faq"),
    path("our_clients/",OurClientsFeedbackList.as_view(),name="our.clients"),
    path("our_achievement/",OurAchievementListView.as_view(),name=("our.achievement")),
    path("our_growth/",OurGrowthListView.as_view(),name=("our.growth")),
    path("our_journey/",OurJourneyListView.as_view(),name=("our.journey"))
]

web_url = [path("", index)]

urlpatterns = [
    path("api/website/", include(api_urls)),
    path("website/", include(web_url)),
]

urlpatterns = format_suffix_patterns(urlpatterns)
