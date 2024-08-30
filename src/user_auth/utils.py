
from .models import Profile
import random
from django.core.mail import send_mail

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_via_email(user):
    otp_code = generate_otp()

    # Save OTP in the database
    otp, created = Profile.objects.get_or_create(user=user)
    otp.otp = otp_code
    print(otp.otp,"Your OTP")
    otp.save()

    subject = 'Your OTP Code To Login Mediusware HR'
    message = f'Your OTP code is {otp}'
    email_from = 'admin@mediusware.com'
    recipient_list = [user.email]
    # send_mail(subject, message, email_from, recipient_list)
