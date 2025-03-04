
from rest_framework import viewsets, permissions, decorators, status

from rest_framework.response import Response

from .serializers import UserSerializer, UserLoginSerializer

from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate




class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.select_related("employee").prefetch_related(
        "employee__leave_set",
    )
    serializer_class = UserSerializer

    permission_classes = [permissions.IsAuthenticated]


    def get_permissions(self):
        if self.action in ["login"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == "login":
            return UserLoginSerializer
        return UserSerializer

    @decorators.action(detail=False, methods=["POST"])
    def login(self, request):
        # create login system using simplejwt
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
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        )