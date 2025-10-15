import datetime
from datetime import timedelta

from django.contrib import admin
from django.db.models import Q, Sum
# from project_management.models import (
#     DailyProjectUpdateGroupByClient,
#     DailyProjectUpdateGroupByEmployee,
#     DailyProjectUpdateGroupByProject,
#     DailyProjectUpdateGroupByManager,
# )

from functools import partial, update_wrapper, wraps
from django.urls import path
from employee.models.employee import Employee


# @admin.register(DailyProjectUpdateGroupByEmployee)
# class ProjectUpdateGroupByEmployeeAdmin(admin.ModelAdmin):
#     list_display = (
#         "created_at",
#         "get_hours_history",
#         "employee",
#         "project",
#         "update",
#         "hours",
#         "manager",
#         "status",
#     )
#     list_filter = (
#         "status",
#         "project",
#         "employee",
#         "manager",
#     )
#     date_hierarchy = "created_at"
#     autocomplete_fields = (
#         "employee",
#         "project",
#     )
#     change_list_template = "admin/daily_update_groupby_employee.html"
#     readonly_fields = ["status"]
#     sortable_by = ["hours"]
#     fieldsets = (
#         (
#             "Standard info",
#             {"fields": ("employee", "manager", "project", "hours", "status")},
#         ),
#     )

#     class Media:
#         css = {"all": ("css/list.css",)}
#         js = ("js/list.js",)

#     def custom_changelist_view(self, request, extra_context=None):
#         today = datetime.datetime.now().date()
#         yesterday = today - timedelta(days=1)

#         filters = dict()
#         for key, value in request.GET.items():
#             if value != "":
#                 filters[key] = value
#         if len(filters) == 0:
#             filters["created_at__date"] = yesterday

#         daily_project_update_data = dict()
#         employee_hours = self.get_queryset(request).filter(**filters)

#         for hours in employee_hours:
#             key = hours.employee
#             key.set_daily_hours(
#                 key.dailyprojectupdate_employee.filter(**filters)
#                 .aggregate(total_hours=Sum("hours"))
#                 .get("total_hours")
#             )
#             daily_project_update_data.setdefault(key, []).append(hours)

#         sorted_data_set = dict(
#             sorted(
#                 daily_project_update_data.items(),
#                 key=lambda x: x[0].daily_project_hours,
#             )
#         )

#         my_context = {
#             "daily_project_hours_data": sorted_data_set,
#         }
#         return super().changelist_view(request, extra_context=my_context)

#     def has_change_permission(self, request, obj=None):
#         permitted = super().has_change_permission(request, obj=obj)
#         if (
#             not request.user.is_superuser
#             and obj
#             and obj.employee != request.user.employee
#             and obj.manager != request.user.employee
#         ):
#             permitted = False
#         return permitted

#     def get_sortable_by(self, request):
#         return (
#             self.sortable_by
#             if self.sortable_by is not None
#             else self.get_list_display(request)
#         )

#     def get_urls(self):
#         urls = super(ProjectUpdateGroupByEmployeeAdmin, self).get_urls()

#         def wrap(view):
#             def wrapper(*args, **kwargs):
#                 return self.admin_site.admin_view(view)(*args, **kwargs)

#             wrapper.model_admin = self
#             return update_wrapper(wrapper, view)

#         info = self.model._meta.app_label, self.model._meta.model_name
#         custome_urls = [
#             path("admin/", wrap(self.changelist_view), name="%s_%s_changelist" % info),
#             path(
#                 "", self.custom_changelist_view, name="groupby_employee_changelist_view"
#             ),
#         ]
#         return custome_urls + urls

#     def get_queryset(self, request):
#         query_set = super(ProjectUpdateGroupByEmployeeAdmin, self).get_queryset(request)

#         if not request.user.is_superuser and not request.user.has_perm(
#             "project_management.see_all_employee_update"
#         ):
#             return query_set.filter(employee=request.user.employee.id)
#         return query_set.filter(employee__active=True).exclude(employee_id__in=[30])

#     def get_readonly_fields(self, request, obj=None):
#         if request.user.is_superuser:
#             return []

#         if obj:
#             if request.user.employee.manager or request.user.employee.lead:
#                 if obj.manager != obj.employee and obj.manager == request.user.employee:
#                     return ["employee", "manager", "project", "update"]
#                 else:
#                     return []
#             else:
#                 return self.readonly_fields

#         else:
#             if request.user.employee.manager or request.user.employee.lead:
#                 return []
#             else:
#                 return self.readonly_fields


# @admin.register(DailyProjectUpdateGroupByProject)
# class ProjectUpdateGroupByProjectAdmin(admin.ModelAdmin):
#     list_display = (
#         "created_at",
#         "employee",
#         "project",
#         "update",
#         "hours",
#         "manager",
#         "status",
#     )
#     list_filter = (
#         "status",
#         "project",
#         "employee",
#         "manager",
#     )
#     date_hierarchy = "created_at"
#     autocomplete_fields = (
#         "employee",
#         "project",
#     )
#     change_list_template = "admin/daily_update_groupby_project.html"
#     readonly_fields = ["status"]
#     fieldsets = (
#         (
#             "Standard info",
#             {"fields": ("employee", "manager", "project", "hours", "status")},
#         ),
#     )

#     class Media:
#         css = {"all": ("css/list.css",)}
#         js = ("js/list.js",)

#     def custom_changelist_view(self, request, extra_context=None):
#         today = datetime.datetime.now().date()
#         yesterday = today - timedelta(days=1)

#         filters = dict()
#         for key, value in request.GET.items():
#             if value != "":
#                 filters[key] = value
#         if len(filters) == 0:
#             filters["created_at__date"] = yesterday

#         daily_project_update_data = dict()
#         project_hours = self.get_queryset(request).filter(**filters)

#         for hours in project_hours:
#             key = hours.project
#             key.set_project_hours(
#                 key.projects.filter(**filters)
#                 .aggregate(total_hours=Sum("hours"))
#                 .get("total_hours")
#             )
#             daily_project_update_data.setdefault(key, []).append(hours)

#         sorted_data_set = dict(
#             sorted(
#                 daily_project_update_data.items(),
#                 key=lambda x: x[0].total_project_hours,
#             )
#         )

#         my_context = {"daily_project_hours_data": sorted_data_set}
#         return super().changelist_view(request, extra_context=my_context)

#     def has_change_permission(self, request, obj=None):
#         permitted = super().has_change_permission(request, obj=obj)
#         if (
#             not request.user.is_superuser
#             and obj
#             and obj.employee != request.user.employee
#             and obj.manager != request.user.employee
#         ):
#             permitted = False
#         return permitted

#     def get_urls(self):
#         urls = super(ProjectUpdateGroupByProjectAdmin, self).get_urls()

#         def wrap(view):
#             def wrapper(*args, **kwargs):
#                 return self.admin_site.admin_view(view)(*args, **kwargs)

#             wrapper.model_admin = self
#             return update_wrapper(wrapper, view)

#         info = self.model._meta.app_label, self.model._meta.model_name
#         custome_urls = [
#             path("admin/", wrap(self.changelist_view), name="%s_%s_changelist" % info),
#             path(
#                 "", self.custom_changelist_view, name="groupby_project_changelist_view"
#             ),
#         ]
#         return custome_urls + urls

#     def get_queryset(self, request):
#         query_set = super(ProjectUpdateGroupByProjectAdmin, self).get_queryset(request)

#         if not request.user.is_superuser and not request.user.has_perm(
#             "project_management.see_all_employee_update"
#         ):
#             return query_set.filter(employee=request.user.employee.id)
#         return query_set.filter(employee__active=True).exclude(employee_id__in=[30])

#     def get_readonly_fields(self, request, obj=None):
#         if request.user.is_superuser:
#             return []

#         if obj:
#             if request.user.employee.manager or request.user.employee.lead:
#                 if obj.manager != obj.employee and obj.manager == request.user.employee:
#                     return ["employee", "manager", "project", "update"]
#                 else:
#                     return []
#             else:
#                 return self.readonly_fields

#         else:
#             if request.user.employee.manager or request.user.employee.lead:
#                 return []
#             else:
#                 return self.readonly_fields


# @admin.register(DailyProjectUpdateGroupByClient)
# class ProjectUpdateGroupByClientAdmin(admin.ModelAdmin):
#     list_display = (
#         "created_at",
#         "get_client",
#         "employee",
#         "project",
#         "update",
#         "hours",
#         "manager",
#         "status",
#     )
#     list_filter = (
#         "status",
#         "project",
#         "project__client",
#     )
#     date_hierarchy = "created_at"
#     autocomplete_fields = (
#         "employee",
#         "project",
#     )
#     change_list_template = "admin/daily_update_groupby_client.html"
#     readonly_fields = ["status"]
#     fieldsets = (
#         (
#             "Standard info",
#             {
#                 "fields": (
#                     "employee",
#                     "manager",
#                     "project",
#                     "hours",
#                     "status",
#                     "project__client",
#                 )
#             },
#         ),
#     )

#     @admin.display(description="Client")
#     def get_client(self, obj):
#         return obj.project.client.name

#     class Media:
#         css = {"all": ("css/list.css",)}
#         js = ("js/list.js",)

#     def total_client_hours(self, data):
#         return sum(key.total_project_hours for key, value in data.items())

#     def custom_changelist_view(self, request, extra_context=None):
#         today = datetime.datetime.now().date()
#         yesterday = today - timedelta(days=1)

#         filters = {}
#         for key, value in request.GET.items():
#             if value != "":
#                 filters[key] = value
#         if not filters:
#             filters["created_at__date"] = yesterday
#         daily_project_update_data = {}
#         project_hours = (
#             self.get_queryset(request)
#             .select_related("project", "project__client", "employee", "manager")
#             .filter(project__active=True)
#             .filter(**filters)
#         )
#         client_daily_project_update_data = {}
#         for hours in project_hours:
#             key = hours.project
#             key.set_project_hours(
#                 key.projects.filter(**filters)
#                 .aggregate(total_hours=Sum("hours"))
#                 .get("total_hours")
#             )
#             daily_project_update_data.setdefault(key, []).append(hours)

#         sorted_data_set = dict(
#             sorted(
#                 daily_project_update_data.items(),
#                 key=lambda x: x[0].total_project_hours,
#             )
#         )
#         for key, value in sorted_data_set.items():
#             if key.client in client_daily_project_update_data:
#                 client_daily_project_update_data[key.client].update({key: value})
#             else:
#                 client_daily_project_update_data[key.client] = {key: value}

#         sorted_client_data_set = dict(
#             sorted(
#                 client_daily_project_update_data.items(),
#                 key=lambda x: self.total_client_hours(x[1]),
#             )
#         )

#         my_context = {"daily_project_hours_data": sorted_client_data_set}
#         return super().changelist_view(request, extra_context=my_context)

#     def has_change_permission(self, request, obj=None):
#         permitted = super().has_change_permission(request, obj=obj)
#         if (
#             not request.user.is_superuser
#             and obj
#             and obj.employee != request.user.employee
#             and obj.manager != request.user.employee
#         ):
#             permitted = False
#         return permitted

#     def get_urls(self):
#         urls = super(ProjectUpdateGroupByClientAdmin, self).get_urls()

#         def wrap(view):
#             def wrapper(*args, **kwargs):
#                 return self.admin_site.admin_view(view)(*args, **kwargs)

#             wrapper.model_admin = self
#             return update_wrapper(wrapper, view)

#         info = self.model._meta.app_label, self.model._meta.model_name
#         custome_urls = [
#             path("admin/", wrap(self.changelist_view), name="%s_%s_changelist" % info),
#             path(
#                 "", self.custom_changelist_view, name="groupby_client_changelist_view"
#             ),
#         ]
#         return custome_urls + urls

#     def get_queryset(self, request):
#         query_set = super(ProjectUpdateGroupByClientAdmin, self).get_queryset(request)

#         if not request.user.is_superuser and not request.user.has_perm(
#             "project_management.see_all_employee_update"
#         ):
#             return query_set.filter(employee=request.user.employee.id)
#         return query_set.filter(employee__active=True).exclude(employee_id__in=[30])

#     def get_readonly_fields(self, request, obj=None):
#         if request.user.is_superuser:
#             return []

#         if obj:
#             if request.user.employee.manager or request.user.employee.lead:
#                 if obj.manager != obj.employee and obj.manager == request.user.employee:
#                     return ["employee", "manager", "project", "update"]
#                 else:
#                     return []
#             else:
#                 return self.readonly_fields

#         else:
#             if request.user.employee.manager or request.user.employee.lead:
#                 return []
#             else:
#                 return self.readonly_fields


# @admin.register(DailyProjectUpdateGroupByManager)
# class ProjectUpdateGroupByManagerAdmin(admin.ModelAdmin):
#     list_display = (
#         "created_at",
#         "employee",
#         "project",
#         "update",
#         "hours",
#         "manager",
#         "status",
#     )
#     list_filter = (
#         "status",
#         "project",
#         "employee",
#         "manager",
#     )
#     date_hierarchy = "created_at"
#     autocomplete_fields = (
#         "employee",
#         "project",
#     )
#     change_list_template = "admin/daily_update_groupby_manager.html"
#     readonly_fields = ["status"]
#     fieldsets = (
#         (
#             "Standard info",
#             {"fields": ("employee", "manager", "project", "hours", "status")},
#         ),
#     )

#     class Media:
#         css = {"all": ("css/list.css",)}
#         js = ("js/list.js",)

#     def custom_changelist_view(self, request, extra_context=None):
#         today = datetime.datetime.now().date()
#         yesterday = today - timedelta(days=1)
#         filters = dict()
#         for key, value in request.GET.items():
#             if value != "":
#                 filters[key] = value
#         if len(filters) == 0:
#             filters["created_at__date"] = yesterday

#         daily_project_update_data = dict()
#         manager_hours = self.get_queryset(request).filter(**filters)

#         for hours in manager_hours:
#             key = hours.manager
#             key.set_daily_hours(
#                 key.dailyprojectupdate_manager.filter(**filters)
#                 .aggregate(total_hours=Sum("hours"))
#                 .get("total_hours")
#             )
#             daily_project_update_data.setdefault(key, []).append(hours)

#         sorted_data_set = dict(
#             sorted(
#                 daily_project_update_data.items(),
#                 key=lambda x: x[0].daily_project_hours,
#             )
#         )

#         my_context = {"daily_project_hours_data": sorted_data_set}
#         return super().changelist_view(request, extra_context=my_context)

#     def has_change_permission(self, request, obj=None):
#         permitted = super().has_change_permission(request, obj=obj)
#         if (
#             not request.user.is_superuser
#             and obj
#             and obj.employee != request.user.employee
#             and obj.manager != request.user.employee
#         ):
#             permitted = False
#         return permitted

#     def get_urls(self):
#         urls = super(ProjectUpdateGroupByManagerAdmin, self).get_urls()

#         def wrap(view):
#             def wrapper(*args, **kwargs):
#                 return self.admin_site.admin_view(view)(*args, **kwargs)

#             wrapper.model_admin = self
#             return update_wrapper(wrapper, view)

#         info = self.model._meta.app_label, self.model._meta.model_name
#         custome_urls = [
#             path("admin/", wrap(self.changelist_view), name="%s_%s_changelist" % info),
#             path(
#                 "", self.custom_changelist_view, name="groupby_manager_changelist_view"
#             ),
#         ]
#         return custome_urls + urls

#     def get_queryset(self, request):
#         query_set = super(ProjectUpdateGroupByManagerAdmin, self).get_queryset(request)

#         if not request.user.is_superuser and not request.user.has_perm(
#             "project_management.see_all_employee_update"
#         ):
#             return query_set.filter(manager=request.user.maanger.id)
#         return query_set.filter(manager__active=True).exclude(manager_id__in=[30])

#     def get_readonly_fields(self, request, obj=None):
#         if request.user.is_superuser:
#             return []

#         if obj:
#             if request.user.employee.manager or request.user.employee.lead:
#                 if obj.manager != obj.employee and obj.manager == request.user.employee:
#                     return ["employee", "manager", "project", "update"]
#                 else:
#                     return []
#             else:
#                 return self.readonly_fields

#         else:
#             if request.user.employee.manager or request.user.employee.lead:
#                 return []
#             else:
#                 return self.readonly_fields
