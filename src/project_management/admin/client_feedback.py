from functools import update_wrapper
import datetime
from dateutil.relativedelta import relativedelta, FR
from config.settings import employee_ids, CLIENT_FEEDBACK_VIDEO_EMBED_URL
from django.contrib import admin, messages
from django.contrib.auth.decorators import login_required
from django.urls import path, reverse
from django.contrib.auth.models import AnonymousUser, User
from django.template.response import TemplateResponse
from django.db import models
from django.db.models import Max, Subquery, OuterRef, Case, When, Value
from django.db.models.functions import Trunc
from django.http import HttpResponseNotFound

from django.shortcuts import redirect

from django.utils import timezone

from project_management.models import Project, ProjectToken
# from project_management.forms import ClientFeedbackForm


def get_last_x_friday(start_date, num_of_week):
    n = -num_of_week - 1
    for i in range(-1, n, -1):
        yield start_date + relativedelta(weekday=FR(i))

# @admin.site.register(ProjectToken)

# class ProjectTokenAdmin(admin.ModelAdmin):
class ProjectTokenAdmin(admin.ModelAdmin):
    list_display = ('project', 'token', 'created_at', 'updated_at')
    search_fields = ('project__title', 'token')
    readonly_fields = ('token',)
    
    def has_module_permission(self, request):
        return False

admin.site.register(ProjectToken, ProjectTokenAdmin)

# @admin.register(ClientFeedback)
# class ClientFeedbackAdmin(admin.ModelAdmin):
#     list_display = ('project', 'avg_rating')
#     list_filter = ('project', 'avg_rating')
#     search_fields = ('project__title',)
#     autocomplete_fields = ('project',)
#
#     URL_ACCESS_IDS = [30, ]
#
#     def custom_changelist_view(self, request, *args, **kwargs) -> TemplateResponse:
#         if not request.user.is_authenticated or not request.user.has_perm("project_management.can_see_client_feedback_admin"):
#             return redirect('/admin/')
#
#         num_of_week = 4
#
#         x_weeks = [i.date() for i in get_last_x_friday(datetime.datetime.today(), num_of_week)]
#         x_weeks_titles = [i.strftime("%b %d, %Y") for i in x_weeks]
#
#         order_keys = {
#             '1': 'last_feedback_rating',
#             '-1': '-last_feedback_rating',
#         }
#
#         order_by = ['-current_feedback_exists', '-last_feedback_date']
#
#         o=request.GET.get('o', None)
#         if o and o in order_keys.keys():
#             order_by.insert(1, order_keys.get(o))
#
#         last_week=timezone.now() + relativedelta(weekday=FR(-1))
#         last_week=last_week.date()
#
#         c_fback_qs = ClientFeedback.objects.filter(
#                         project=OuterRef('pk'),
#                         feedback_week=last_week,
#                     )
#
#         projects = Project.objects.filter(active=True).annotate(
#             last_feedback_date=Max('clientfeedback__updated_at'),
#             last_feedback_rating=Subquery(c_fback_qs.values('avg_rating')[:1]),
#             current_feedback_exists=Case(
#                 When(last_feedback_rating=None, then=Value(False)),
#                 default=Value(True),
#                 output_field=models.BooleanField(),
#             ),
#         ).order_by(*order_by)
#
#         weekly_feedbacks = list()
#         for pr in projects:
#             temp = []
#             last_x_weeks_feedback = pr.last_x_weeks_feedback(num_of_week)
#
#             for week in x_weeks:
#                 for feedback in last_x_weeks_feedback:
#                     if week == feedback.feedback_week:
#                         temp.append(feedback)
#                         break
#                 else:
#                     temp.append(None)
#
#             weekly_feedbacks.append(temp)
#
#         context = dict(
#                 self.admin_site.each_context(request),
#                 url_permission=request.user.employee.id in self.URL_ACCESS_IDS,
#                 week_titles=x_weeks_titles,
#                 weekly_feedbacks=zip(projects, weekly_feedbacks),
#                 o=o, # order key
#             )
#         return TemplateResponse(request, 'admin/client_feedback/client_feedback_admin.html', context)
#
#
#     def client_feedback_urls_view(self, request, *args, **kwargs):
#         if not request.user.is_authenticated or request.user.employee.id not in self.URL_ACCESS_IDS:
#             return redirect('/')
#
#         token_objs = ProjectToken.objects.all().values('project__title', 'token')
#
#         BASE_URL = f'http://{request.get_host()}'
#
#         for token_obj in token_objs:
#             kwargs = dict(
#                 token=token_obj['token'],
#             )
#             token_obj['url'] = BASE_URL + reverse("admin:client_feedback", kwargs=kwargs)
#
#         context = dict(
#                 self.admin_site.each_context(request),
#                 token_objs=token_objs
#             )
#         return TemplateResponse(request, 'admin/client_feedback/client_feedback_urls.html', context)
#
#
#     def get_urls(self):
#         def wrap(view):
#             def wrapper(*args, **kwargs):
#                 return self.admin_site.admin_view(view)(*args, **kwargs)
#             wrapper.model_admin = self
#             return update_wrapper(wrapper, view)
#
#         info = self.model._meta.app_label, self.model._meta.model_name
#
#         urls = super(ClientFeedbackAdmin, self).get_urls()
#
#         employee_online_urls = [
#             path("admin/", wrap(self.changelist_view), name="%s_%s_changelist" % info),
#
#             path("", self.custom_changelist_view, name='client_feedback_admin'),
#             path("urls/", self.client_feedback_urls_view, name='client_feedback_urls'),
#
#             path('client-feedback/<str:token>/', self.client_feedback_view, name='client_feedback'),
#             path('client-feedback/<str:token>/update/', self.client_feedback_form_view, name='client_feedback_form'),
#         ]
#         return employee_online_urls + urls
#
#
#     def client_feedback_view(self, request, token, *args, **kwargs):
#         if request.method == 'GET':
#             project_token = ProjectToken.objects.filter(token=token)
#             context = dict(
#                 self.admin_site.each_context(request),
#                 is_nav_sidebar_enabled=False,
#             )
#
#             if not project_token.exists():
#                 return HttpResponseNotFound("<h1>Invalid / Expired URL</h1>")
#             else:
#                 project = project_token.last().project
#                 current_feedback_exists = ClientFeedback.objects.filter(
#                     project=project,
#                     feedback_week=datetime.datetime.today().date() + relativedelta(weekday=FR(-1)),
#                 ).exists()
#
#                 feedback_objs = ClientFeedback.objects.filter(
#                     project=project,
#                 ).order_by('-created_at')
#
#                 form = ClientFeedbackForm()
#
#                 context = dict(
#                     context,
#                     temp_token=token,
#                     project=project,
#                     current_feedback_exists=current_feedback_exists,
#                     feedback_objs=feedback_objs,
#                     feedback_form=form,
#                     youtube_url=CLIENT_FEEDBACK_VIDEO_EMBED_URL,
#                 )
#             return TemplateResponse(request, 'admin/client_feedback/client_feedback.html', context)
#
#
#     def client_feedback_form_view(self, request, token, *args, **kwargs):
#         project_token = ProjectToken.objects.filter(token=token)
#         context = dict(
#             self.admin_site.each_context(request),
#             is_nav_sidebar_enabled=False,
#         )
#
#         if not project_token.exists():
#             return HttpResponseNotFound("<h1>Invalid / Expired URL</h1>")
#         else:
#             project = project_token.last().project
#             feedback_obj = ClientFeedback.objects.filter(
#                 project=project,
#                 feedback_week=datetime.datetime.today().date() + relativedelta(weekday=FR(-1)),
#             ).last()
#             if request.method == 'POST':
#                 form = ClientFeedbackForm(request.POST, instance=feedback_obj)
#                 if form.is_valid():
#                     form = form.save(commit=False)
#                     form.project = project
#                     form.save()
#                     # messages.success(request, 'Your feedback has been submitted successfully')
#                     return redirect('admin:client_feedback', token=token)
#                 else:
#                     messages.error(request, 'Please provide all info')
#                     return redirect('admin:client_feedback', token=token)
#             elif request.method == 'GET':
#                 form = ClientFeedbackForm(instance=feedback_obj)
#
#                 feedback_objs = ClientFeedback.objects.filter(
#                     project=project,
#                 ).order_by('-created_at')
#
#                 context = dict(
#                     context,
#                     temp_token=token,
#                     update_feedback=True,
#                     project=project,
#                     feedback_form=form,
#                     feedback_objs=feedback_objs,
#                     youtube_url=CLIENT_FEEDBACK_VIDEO_EMBED_URL,
#                 )
#
#                 return TemplateResponse(request, 'admin/client_feedback/client_feedback.html', context)
            
    # def has_module_permission(self, request):
    #     return False
from django.db.models import Max, Subquery, OuterRef, Case, When, Value, BooleanField

# @admin.register(ClientFeedback)
# class ClientFeedbackAdmin(admin.ModelAdmin):
#     list_display = ('project', 'avg_rating')
#     list_filter = ('project', 'avg_rating')
#     search_fields = ('project__title',)
#     autocomplete_fields = ('project',)

#     URL_ACCESS_IDS = [30, ]

#     def custom_changelist_view(self, request, *args, **kwargs) -> TemplateResponse:
#         if not request.user.is_authenticated or not request.user.has_perm(
#                 "project_management.can_see_client_feedback_admin"):
#             return redirect('/admin/')

#         num_of_months = 3

#         months = [i.date() for i in self.get_last_n_months(datetime.datetime.today(), num_of_months)]
#         month_titles = [i.strftime("%b %Y") for i in months]

#         order_keys = {
#             '1': 'last_feedback_rating',
#             '-1': '-last_feedback_rating',
#         }

#         order_by = ['-current_feedback_exists', '-last_feedback_date']

#         o = request.GET.get('o', None)
#         if o and o in order_keys.keys():
#             order_by.insert(1, order_keys.get(o))

#         last_month = timezone.now().date().replace(day=1) - relativedelta(months=1)

#         c_fback_qs = ClientFeedback.objects.filter(
#             project=OuterRef('pk'),
#             feedback_month=last_month,
#         )

#         projects = Project.objects.filter(active=True).annotate(
#             last_feedback_date=Max('clientfeedback__updated_at'),
#             last_feedback_rating=Subquery(c_fback_qs.values('avg_rating')[:1]),
#             current_feedback_exists=Case(
#                 When(last_feedback_rating=None, then=Value(False)),
#                 default=Value(True),
#                 output_field=BooleanField(),
#             ),
#         ).order_by(*order_by)

#         monthly_feedbacks = []
#         for pr in projects:
#             temp = []
#             last_n_months_feedback = pr.last_n_months_feedback(num_of_months)


#             for month in months:
#                 feedback_found = None
#                 for feedback in last_n_months_feedback:
#                     if month.month == feedback.feedback_month.month:
#                         feedback_found = feedback
#                         break
#                 temp.append(feedback_found)

#             monthly_feedbacks.append(temp)

#         context = dict(
#             self.admin_site.each_context(request),
#             url_permission=request.user.employee.id in self.URL_ACCESS_IDS,
#             month_titles=month_titles,
#             monthly_feedbacks=zip(projects, monthly_feedbacks),
#             o=o,  # order key
#         )
#         return TemplateResponse(request, 'admin/client_feedback/client_feedback_admin.html', context)

#     def client_feedback_urls_view(self, request, *args, **kwargs):
#         if not request.user.is_authenticated or request.user.employee.id not in self.URL_ACCESS_IDS:
#             return redirect('/')

#         token_objs = ProjectToken.objects.all().values('project__title', 'token')

#         BASE_URL = f'http://{request.get_host()}'

#         for token_obj in token_objs:
#             kwargs = dict(
#                 token=token_obj['token'],
#             )
#             token_obj['url'] = BASE_URL + reverse("admin:client_feedback", kwargs=kwargs)

#         context = dict(
#             self.admin_site.each_context(request),
#             token_objs=token_objs
#         )
#         return TemplateResponse(request, 'admin/client_feedback/client_feedback_urls.html', context)

#     def get_urls(self):
#         def wrap(view):
#             def wrapper(*args, **kwargs):
#                 return self.admin_site.admin_view(view)(*args, **kwargs)

#             wrapper.model_admin = self
#             return update_wrapper(wrapper, view)

#         info = self.model._meta.app_label, self.model._meta.model_name

#         urls = super(ClientFeedbackAdmin, self).get_urls()

#         employee_online_urls = [
#             path("admin/", wrap(self.changelist_view), name="%s_%s_changelist" % info),
#             path("", self.custom_changelist_view, name='client_feedback_admin'),
#             path("urls/", self.client_feedback_urls_view, name='client_feedback_urls'),
#             path('client-feedback/<str:token>/', self.client_feedback_view, name='client_feedback'),
#             path('client-feedback/<str:token>/update/', self.client_feedback_form_view, name='client_feedback_form'),
#         ]
#         return employee_online_urls + urls

#     def client_feedback_view(self, request, token, *args, **kwargs):
#         if request.method == 'GET':
#             project_token = ProjectToken.objects.filter(token=token)
#             context = dict(
#                 self.admin_site.each_context(request),
#                 is_nav_sidebar_enabled=False,
#             )

#             if not project_token.exists():
#                 return HttpResponseNotFound("<h1>Invalid / Expired URL</h1>")
#             else:
#                 project = project_token.last().project
#                 current_feedback_exists = ClientFeedback.objects.filter(
#                     project=project,
#                     feedback_month=ClientFeedback.get_current_month(),
#                 ).exists()

#                 feedback_objs = ClientFeedback.objects.filter(
#                     project=project,
#                 ).order_by('-created_at')

#                 form = ClientFeedbackForm()

#                 context.update({
#                     'temp_token': token,
#                     'project': project,
#                     'current_feedback_exists': current_feedback_exists,
#                     'feedback_objs': feedback_objs,
#                     'feedback_form': form,
#                     'youtube_url': CLIENT_FEEDBACK_VIDEO_EMBED_URL,
#                 })
#             return TemplateResponse(request, 'admin/client_feedback/client_feedback.html', context)

#     def client_feedback_form_view(self, request, token, *args, **kwargs):
#         project_token = ProjectToken.objects.filter(token=token)
#         context = dict(
#             self.admin_site.each_context(request),
#             is_nav_sidebar_enabled=False,
#         )

#         if not project_token.exists():
#             return HttpResponseNotFound("<h1>Invalid / Expired URL</h1>")
#         else:
#             project = project_token.last().project
#             feedback_obj = ClientFeedback.objects.filter(
#                 project=project,
#                 feedback_month=ClientFeedback.get_current_month(),
#             ).last()
#             if request.method == 'POST':
#                 form = ClientFeedbackForm(request.POST, instance=feedback_obj)
#                 if form.is_valid():
#                     form = form.save(commit=False)
#                     form.project = project
#                     form.save()
#                     # messages.success(request, 'Your feedback has been submitted successfully')
#                     return redirect('admin:client_feedback', token=token)
#                 else:
#                     messages.error(request, 'Please provide all info')
#                     return redirect('admin:client_feedback', token=token)
#             elif request.method == 'GET':
#                 form = ClientFeedbackForm(instance=feedback_obj)

#                 feedback_objs = ClientFeedback.objects.filter(
#                     project=project,
#                 ).order_by('-created_at')

#                 context.update({
#                     'temp_token': token,
#                     'update_feedback': True,
#                     'project': project,
#                     'feedback_form': form,
#                     'feedback_objs': feedback_objs,
#                     'youtube_url': CLIENT_FEEDBACK_VIDEO_EMBED_URL,
#                 })

#                 return TemplateResponse(request, 'admin/client_feedback/client_feedback.html', context)

#     @staticmethod
#     def get_last_n_months(date, n):
#         months = []
#         for i in range(n):
#             months.append(date - relativedelta(months=i))
#         return months