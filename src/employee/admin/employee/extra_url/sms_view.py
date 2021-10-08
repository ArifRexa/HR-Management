from django.contrib import admin, messages
from django.core import management
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseNotFound
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse

from employee.admin.employee._forms import SMSAnnounceForm


class SMSView(admin.ModelAdmin):
    def sms_announce_view(self, request, *args, **kwargs):
        """
        Render sms announce view
        @param request:
        @param args:
        @param kwargs:
        @return TemplateResponse:
        """
        if not request.user.is_superuser:
            raise PermissionDenied
        context = dict(
            self.admin_site.each_context(request),
            title='SMS Announcement',
            form=SMSAnnounceForm()
        )
        return TemplateResponse(request, "admin/employee/sms_announce.html", context=context)

    def send_sms(self, request, *args, **kwargs):
        """
        Send sms to selected employees by management command
        @param request:
        @param args:
        @param kwargs:
        @return redirect back | @return 404:
        """
        if request.method == 'POST':
            form = SMSAnnounceForm(request.POST)
            context = dict(
                self.admin_site.each_context(request),
                title='SMS Announcement',
                form=form
            )
            if form.is_valid():
                management.call_command('sms_notification_to_employee',
                                        list(form.cleaned_data['employees'].values_list('id', flat=True)),
                                        form.cleaned_data['message'])
                messages.success(request=request, message='SMS sent')
                return redirect(reverse('admin:employee.announce.sms'))
            else:
                return TemplateResponse(request, "admin/employee/sms_announce.html", context=context)
        return HttpResponseNotFound('<h1>Page not found</h1>')
