import django_filters
from django.http import Http404
from django.shortcuts import render
from django.db.models import Count, Q, F
from icecream import ic


from django.shortcuts import get_object_or_404


from django_filters import FilterSet 
from rest_framework.pagination import LimitOffsetPagination
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import filters, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.pagination import PageNumberPagination
from employee.models import Employee, EmployeeNOC
from project_management.models import Project,ProjectTechnology

from employee.models import Employee, EmployeeNOC, Skill, EmployeeSkill
from settings.models import Designation
from project_management.models import Project,Tag,OurTechnology,Client
from website.models import Award, Gallery, Service, Category, Blog, BlogComment,FAQ,OurAchievement,OurJourney,OurGrowth,EmployeePerspective,Industry,Lead
from website.serializers import (
    AwardSerializer,
    ClientLogoSerializer,
    GallerySerializer,
    ServiceSerializer,
    ProjectSerializer,
    EmployeeSerializer,
    ServiceDetailsSerializer,
    ProjectDetailsSerializer,
    EmployeeDetailsSerializer,
    CategoryListSerializer,
    TagListSerializer,
    BlogListSerializer,
    BlogDetailsSerializer,
    EmployeeNOCSerializer,
    BlogCommentSerializer, DesignationSetSerializer,
    AvailableTagSerializer,
    ProjectHighlightedSerializer,
    OurTechnologySerializer,
    FAQSerializer,
    OurClientsFeedbackSerializer,
    OurAchievementSerializer,
    OurJourneySerializer,
    OurGrowthSerializer,
    EmployeePerspectiveSerializer,
    IndustrySerializer,
    SkillSerializer,
    LeadSerializer
)
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView
from django_filters.rest_framework import DjangoFilterBackend
def index(request):
    return render(request, "webdoc/index.html")


class CustomPagination(PageNumberPagination):
    page_size = 4
    page_size_query_param = 'page_size'
    max_page_size = 100


class MostPopularBlogPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 100

class CustomPagination(PageNumberPagination):
    page_size = 4
    page_size_query_param = 'page_size'
    max_page_size = 100


class MostPopularBlogPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'page_size'
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
    page_size_query_param = 'page_size'
    max_page_size = 100


class MostPopularBlogPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'page_size'
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
        serializer_context = {"request": request, "project_technologies": project_technologies}
        serializer = ProjectDetailsSerializer(project, context=serializer_context)
        return Response(serializer.data)



class EmployeeSkillFilter(FilterSet):
    skill = django_filters.CharFilter(field_name='employeeskill__skill__title', lookup_expr='exact')

    class Meta:
        model = Employee
        fields = ['skill']

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
        search_query = self.request.query_params.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(full_name__icontains=search_query) |
                Q(designation__title__icontains=search_query)
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
        return Employee.objects.filter(active=True, show_in_web=True,operation=True).order_by(
                "list_order"
            )
    
    
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
        designation = self.kwargs.get('designation')  # Fetch the skill title from the URL kwargs
        employee_with_designation = Employee.objects.filter(designation__title=designation)
        
        serializer = EmployeeSerializer(employee_with_designation, many=True)
        total_count = len(employee_with_designation)
        return Response({'toal_count': total_count, 'employee_list': serializer.data})


class CategoryListView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryListSerializer


class TagListView(ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagListSerializer


class CategoryListViewWithBlogCount(APIView):
    def get(self, request, *args, **kwargs):
        queryset = Category.objects.annotate(
            total_blog=Count("categories", filter=Q(categories__active=True))
        ).values("id", "name", "slug", "total_blog")
        return Response(
            data=queryset,
            headers={"Access-Control-Allow-Origin": "*"},
        )


class BlogListView(ListAPIView):
    queryset = Blog.objects.filter(active=True).all()
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
    queryset = Blog.objects.filter(active=True).order_by('-total_view')
    serializer_class = BlogListSerializer
    pagination_class = MostPopularBlogPagination

class FeaturedBlogListView(ListAPIView):
    queryset = Blog.objects.filter(active=True, is_featured=True)
    serializer_class = BlogListSerializer
    pagination_class = CustomPagination

class MostPopularBlogListView(ListAPIView):
    queryset = Blog.objects.filter(active=True).order_by('-total_view')
    serializer_class = BlogListSerializer
    pagination_class = MostPopularBlogPagination


class FeaturedBlogListView(ListAPIView):
    queryset = Blog.objects.filter(active=True, is_featured=True)
    serializer_class = BlogListSerializer
    pagination_class = CustomPagination    

class MostPopularBlogListView(ListAPIView):
    queryset = Blog.objects.filter(active=True).order_by('-total_view')
    serializer_class = BlogListSerializer
    pagination_class = MostPopularBlogPagination


class FeaturedBlogListView(ListAPIView):
    queryset = Blog.objects.filter(active=True, is_featured=True)
    serializer_class = BlogListSerializer
    pagination_class = CustomPagination    

class BlogDetailsView(RetrieveAPIView):
    lookup_field = "slug"
    queryset = Blog.objects.filter(active=True).all()
    serializer_class = BlogDetailsSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]

    def retrieve(self, request, *args, **kwargs):
        blog = self.get_object()
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
                return Response({"message": "Comment deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
            except BlogComment.DoesNotExist:
                return Response({"error": "Comment does not exist"}, status=status.HTTP_404_NOT_FOUND)

class BlogListByAuthorAPIView(ListAPIView):
    serializer_class = BlogListSerializer

    def get_queryset(self):
        author_id = self.kwargs.get('author_id')
        return Blog.objects.filter(created_by__employee__id=author_id)


class BlogCommentDeleteAPIView(APIView):
   def get(self, request, blog_id, comment_id):
            try:
                comment = get_object_or_404(BlogComment, id=comment_id, blog_id=blog_id)
                comment.delete()
                return Response({"message": "Comment deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
            except BlogComment.DoesNotExist:
                return Response({"error": "Comment does not exist"}, status=status.HTTP_404_NOT_FOUND)

class BlogListByAuthorAPIView(ListAPIView):
    serializer_class = BlogListSerializer

    def get_queryset(self):
        author_id = self.kwargs.get('author_id')
        return Blog.objects.filter(created_by__employee__id=author_id)



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
        paginated_parent_comments = paginator.paginate_queryset(parent_comments, request)
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
                "first_reply": {
                    "id": first_reply.id if first_reply else None,
                    "name": first_reply.name if first_reply else None,
                    "email": first_reply.email if first_reply else None,
                    "content": first_reply.content if first_reply else None,
                    "created_at": first_reply.created_at if first_reply else None,
                    "updated_at": first_reply.updated_at if first_reply else None,
                } if first_reply else None
            }
            results.append(data)

        return paginator.get_paginated_response({"results": results})
    

class BlogCommentDeleteAPIView(APIView):
   def get(self, request, blog_id, comment_id):
            try:
                comment = get_object_or_404(BlogComment, id=comment_id, blog_id=blog_id)
                comment.delete()
                return Response({"message": "Comment deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
            except BlogComment.DoesNotExist:
                return Response({"error": "Comment does not exist"}, status=status.HTTP_404_NOT_FOUND)

class BlogNextCommentDetailAPIView(APIView):
    pagination_class = CustomPagination

    def get(self, request, blog_id, comment_parent_id):
        comments = BlogComment.objects.filter(blog=blog_id, parent__id=comment_parent_id)
        comments_annotated = comments.annotate(next_total_comment_reply=Count("children"))
        
        paginator = self.pagination_class()
        paginated_comments = paginator.paginate_queryset(comments_annotated.values_list('id', flat=True), request)
        
        comment_ids = [comment_id for comment_id in paginated_comments]
        
        query = (
            comments_annotated
            .filter(id__in=comment_ids)
            .values(
                "id",
                "name",
                "email",
                "content",
                "blog",
                "created_at",
                "updated_at",
            )
        )
        
        return paginator.get_paginated_response(query)
    
class BlogListByAuthorAPIView(ListAPIView):
    serializer_class = BlogListSerializer

    def get_queryset(self):
        author_id = self.kwargs.get('author_id')
        return Blog.objects.filter(created_by__employee__id=author_id).order_by('-total_view')

class OurTechnologyListView(ListAPIView):
    queryset = OurTechnology.objects.all()
    serializer_class = OurTechnologySerializer


class FAQListView(ListAPIView):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer


class OurClientsFeedbackList(ListAPIView):
    queryset = Project.objects.filter(client__isnull=False)
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
        logos = [request.build_absolute_uri(logo['logo']) for logo in serializer.data]
        return Response({"results": logos})
    
    
class GalleryListView(APIView):
    serializer_class = GallerySerializer
    
    def get(self, request, *args, **kwargs):
        queryset = Gallery.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        images = [request.build_absolute_uri(image['image']) for image in serializer.data]
        return Response({"results": images})
    

class AwardListView(APIView):
    serializer_class = AwardSerializer
    
    def get(self, request, *args, **kwargs):
        queryset = Award.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        images = [request.build_absolute_uri(image['image']) for image in serializer.data]
        return Response({"results": images})
    
