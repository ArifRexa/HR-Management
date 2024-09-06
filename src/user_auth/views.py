import datetime
import email
from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import OTPForm
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from .utils import send_otp_via_email  #
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from .models import UserLogs
from user_agents import parse

User = get_user_model()


def get_device_name(request):
    user_agent = request.META.get('HTTP_USER_AGENT', '')

    if "Mobile" in user_agent:
        device_type = "Mobile"
    elif "Tablet" in user_agent:
        device_type = "Tablet"
    elif "Windows" in user_agent or "Macintosh" in user_agent or "Linux" in user_agent:
        device_type = "Desktop"
    else:
        device_type = "Unknown"

    return device_type

def get_browser_name(request):
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    parsed_user_agent = parse(user_agent)
    return parsed_user_agent.browser.family


def get_location_by_ip(request):
    import requests

    ip = request.META.get('REMOTE_ADDR')
    response = requests.get(f'https://ipinfo.io/{ip}/json')
    data = response.json()
    
    location = data.get('city', 'Unknown Location') + ', ' + data.get('country', 'Unknown Country')
    return location

def get_ip_address(request):
    return request.META.get('REMOTE_ADDR')

def get_operating_system(request):
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    parsed_user_agent = parse(user_agent)
    return parsed_user_agent.os.family

def verify_otp(request):
    if request.method == 'POST':
        form = OTPForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data['otp']
            user_id = request.session.get('pre_login_user_id')

            if user_id:
                user = User.objects.get(id=user_id)

                if user.profile.otp == otp:
                    # Clear OTP after successful verification
                    user.profile.otp = None
                    user.profile.save()

                    # Log the user in
                    auth_login(request, user)

                    location = get_location_by_ip(request)
                    device_name = get_device_name(request)
                    browser_name = get_browser_name(request)
                    ip_address = get_ip_address(request)  # Get IP address
                    operating_system = get_operating_system(request)  # Get OS

                    user_logs, created = UserLogs.objects.update_or_create(
                    user=user,
                    defaults={
                        'name': user.username,
                        'email': user.email,
                        'designation': getattr(user, 'employee', None).designation.title if hasattr(user, 'employee') else '',
                        'loging_time': timezone.now() , # Update the login time to now
                        'location':location,
                        'browser_name':browser_name,
                        'device_name':device_name,
                        'ip_address': ip_address,  # Save IP address
                        'operating_system': operating_system,  # Save OS
                    }
                )
                    request.session.pop('pre_login_user_id', None)

                    return redirect('/admin/')  # Redirect to the admin dashboard
                else:
                    massage =  'Invalid OTP'
                    return render(request, 'verify_otp.html', {'form': form,'massage':massage})
            else:
                messages.error(request, 'Session expired. Please log in again.')
                return redirect('/admin/login/')
    else:
        form = OTPForm()

    return render(request, 'verify_otp.html', {'form': form})

class CustomAdminLoginView(LoginView):
    form_class = AuthenticationForm
    template_name = 'login.html'

    def form_valid(self, form):
        user = form.get_user()
        try:
            # Attempt to send the OTP
            send_otp_via_email(user)
        except Exception as e:
            messages.error(self.request, "Failed to send OTP. Please try again.")
            return self.form_invalid(form)  

    
        self.request.session['pre_login_user_id'] = user.id
        return redirect('/admin/verify-otp/')  