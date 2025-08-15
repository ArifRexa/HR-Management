import json

import django_filters
from django.core.files.base import ContentFile
from django.db.models import Count, Q
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django_filters import FilterSet
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, status, viewsets
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from employee.models import Employee, EmployeeNOC, Skill
from project_management.models import (
    Client,
    OurTechnology,
    Project,
    ProjectTechnology,
    Tag,
    Technology,
)
from settings.models import Designation
from website.models import (
    FAQ,
    Award,
    BenefitsOfEmployment,
    Blog,
    BlogComment,
    BlogStatus,
    Brand,
    Category,
    Contact,
    EmployeePerspective,
    EmployeeTestimonial,
    Gallery,
    Industry,
    IndustryWeServe,
    Inquiry,
    Lead,
    Leadership,
    LifeAtMediusware,
    OfficeLocation,
    OurAchievement,
    OurGrowth,
    OurJourney,
    PageBanner,
    PlagiarismInfo,
    PostCredential,
    Service,
    Subscription,
    VideoTestimonial,
    WebsiteTitle,
)
from website.models_v2.industries_we_serve import ServeCategory
from website.models_v2.services import ServicePage
from website.serializers import (
    AvailableTagSerializer,
    AwardSerializer,
    BenefitsOfEmploymentSerializer,
    BlogCommentSerializer,
    BlogDetailsSerializer,
    BlogListSerializer,
    BlogSerializer,
    BlogSitemapSerializer,
    BrandSerializer,
    CategoryListSerializer,
    ClientLogoSerializer,
    ClientReviewSerializer,
    ClientSerializer,
    ContactFormSerializer,
    ContactSerializer,
    DesignationSetSerializer,
    EmployeeDetailsSerializer,
    EmployeeNOCSerializer,
    EmployeePerspectiveSerializer,
    EmployeeSerializer,
    EmployeeTestimonialSerializer,
    FAQSerializer,
    GallerySerializer,
    IndustrySerializer,
    IndustryWeServeSerializer,
    InquirySerializer,
    LeadershipSerializer,
    LeadSerializer,
    LifeAtMediuswareSerializer,
    NewTechnologySerializer,
    OfficeLocationSerializer,
    OurAchievementSerializer,
    OurClientsFeedbackSerializer,
    OurGrowthSerializer,
    OurJourneySerializer,
    OurTechnologySerializer,
    PageBannerSerializer,
    PostCredentialSerializer,
    ProjectDetailsSerializer,
    ProjectListSerializer,
    ProjectSerializer,
    ProjectSitemapSerializer,
    ServeCategorySerializer,
    ServiceDetailsSerializer,
    ServicePageSerializer,
    ServiceSerializer,
    SkillSerializer,
    SpecialProjectSerializer,
    SubscriptionSerializer,
    TagListSerializer,
    TechnologySerializer,
    VideoTestimonialSerializer,
    WebsiteTitleSerializer,
)
from website.utils.plagiarism_checker import CopyleaksAPI


def index(request):
    return render(request, "webdoc/index.html")


class CustomPagination(PageNumberPagination):
    page_size = 4
    page_size_query_param = "page_size"
    max_page_size = 100


class MostPopularBlogPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = "page_size"
    max_page_size = 100


class CustomPagination(PageNumberPagination):
    page_size = 4
    page_size_query_param = "page_size"
    max_page_size = 100


class MostPopularBlogPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = "page_size"
    max_page_size = 100


class ServiceList(APIView):
    def get(self, request, format=None):
        services = Service.objects.filter(active=True).order_by("order").all()
        serializer = ServiceSerializer(
            services, many=True, context={"request": request}
        )
        return Response(serializer.data)


class ServiceDetails(APIView):
    def get_object(self, slug):
        try:
            return Service.objects.filter(active=True).get(slug__exact=slug)
        except Service.DoesNotExist:
            raise Http404

    def get(self, request, slug, format=None):
        service = self.get_object(slug)
        serializer = ServiceDetailsSerializer(service, context={"request": request})
        return Response(serializer.data)


class CustomPagination(PageNumberPagination):
    page_size = 4
    page_size_query_param = "page_size"
    max_page_size = 100


class MostPopularBlogPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = "page_size"
    max_page_size = 100


class ProjectList(ListAPIView):
    queryset = Project.objects.filter(show_in_website=True).all()
    serializer_class = ProjectSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["tags", "is_highlighted"]
    search_fields = ["title"]
    ordering_fields = ["created_at", "modified_at"]

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response["Access-Control-Allow-Origin"] = "*"
        return response


class ProjectSitemapView(ListAPIView):
    queryset = Project.objects.filter(show_in_website=True).all()
    serializer_class = ProjectSitemapSerializer
    pagination_class = None


class ProjectVideoListAPIView(ListAPIView):
    queryset = Project.objects.filter(
        show_in_website=True, active=True, featured_video__isnull=False
    )
    serializer_class = ProjectListSerializer


class AvailableTagsListView(ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = AvailableTagSerializer


class ProjectDetails(APIView):
    def get_object(self, slug):
        try:
            return Project.objects.filter(show_in_website=True).get(slug__exact=slug)
        except Project.DoesNotExist:
            raise Http404

    def get(self, request, slug, format=None):
        project = self.get_object(slug)
        project_technologies = ProjectTechnology.objects.filter(project=project)
        serializer_context = {
            "request": request,
            "project_technologies": project_technologies,
        }
        serializer = ProjectDetailsSerializer(project, context=serializer_context)
        return Response(serializer.data)


class SpecialProjectListView(ListAPIView):
    queryset = Project.objects.filter(is_special=True, active=True)
    serializer_class = SpecialProjectSerializer


class EmployeeSkillFilter(FilterSet):
    skill = django_filters.CharFilter(
        field_name="employeeskill__skill__title", lookup_expr="exact"
    )

    class Meta:
        model = Employee
        fields = ["skill"]


class EmployeeList(ListAPIView):
    queryset = Employee.objects.filter(active=True, show_in_web=True).order_by(
        "joining_date",
    )
    serializer_class = EmployeeSerializer
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend]  # Should be a list
    filterset_class = EmployeeSkillFilter  # Use the filter class
    pagination_class.page_size = 6

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get("search")
        if search_query:
            queryset = queryset.filter(
                Q(full_name__icontains=search_query)
                | Q(designation__title__icontains=search_query)
            )
        return queryset


class EmployeeDetails(APIView):
    def get_object(self, slug):
        try:
            return Employee.objects.get(slug__exact=slug)
        except Employee.DoesNotExist:
            raise Http404

    def get(self, request, slug, format=None):
        employee = self.get_object(slug)
        serializer = EmployeeDetailsSerializer(employee, context={"request": request})
        return Response(serializer.data)


class MainEmployeeListView(ListAPIView):
    serializer_class = EmployeeSerializer

    def get_queryset(self):
        return Employee.objects.filter(
            active=True, show_in_web=True, operation=True
        ).order_by("list_order")


class DesignationListView(ListAPIView):
    queryset = Designation.objects.all()
    serializer_class = DesignationSetSerializer

    # def get(self,request,*args,**kwargs):


class SkillListView(ListAPIView):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    pagination_class = None


class EmployeeWithDesignationView(APIView):
    def get(self, request, *args, **kwargs):
        designation = self.kwargs.get(
            "designation"
        )  # Fetch the skill title from the URL kwargs
        employee_with_designation = Employee.objects.filter(
            designation__title=designation
        )

        serializer = EmployeeSerializer(employee_with_designation, many=True)
        total_count = len(employee_with_designation)
        return Response({"toal_count": total_count, "employee_list": serializer.data})


class CategoryListView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryListSerializer


class TagListView(ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagListSerializer


class CategoryListViewWithBlogCount(APIView):
    def get(self, request, *args, **kwargs):
        queryset = Category.objects.annotate(
            total_blog=Count(
                "categories",
                filter=Q(categories__status=BlogStatus.APPROVED)
                | Q(categories__status=BlogStatus.PUBLISHED),
            )
        ).values("id", "name", "slug", "total_blog")
        return Response(
            data=queryset,
            headers={"Access-Control-Allow-Origin": "*"},
        )


class BlogSitemapView(ListAPIView):
    q_obj = Q(status=BlogStatus.APPROVED) | Q(status=BlogStatus.PUBLISHED)
    queryset = Blog.objects.filter(q_obj).all()
    serializer_class = BlogSitemapSerializer
    pagination_class = None


class BlogListView(ListAPIView):
    q_obj = Q(status=BlogStatus.APPROVED) | Q(status=BlogStatus.PUBLISHED)
    queryset = Blog.objects.filter(q_obj).all()
    serializer_class = BlogListSerializer
    filter_backends = [
        django_filters.rest_framework.DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["category", "created_by__employee"]
    search_fields = ["title"]
    ordering_fields = ["created_at", "total_view"]

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response


class MostPopularBlogListView(ListAPIView):
    q_obj = Q(status=BlogStatus.APPROVED) | Q(status=BlogStatus.PUBLISHED)
    queryset = Blog.objects.filter(q_obj).order_by("-total_view")
    serializer_class = BlogListSerializer
    pagination_class = MostPopularBlogPagination


class FeaturedBlogListView(ListAPIView):
    q_obj = Q(status=BlogStatus.APPROVED) | Q(status=BlogStatus.PUBLISHED)
    queryset = Blog.objects.filter(q_obj, is_featured=True)
    serializer_class = BlogListSerializer
    pagination_class = CustomPagination


# class MostPopularBlogListView(ListAPIView):
#     queryset = Blog.objects.filter(status=BlogStatus.APPROVED).order_by("-total_view")
#     serializer_class = BlogListSerializer
#     pagination_class = MostPopularBlogPagination


# class FeaturedBlogListView(ListAPIView):
#     queryset = Blog.objects.filter(status=BlogStatus.APPROVED, is_featured=True)
#     serializer_class = BlogListSerializer
#     pagination_class = CustomPagination


# class MostPopularBlogListView(ListAPIView):
#     queryset = Blog.objects.filter(status=BlogStatus.APPROVED).order_by("-total_view")
#     serializer_class = BlogListSerializer
#     pagination_class = MostPopularBlogPagination


# class FeaturedBlogListView(ListAPIView):
#     queryset = Blog.objects.filter(status=BlogStatus.APPROVED, is_featured=True)
#     serializer_class = BlogListSerializer
#     pagination_class = CustomPagination


class BlogDetailsView(RetrieveAPIView):
    lookup_field = "slug"
    # q_obj = Q(status=BlogStatus.APPROVED) | Q(status=BlogStatus.PUBLISHED)
    queryset = Blog.objects.filter(
        Q(status=BlogStatus.APPROVED) | Q(status=BlogStatus.PUBLISHED)
    ).all()
    serializer_class = BlogDetailsSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]

    def retrieve(self, request, *args, **kwargs):
        blog = self.get_object()
        if blog.total_view is None:
            blog.total_view = 1
        else:
            blog.total_view += 1
        blog.save()
        response = super().retrieve(request, *args, **kwargs)
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response


class BlogCommentDeleteAPIView(APIView):
    def get(self, request, blog_id, comment_id):
        try:
            comment = get_object_or_404(BlogComment, id=comment_id, blog_id=blog_id)
            comment.delete()
            return Response(
                {"message": "Comment deleted successfully."},
                status=status.HTTP_204_NO_CONTENT,
            )
        except BlogComment.DoesNotExist:
            return Response(
                {"error": "Comment does not exist"}, status=status.HTTP_404_NOT_FOUND
            )


class BlogListByAuthorAPIView(ListAPIView):
    serializer_class = BlogListSerializer

    def get_queryset(self):
        q_obj = Q(status=BlogStatus.APPROVED) | Q(status=BlogStatus.PUBLISHED)
        author_id = self.kwargs.get("author_id")
        return Blog.objects.filter(q_obj, created_by__employee__id=author_id)


# class BlogCommentDeleteAPIView(APIView):
#     def get(self, request, blog_id, comment_id):
#         try:
#             comment = get_object_or_404(BlogComment, id=comment_id, blog_id=blog_id)
#             comment.delete()
#             return Response(
#                 {"message": "Comment deleted successfully."},
#                 status=status.HTTP_204_NO_CONTENT,
#             )
#         except BlogComment.DoesNotExist:
#             return Response(
#                 {"error": "Comment does not exist"}, status=status.HTTP_404_NOT_FOUND
#             )


# class BlogListByAuthorAPIView(ListAPIView):
#     serializer_class = BlogListSerializer

#     def get_queryset(self):
#         author_id = self.kwargs.get("author_id")
#         return Blog.objects.filter(created_by__employee__id=author_id, status=BlogStatus.APPROVED)


class VerifyDocuments(APIView):
    def get_noc(self, uuid):
        try:
            return EmployeeNOC.objects.get(uuid__exact=uuid)
        except EmployeeNOC.DoesNotExist:
            raise Http404

    def get(self, request, document_type, uuid, format=None):
        if document_type == "NOC":
            enoc = self.get_noc(uuid)
            serializer = EmployeeNOCSerializer(enoc, context={"request": request})
            return Response(serializer.data)

        raise Http404


class BlogCommentAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializers = BlogCommentSerializer(data=request.data)
        if serializers.is_valid():
            serializers.save()
            return Response(
                data=serializers.data,
                headers={"Access-Control-Allow-Origin": "*"},
                status=status.HTTP_200_OK,
            )

        return Response(
            data=serializers.errors,
            headers={"Access-Control-Allow-Origin": "*"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class BlogCommentDetailAPIView(APIView):
    pagination_class = CustomPagination

    def get(self, request, pk):
        parent_comments = BlogComment.objects.filter(blog=pk, parent=None)
        paginator = self.pagination_class()
        paginated_parent_comments = paginator.paginate_queryset(
            parent_comments, request
        )
        results = []

        for parent_comment in paginated_parent_comments:
            first_reply = parent_comment.children.first()
            data = {
                "id": parent_comment.id,
                "name": parent_comment.name,
                "email": parent_comment.email,
                "content": parent_comment.content,
                "blog": parent_comment.blog.id,
                "created_at": parent_comment.created_at,
                "updated_at": parent_comment.updated_at,
                "total_comment_reply": parent_comment.children.count(),
                "first_reply": (
                    {
                        "id": first_reply.id if first_reply else None,
                        "name": first_reply.name if first_reply else None,
                        "email": first_reply.email if first_reply else None,
                        "content": first_reply.content if first_reply else None,
                        "created_at": first_reply.created_at if first_reply else None,
                        "updated_at": first_reply.updated_at if first_reply else None,
                    }
                    if first_reply
                    else None
                ),
            }
            results.append(data)

        return paginator.get_paginated_response({"results": results})


# class BlogCommentDeleteAPIView(APIView):
#     def get(self, request, blog_id, comment_id):
#         try:
#             comment = get_object_or_404(BlogComment, id=comment_id, blog_id=blog_id)
#             comment.delete()
#             return Response(
#                 {"message": "Comment deleted successfully."},
#                 status=status.HTTP_204_NO_CONTENT,
#             )
#         except BlogComment.DoesNotExist:
#             return Response(
#                 {"error": "Comment does not exist"}, status=status.HTTP_404_NOT_FOUND
#             )


class BlogNextCommentDetailAPIView(APIView):
    pagination_class = CustomPagination

    def get(self, request, blog_id, comment_parent_id):
        comments = BlogComment.objects.filter(
            blog=blog_id, parent__id=comment_parent_id
        )
        comments_annotated = comments.annotate(
            next_total_comment_reply=Count("children")
        )

        paginator = self.pagination_class()
        paginated_comments = paginator.paginate_queryset(
            comments_annotated.values_list("id", flat=True), request
        )

        comment_ids = [comment_id for comment_id in paginated_comments]

        query = comments_annotated.filter(id__in=comment_ids).values(
            "id",
            "name",
            "email",
            "content",
            "blog",
            "created_at",
            "updated_at",
        )

        return paginator.get_paginated_response(query)


# class BlogListByAuthorAPIView(ListAPIView):
#     serializer_class = BlogListSerializer

#     def get_queryset(self):
#         author_id = self.kwargs.get("author_id")
#         return Blog.objects.filter(created_by__employee__id=author_id, status=BlogStatus.APPROVED).order_by(
#             "-total_view"
#         )


class OurTechnologyListView(ListAPIView):
    queryset = OurTechnology.objects.all()
    serializer_class = OurTechnologySerializer


class FAQListView(ListAPIView):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer


class OurClientsFeedbackList(ListAPIView):
    queryset = Client.objects.filter(project__isnull=False).distinct()
    serializer_class = OurClientsFeedbackSerializer


class OurAchievementListView(ListAPIView):
    queryset = OurAchievement.objects.all()
    serializer_class = OurAchievementSerializer


class OurGrowthListView(ListAPIView):
    queryset = OurGrowth.objects.all()
    serializer_class = OurGrowthSerializer


class OurJourneyListView(ListAPIView):
    queryset = OurJourney.objects.all()
    serializer_class = OurJourneySerializer


class EmployeePerspectiveListView(ListAPIView):
    queryset = EmployeePerspective.objects.all()
    serializer_class = EmployeePerspectiveSerializer


class IndustryListView(ListAPIView):
    queryset = Industry.objects.all()
    serializer_class = IndustrySerializer


class LeadCreateAPIView(CreateAPIView):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer


class ClientLogoListView(APIView):
    serializer_class = ClientLogoSerializer

    def get(self, request, *args, **kwargs):
        queryset = Client.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        logos = [
            request.build_absolute_uri(logo["logo"])
            for logo in serializer.data
            if logo["logo"]
        ]
        return Response({"results": logos})


class GalleryListView(APIView):
    serializer_class = GallerySerializer

    def get(self, request, *args, **kwargs):
        queryset = Gallery.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        images = [
            request.build_absolute_uri(image["image"]) for image in serializer.data
        ]
        return Response({"results": images})


class LifeAtMediuswareListView(APIView):
    serializer_class = LifeAtMediuswareSerializer

    def get(self, request, *args, **kwargs):
        queryset = LifeAtMediusware.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        images = [
            request.build_absolute_uri(image["image"]) for image in serializer.data
        ]
        return Response({"results": images})


class AwardListView(ListAPIView):
    queryset = Award.objects.all()
    serializer_class = AwardSerializer

    # def get(self, request, *args, **kwargs):
    #     queryset = Award.objects.all()
    #     serializer = self.serializer_class(queryset, many=True)
    #     images = [request.build_absolute_uri(image['image']) for image in serializer.data]
    #     return Response({"results": images})


class ClientListAPIView(ListAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


class VideoTestimonialListAPIView(ListAPIView):
    queryset = VideoTestimonial.objects.all()
    serializer_class = VideoTestimonialSerializer


class IndustryWeServeListAPIView(ListAPIView):
    queryset = IndustryWeServe.objects.all()
    serializer_class = IndustryWeServeSerializer


class OfficeLocationListView(ListAPIView):
    queryset = OfficeLocation.objects.all()
    serializer_class = OfficeLocationSerializer
    pagination_class = None


class PostCredentialCreateView(APIView):
    queryset = PostCredential.objects.all()
    serializer_class = PostCredentialSerializer
    permission_classes = ()
    authentication_classes = ()

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        obj, created = PostCredential.objects.get_or_create(
            platform=data.get("platform"),
            defaults={
                "token": data.get("token"),
                "name": data.get("name"),
            },
        )
        if not created:
            obj.token = data.get("token")
            obj.name = data.get("name")
            obj.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class BrandListCreateAPIView(ListAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    pagination_class = None


class WebsiteTitleView(RetrieveAPIView):
    queryset = WebsiteTitle.objects.all()
    serializer_class = WebsiteTitleSerializer

    def get_object(self):
        return self.queryset.first()

    # def get(self, request, *args, **kwargs):
    #     try:
    #         # Assuming there's only one WebsiteTitle object
    #         website_title = WebsiteTitle.objects.first()  # Adjust query as needed
    #         if website_title is None:
    #             return JsonResponse(
    #                 {"error": "No WebsiteTitle object found"}, status=404
    #             )

    #         serializer = WebsiteTitleSerializer(website_title)
    #         return JsonResponse(
    #             serializer.data, safe=False, json_dumps_params={"indent": 2}
    #         )

    #     except Exception as e:
    #         return JsonResponse({"error": str(e)}, status=500)


class PageBannerListAPIView(RetrieveAPIView):
    queryset = PageBanner.objects.all()
    serializer_class = PageBannerSerializer
    pagination_class = None

    def get_object(self):
        return PageBanner.objects.first()


class ProjectTechnologyListAPIView(APIView):
    # queryset = ProjectTechnology.objects.all()
    # serializer_class = ProjectTechnologyCountSerializer
    # pagination_class = None

    def get(self, request, *args, **kwargs):
        qs = Technology.objects.annotate(
            project_count=Count("projecttechnology__project")
        ).values("name", "project_count")
        # serializer = ProjectTechnologyCountSerializer(data=qs, many=True)
        # serializer.is_valid(raise_exception=True)
        # print(serializer.validated_data)
        return Response(qs)


class ClientReviewListAPIView(ListAPIView):
    queryset = Project.objects.filter(show_in_website=True)
    serializer_class = ClientReviewSerializer
    pagination_class = None


class PreviewBlogRetrieveAPIView(RetrieveAPIView):
    queryset = Blog.objects.all()
    serializer_class = BlogDetailsSerializer
    lookup_field = "slug"

    # def get(self, request, *args, **kwargs):
    #     response = super().get(request, *args, **kwargs)
    #     response.headers["Access-Control-Allow-Origin"] = "*"
    #     return response


class LeadershipAPIView(RetrieveAPIView):
    queryset = Leadership.objects.all()
    serializer_class = LeadershipSerializer

    def get_object(self):
        return self.queryset.first()


class EmployeeTestimonialListAPIView(ListAPIView):
    queryset = EmployeeTestimonial.objects.all()
    serializer_class = EmployeeTestimonialSerializer
    pagination_class = None


class BenefitsOfEmploymentListAPIView(ListAPIView):
    queryset = BenefitsOfEmployment.objects.all()
    serializer_class = BenefitsOfEmploymentSerializer
    pagination_class = None


# These are the webhook that handle copyleaks request and process the data
# Plagiarism webhook receiving
@csrf_exempt
def plagiarism_webhook(request):
    if request.method == "POST":
        try:
            # Parse the incoming JSON data
            data = json.loads(request.body)
            print("webhook data")

            # Extract relevant fields from the payload
            scan_id = data.get("scannedDocument", {}).get("scanId")
            results = data.get("results", {})
            aggregatedScore = results.get("score", {}).get("aggregatedScore")
            plagiarism_object = PlagiarismInfo.objects.get(scan_id=scan_id)
            if plagiarism_object:
                plagiarism_object.plagiarism_percentage = aggregatedScore
                host_url = request.build_absolute_uri("/")
                copyleaks_object = CopyleaksAPI(callback_host=host_url)
                copyleaks_object.call_for_export(
                    scan_id=scan_id, export_id=plagiarism_object.export_id
                )
                plagiarism_object.save()

            # For demonstration, we'll print some information
            print(f"Scan ID: {scan_id}")
            print(f"Status: {status}")
            print(f"aggregatedScore: {aggregatedScore}")

            # Handle any status or alert-specific actions
            if status == 0:  # Success
                print("Plagiarism scan completed successfully.")
                # You can perform further actions like saving to DB or notifying the user

            # Return a success response to Copyleaks
            return JsonResponse(
                {"message": "Webhook received successfully"}, status=200
            )

        except Exception as e:
            print(f"Error processing webhook: {e}")
            return JsonResponse({"error": "Error processing the webhook"}, status=400)

    # If it's not a POST request, return a 405 Method Not Allowed response
    return JsonResponse({"error": "Invalid request method"}, status=405)


@csrf_exempt
def export_pdf(request, scan_id, export_id):
    if request.method == "POST":
        # Log the content type to determine how to handle the body
        content_type = request.content_type
        print(f"Content-Type: {content_type}")

        # Log the raw request body for debugging
        raw_body = request.body
        # print("Raw request body (binary data):", raw_body)

        if content_type == "application/pdf":
            # Fetch the plagiarism object based on scan_id and export_id
            try:
                plagiarism_object = PlagiarismInfo.objects.get(
                    scan_id=scan_id, export_id=export_id
                )
            except PlagiarismInfo.DoesNotExist:
                return JsonResponse(
                    {"error": "Plagiarism record not found"}, status=404
                )

            # Save the PDF file to the model's pdf_file field
            # Create a ContentFile from the raw body
            pdf_file = ContentFile(
                raw_body, name=f"plagiarism_report_{scan_id}_{export_id}.pdf"
            )

            # Assign the file to the pdf_file field and save the model
            plagiarism_object.pdf_file.save(
                f"plagiarism_report_{scan_id}_{export_id}.pdf", pdf_file
            )

            print("Received a PDF file.")
            return JsonResponse(
                {"message": "PDF file received and saved successfully"}, status=200
            )
        else:
            return JsonResponse({"error": "Unsupported content type"}, status=415)

    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)


@csrf_exempt
def plagiarism_webhook_export(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            print("webhook data for complete export")
            return JsonResponse(
                {"message": "Webhook received successfully"}, status=200
            )
        except Exception as e:
            print(f"Error processing webhook: {e}")
            return JsonResponse({"error": "Error processing webhook"}, status=400)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)



class ContactModelViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    
class InquiryModelViewSet(viewsets.ModelViewSet):
    queryset = Inquiry.objects.all()
    serializer_class = InquirySerializer
    
class SubscriptionModelViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer


class ContactFormView(APIView):
    serializer_class = ContactFormSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=ContactFormSerializer,
        tags=["Contact"],
        operation_description="Create a new contact form entry"
    )
    def post(self, request):
        serializer = ContactFormSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


# class TechnologyNavigationView(APIView):
class TechnologyNavigationView(APIView):
    permission_classes = [AllowAny]
    serializer_class = NewTechnologySerializer
    def get(self, request):
        from website.models import Technology
        technologies = Technology.objects.filter(show_in_menu=True).values('name', 'slug')
        return Response(technologies, status=status.HTTP_200_OK)
    




# class BlogFilter(django_filters.FilterSet):
#     services = django_filters.BooleanFilter(
#         method='filter_has_services',
#         label='Has Parent Services'
#     )
#     industry = django_filters.BooleanFilter(
#         method='filter_has_industry',
#         label='Has Industry Details'
#     )
#     technology = django_filters.BooleanFilter(
#         method='filter_has_technology',
#         label='Has Technology'
#     )

#     def filter_has_services(self, queryset, name, value):
#         if value:
#             return queryset.filter(parent_services__isnull=False).distinct()
#         return queryset

#     def filter_has_industry(self, queryset, name, value):
#         if value:
#             return queryset.filter(industry_details__isnull=False).distinct()
#         return queryset

#     def filter_has_technology(self, queryset, name, value):
#         if value:
#             return queryset.filter(technology__isnull=False).distinct()
#         return queryset

#     class Meta:
#         model = Blog
#         fields = ['services', 'industry', 'technology']


# class BlogListAPIView(ListAPIView):
#     queryset = Blog.objects.all().order_by('-created_at')
#     serializer_class = BlogSerializer
#     filterset_class = BlogFilter
#     filter_backends = [DjangoFilterBackend, filters.SearchFilter]
#     search_fields = ['category__name']  # Search only on category (verbose name: tags)

#     @swagger_auto_schema(
#             tags=
#             ["Blog List"],
#         manual_parameters=[
#             openapi.Parameter(
#                 'services',
#                 openapi.IN_QUERY,
#                 description="Filter blogs that have at least one parent service (true/false)",
#                 type=openapi.TYPE_BOOLEAN
#             ),
#             openapi.Parameter(
#                 'industry',
#                 openapi.IN_QUERY,
#                 description="Filter blogs that have at least one industry detail (true/false)",
#                 type=openapi.TYPE_BOOLEAN
#             ),
#             openapi.Parameter(
#                 'technology',
#                 openapi.IN_QUERY,
#                 description="Filter blogs that have at least one technology (true/false)",
#                 type=openapi.TYPE_BOOLEAN
#             ),
#             openapi.Parameter(
#                 'search',
#                 openapi.IN_QUERY,
#                 description="Search across category name (verbose name: tags)",
#                 type=openapi.TYPE_STRING
#             ),
#         ],
#         responses={
#             200: BlogSerializer(many=True),
#             400: 'Bad Request'
#         }
#     )
#     def get(self, request, *args, **kwargs):
#         return super().get(request, *args, **kwargs)





# testing news

class BlogPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100



class BlogFilter(django_filters.FilterSet):
    services = django_filters.BooleanFilter(
        method='filter_has_services',
        label='Has Parent Services'
    )
    industry = django_filters.BooleanFilter(
        method='filter_has_industry',
        label='Has Industry Details'
    )
    technology = django_filters.BooleanFilter(
        method='filter_has_technology',
        label='Has Technology'
    )
    # Updated filters for comma-separated IDs
    service_ids = django_filters.CharFilter(
        method='filter_by_service_ids',
        label='Filter by specific service IDs (comma separated)'
    )
    industry_ids = django_filters.CharFilter(
        method='filter_by_industry_ids',
        label='Filter by specific industry IDs (comma separated)'
    )
    technology_ids = django_filters.CharFilter(
        method='filter_by_technology_ids',
        label='Filter by specific technology IDs (comma separated)'
    )

    def filter_has_services(self, queryset, name, value):
        if value:
            return queryset.filter(parent_services__isnull=False).distinct()
        return queryset

    def filter_has_industry(self, queryset, name, value):
        if value:
            return queryset.filter(industry_details__isnull=False).distinct()
        return queryset

    def filter_has_technology(self, queryset, name, value):
        if value:
            return queryset.filter(technology__isnull=False).distinct()
        return queryset

    def filter_by_service_ids(self, queryset, name, value):
        if value:
            try:
                ids = [int(i.strip()) for i in value.split(',') if i.strip()]
                return queryset.filter(parent_services__id__in=ids).distinct()
            except ValueError:
                return queryset.none()
        return queryset

    def filter_by_industry_ids(self, queryset, name, value):
        if value:
            try:
                ids = [int(i.strip()) for i in value.split(',') if i.strip()]
                return queryset.filter(industry_details__id__in=ids).distinct()
            except ValueError:
                return queryset.none()
        return queryset

    def filter_by_technology_ids(self, queryset, name, value):
        if value:
            try:
                ids = [int(i.strip()) for i in value.split(',') if i.strip()]
                return queryset.filter(technology__id__in=ids).distinct()
            except ValueError:
                return queryset.none()
        return queryset

    class Meta:
        model = Blog
        fields = ['services', 'industry', 'technology', 'service_ids', 'industry_ids', 'technology_ids']


class BlogListAPIView(ListAPIView):
    queryset = Blog.objects.all().order_by('-created_at')
    serializer_class = BlogSerializer
    filterset_class = BlogFilter
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['category__name']
    pagination_class = BlogPagination
    
    @swagger_auto_schema(
        tags=["Blog List"],
        manual_parameters=[
            openapi.Parameter(
                'services',
                openapi.IN_QUERY,
                description="Filter blogs that have at least one parent service and include all parent services in response (true/false)",
                type=openapi.TYPE_BOOLEAN
            ),
            openapi.Parameter(
                'industry',
                openapi.IN_QUERY,
                description="Filter blogs that have at least one industry detail and include all industry details in response (true/false)",
                type=openapi.TYPE_BOOLEAN
            ),
            openapi.Parameter(
                'technology',
                openapi.IN_QUERY,
                description="Filter blogs that have at least one technology and include all technologies in response (true/false)",
                type=openapi.TYPE_BOOLEAN
            ),
            openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                description="Search across category name (verbose name: tags)",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'page',
                openapi.IN_QUERY,
                description="Page number for pagination",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'page_size',
                openapi.IN_QUERY,
                description="Number of items per page",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'service_ids',
                openapi.IN_QUERY,
                description="Filter blogs by specific service IDs (comma separated)",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'industry_ids',
                openapi.IN_QUERY,
                description="Filter blogs by specific industry IDs (comma separated)",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'technology_ids',
                openapi.IN_QUERY,
                description="Filter blogs by specific technology IDs (comma separated)",
                type=openapi.TYPE_STRING
            ),
        ],
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'count': openapi.Schema(
                        type=openapi.TYPE_INTEGER,
                        description='Total number of blogs'
                    ),
                    'next': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='URL for next page'
                    ),
                    'previous': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='URL for previous page'
                    ),
                    'services': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            ref='#/definitions/website_servicepage'
                        ),
                        description='List of all parent services when services=true'
                    ),
                    'industry': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            ref='#/definitions/website_servecategory'
                        ),
                        description='List of all industry details when industry=true'
                    ),
                    'technology': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            ref='#/definitions/website_technology'
                        ),
                        description='List of all technologies when technology=true'
                    ),
                    'results': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            ref='#/definitions/website_blog'
                        ),
                        description='List of filtered blogs for current page'
                    ),
                }
            ),
            400: 'Bad Request'
        }
    )
    def get(self, request, *args, **kwargs):
        # Apply filters
        filterset = self.filterset_class(request.GET, queryset=self.get_queryset())
        if not filterset.is_valid():
            return Response(filterset.errors, status=400)
        queryset = filterset.qs
        
        # Apply search
        queryset = self.filter_queryset(queryset)
        
        # Paginate the queryset
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_data = self.get_paginated_response(serializer.data).data
        else:
            serializer = self.get_serializer(queryset, many=True)
            paginated_data = {
                'count': queryset.count(),
                'next': None,
                'previous': None,
                'results': serializer.data
            }
        
        # Prepare response with additional data
        response_data = paginated_data.copy()
        
        # Include all parent services if services=true
        if request.GET.get('services') == 'true':
            services = ServicePage.objects.filter(is_parent=True)
            response_data['services'] = ServicePageSerializer(services, many=True).data
        
        # Include all industry details if industry=true
        if request.GET.get('industry') == 'true':
            industries = ServeCategory.objects.all()
            response_data['industry'] = ServeCategorySerializer(industries, many=True).data
        
        # Include all technologies if technology=true
        from website.models import Technology
        if request.GET.get('technology') == 'true':
            technologies = Technology.objects.all()
            response_data['technology'] = TechnologySerializer(technologies, many=True).data
        
        return Response(response_data)
    
    


    





# class ServeCategoryAPIView(APIView):
#     @swagger_auto_schema(
#         tags=["Industry Details"],
#         operation_description="Retrieve serve categories or a specific category by slug",
#         manual_parameters=[
#             openapi.Parameter(
#                 'slug',
#                 openapi.IN_PATH,
#                 type=openapi.TYPE_STRING,
#                 description='Slug of the category to retrieve',
#                 # required=False
#             ),
#         ],
#         responses={
#             200: ServeCategorySerializer(many=True),
#             404: "Category not found",
#         },
#     )
#     def get(self, request, slug=None):
#         try:
#             if slug:
#                 # Use correct related names for prefetch_related
#                 category = ServeCategory.objects.prefetch_related(
#                     'our_process', 'industry_details_heading', 'custom_solutions',
#                     'benefits', 'why_choose_us', 'ctas', 'faqs', 'application_areas', 'industries'
#                 ).select_related('faq_schema').get(slug=slug)
#                 serializer = ServeCategorySerializer(category, context={'request': request})
#                 return Response(serializer.data)
#             else:
#                 # Use correct related names for prefetch_related
#                 categories = ServeCategory.objects.prefetch_related(
#                     'our_process', 'industry_details_heading', 'custom_solutions',
#                     'benefits', 'why_choose_us', 'ctas', 'faqs', 'application_areas', 'industries'
#                 ).select_related('faq_schema').all()
                
#                 serializer = ServeCategorySerializer(categories, many=True, context={'request': request})
#                 return Response(serializer.data)
#         except Exception as e:
#             return Response(
#                 {"error": str(e)}, 
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )

class ServeCategoryAPIView(APIView):
    @swagger_auto_schema(
        tags=["Industry Details"],
        operation_description="Retrieve serve categories or a specific category by slug",
        manual_parameters=[
            openapi.Parameter(
                'slug',
                openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                description='Slug of the category to retrieve',
            ),
        ],
        responses={
            200: ServeCategorySerializer(many=True),
            404: "Category not found",
        },
    )
    def get(self, request, slug=None):
        try:
            if slug:
                # Include all related fields in prefetch_related
                category = ServeCategory.objects.prefetch_related(
                    'industry_details_hero_section', 'our_process', 'industry_details_heading',
                    'industry_details_heading__industry_details_sub_heading',
                    'custom_solutions', 'custom_solutions__custom_solutions_cards',
                    'benefits', 'benefits__benefits_cards',
                    'why_choose_us', 'why_choose_us__why_choose_us_cards',
                    'ctas', 'faqs', 'application_areas', 'industries'
                ).select_related('faq_schema').get(slug=slug)
                serializer = ServeCategorySerializer(category, context={'request': request})
                return Response(serializer.data)
            else:
                # Include all related fields in prefetch_related
                categories = ServeCategory.objects.prefetch_related(
                    'industry_details_hero_section', 'our_process', 'industry_details_heading',
                    'industry_details_heading__industry_details_sub_heading',
                    'custom_solutions', 'custom_solutions__custom_solutions_cards',
                    'benefits', 'benefits__benefits_cards',
                    'why_choose_us', 'why_choose_us__why_choose_us_cards',
                    'ctas', 'faqs', 'application_areas', 'industries'
                ).select_related('faq_schema').all()
                
                serializer = ServeCategorySerializer(categories, many=True, context={'request': request})
                return Response(serializer.data)
        except ServeCategory.DoesNotExist:
            return Response(
                {"error": "Category not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )