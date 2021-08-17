from django.contrib.auth import hashers
from django.utils import timezone
from rest_framework import serializers

from config import settings
from job_board.models.candidate import ResetPassword, Candidate


class ValidCandidateEmail:
    """
    Candidate Email Validation
    """

    def __call__(self, value):
        if not Candidate.objects.filter(email=value).first():
            raise serializers.ValidationError(
                'Your given email is not found in candidate list, please insert a valid email address')


class SendOTPSerializer(serializers.ModelSerializer):
    """
    this serializer will use for sending OTP to candidate email
    """
    email = serializers.EmailField(validators=[ValidCandidateEmail()])

    class Meta:
        model = ResetPassword
        fields = ['email']


class ResetPasswordSerializer(serializers.Serializer):
    """
    Password reset serializer is use for reset password from otp
    ** this serializer cannot be use for change password while the user is logged in
    """
    email = serializers.EmailField(validators=[ValidCandidateEmail()])
    otp = serializers.CharField(min_length=6, max_length=6)
    password = serializers.CharField(min_length=6, max_length=40)

    def validate(self, data):
        """
        Validate if the otp is correct and does not expire
        @param data:
        @return:
        """
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
        """
        Update candidate password
        @param validated_data:
        @return:
        """
        candidate = Candidate.objects.filter(email__exact=validated_data['email']).first()
        candidate.password = hashers.make_password(validated_data['password'], salt=settings.CANDIDATE_PASSWORD_HASH)
        candidate.save()

        pass_reset = ResetPassword.objects.filter(otp__exact=validated_data['otp']).last()
        pass_reset.otp_used_at = timezone.now()
        pass_reset.save()
        return validated_data


class ChangePasswordSerializer(serializers.Serializer):
    """
    Change password serializer , change authenticated candidate password only if the current password mathced
    """
    current_password = serializers.CharField()
    new_password = serializers.CharField()
    retype_new_password = serializers.CharField()

    given_password = ''

    def validate(self, data):
        """
        validate if new_password and re_type_new_password are same
        validate if current password matched with given password
        @param data:
        @return:
        """
        if data['new_password'] != data['retype_new_password']:
            raise serializers.ValidationError({'new_password': 'Retype password does not match with current password'})
        user_pass = self.context['request'].user.password
        given_current_pass = hashers.make_password(data['current_password'], salt=settings.CANDIDATE_PASSWORD_HASH)
        if user_pass == given_current_pass:
            self.given_password = given_current_pass
            return data
        raise serializers.ValidationError({'current_password': 'Current password does not matched'})

    def update(self, instance, validated_data):
        """
        Update authenticated user password
        @param instance:
        @param validated_data:
        @return:
        """
        instance.password = hashers.make_password(validated_data['new_password'], salt=settings.CANDIDATE_PASSWORD_HASH)
        instance.save()
        print(instance.password)
        return instance
