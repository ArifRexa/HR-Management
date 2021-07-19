from collections import OrderedDict

from django.utils import timezone
from rest_framework import serializers

from job_board.models import ResetPassword, Candidate


class ValidCandidateEmail:
    def __call__(self, value: OrderedDict):
        print(*value.items())
        if not Candidate.objects.filter(*value.items()).first():
            raise serializers.ValidationError(
                {'email': 'Your given email is not found in candidate list, please insert a valid email address'})


class SendOTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResetPassword
        fields = ['email']
        validators = [ValidCandidateEmail()]


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()
    password = serializers.CharField(min_length=6)

    def validate(self, data):
        if ResetPassword.objects.filter(
                otp_used_at__isnull=True,
                email__exact=data['email'],
                otp__exact=data['otp'],
                otp_expire_at__gte=timezone.now()).last():
            return data
        raise serializers.ValidationError({'otp': 'OTP is not correct or expire'})

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        candidate = Candidate.objects.filter(email__exact=validated_data['email']).first()
        candidate.password = validated_data['password']
        candidate.save()
        return candidate
