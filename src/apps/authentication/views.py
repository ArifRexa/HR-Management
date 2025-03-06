from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import decorators, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from apps.employeeapp.serializers import EmployeeSerializer
from apps.mixin.permission import ModelPermission
from apps.mixin.views import BaseModelViewSet

from .serializers import UserLoginSerializer, UserSerializer


class UserViewSet(BaseModelViewSet):
    queryset = User.objects.select_related("employee").prefetch_related(
        "employee__leave_set",
    )
    serializer_class = UserSerializer

    permission_classes = [permissions.IsAuthenticated, ModelPermission]
    serializers = {
        "login": UserLoginSerializer,
    }
    permissions = {
        "login": [permissions.AllowAny()],
    }

    @decorators.action(detail=False, methods=["POST"])
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )
        if not user:
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )
        refresh = RefreshToken.for_user(user)
        user_data = EmployeeSerializer(user.employee).data
        user_data["refresh"] = str(refresh)
        user_data["access"] = str(refresh.access_token)
        return Response(user_data, status=status.HTTP_200_OK)

    # user registration action
    @decorators.action(detail=False, methods=["POST"])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        user_data = EmployeeSerializer(user.employee).data
        user_data["refresh"] = str(refresh)
        user_data["access"] = str(refresh.access_token)
        return Response(user_data, status=status.HTTP_201_CREATED)
