import random
from datetime import timedelta

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework import decorators, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from apps.employeeapp.serializers import EmployeeListSerializer
from apps.mixin.views import BaseModelViewSet
from user_auth.models import Profile, UserLogs

from .serializers import OTPSerializer, UserLoginSerializer, UserSerializer
from .utils import (
    get_browser_name,
    get_device_name,
    get_ip_address,
    get_location_by_ip,
    get_operating_system,
)


class UserViewSet(BaseModelViewSet):
    queryset = User.objects.select_related("employee").prefetch_related(
        "employee__leave_set", "groups__permissions"
    )
    serializer_class = UserSerializer

    serializers = {
        "login": UserLoginSerializer,
        "verify_otp": OTPSerializer,
    }
    permissions = {
        "login": [permissions.AllowAny()],
        "verify_otp":[permissions.AllowAny()],
    }

    def _generate_otp(self):
        return str(random.randint(100000, 999999))

    def _send_otp_via_email(self, otp, user_email):

        subject = "Your OTP Code To Login Mediusware HR"
        message = f"Your OTP code is {otp}"
        email_from = "admin@mediusware.com"
        recipient_list = [user_email]
        send_mail(subject, message, email_from, recipient_list)

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
        otp_code = self._generate_otp()

        # Save OTP in the database
        otp, created = Profile.objects.get_or_create(
            user=user, defaults={"otp": otp_code}
        )
        if not created:
            otp.otp = otp_code
            otp.save()

        self._send_otp_via_email(otp_code, user.email)

        return Response(
            {"message": "OTP sent successfully", "user_id": user.id},
            status=status.HTTP_200_OK,
        )
    
    @decorators.action(detail=True, methods=["POST"], url_path="resend-otp")
    def resend_otp(self, request, *args, **kwargs):
        user = self.get_object()
        otp_code = self._generate_otp()

        # Save OTP in the database
        otp, created = Profile.objects.get_or_create(
            user=user, defaults={"otp": otp_code}
        )
        if not created:
            otp.otp = otp_code
            otp.save()

        self._send_otp_via_email(otp_code, user.email)

        return Response(
            {"message": "OTP resent successfully", "user_id": user.id},
            status=status.HTTP_200_OK,
        )

    @decorators.action(detail=True, methods=["POST"], url_path="verify-otp")
    def verify_otp(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp_code = serializer.validated_data["otp"]
        user = self.get_object()
        otp = Profile.objects.get(user=user)
        if otp.otp != otp_code:
            return Response(
                {"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST
            )

        expire_time = otp.otp_created_at + timedelta(minutes=1)
        if timezone.now() > expire_time:
            return Response(
                {"error": "OTP expired. Please request a new one."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        refresh = RefreshToken.for_user(user)
        user_data = EmployeeListSerializer(user.employee).data
        user_data["refresh"] = str(refresh)
        user_data["access"] = str(refresh.access_token)
        # save url logs
        location = get_location_by_ip(request)
        device_name = get_device_name(request)
        browser_name = get_browser_name(request)
        ip_address = get_ip_address(request)  # Get IP address
        operating_system = get_operating_system(request)  # Get OS

        user_logs, created = UserLogs.objects.update_or_create(
            user=user,
            defaults={
                "name": user.username,
                "email": user.email,
                "designation": (
                    getattr(user, "employee", None).designation.title
                    if hasattr(user, "employee")
                    else ""
                ),
                "loging_time": timezone.now(),
                "location": location,
                "browser_name": browser_name,
                "device_name": device_name,
                "ip_address": ip_address,
                "operating_system": operating_system,
            },
        )
        user_data["message"] = "OTP verified successfully"
        return Response(user_data, status=status.HTTP_200_OK)

    # user registration action
    @decorators.action(detail=False, methods=["POST"])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        user_data = EmployeeListSerializer(user.employee).data
        user_data["refresh"] = str(refresh)
        user_data["access"] = str(refresh.access_token)
        return Response(user_data, status=status.HTTP_201_CREATED)
