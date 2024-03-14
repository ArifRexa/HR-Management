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
    BlogNextCommentDetailAPIView, SkillListView, EmployeeSkillListView,
)


api_urls = [
    path("services/", ServiceList.as_view(), name="service.list"),
    path("service/<str:slug>/", ServiceDetails.as_view(), name="service.details"),
    path("projects/", ProjectList.as_view(), name="project.list"),
    path("project/<str:slug>/", ProjectDetails.as_view(), name="project.details"),
    path("employees/", EmployeeList.as_view(), name="employee.list"),
    path("employee/<str:slug>/", EmployeeDetails.as_view(), name="employee.details"),
    path("skills/", SkillListView.as_view(), name="all-skills"),
    path('employees/<str:skill>/', EmployeeSkillListView.as_view(), name='employee-skill-list'),
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
]

web_url = [path("", index)]

urlpatterns = [
    path("api/website/", include(api_urls)),
    path("website/", include(web_url)),
]

urlpatterns = format_suffix_patterns(urlpatterns)
