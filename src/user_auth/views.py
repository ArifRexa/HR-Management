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
User = get_user_model()

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
                    user_logs, created = UserLogs.objects.update_or_create(
                    user=user,
                    defaults={
                        'name': user.username,
                        'email': user.email,
                        'designation': getattr(user, 'employee', None).designation.title if hasattr(user, 'employee') else '',
                        'loging_time': timezone.now()  # Update the login time to now
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
    template_name = 'admin/login.html'

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