from django.contrib import admin
from django.urls import path

from employee.admin.employee.extra_url.formal_view import FormalView
from employee.admin.employee.extra_url.graph_view import GraphView
from employee.admin.employee.extra_url.sms_view import SMSView

class EmployeeExtraUrls(SMSView, GraphView, FormalView, admin.ModelAdmin):
    def get_urls(self):
        urls = super().get_urls()
        employee_urls = [
            path('formal-summery/', self.admin_site.admin_view(self.formal_summery_view), name='employee.summery'),
            path('observe-new-employee/', self.admin_site.admin_view(self.observe_new_employee), name='employee.observenewemployee'),
            path('<int:employee_id__exact>/salary/received-history/',
                 self.admin_site.admin_view(self.salary_receive_history_view),
                 name='employee.salary.receive.history'),
            path('notice-board/', self.admin_site.admin_view(self.notice_bord), name='employee.notice_board'),
            path('graph/', self.admin_site.admin_view(self.all_employee_graph_view), name='employee.hours.graph'),
            path('<int:employee_id__exact>/graph/', self.admin_site.admin_view(self.employee_graph_view),
                 name='hour_graph'),
            path('<int:employee_id__exact>/time-graph/', self.admin_site.admin_view(self.employee_time_base_graph_view),
                 name='time_hour_graph'),
            path('<int:project_id__exact>/project-time-graph/', self.admin_site.admin_view(self.project_graph_view),
                 name='project_hour_graph'),
            path('announce/sms/', self.admin_site.admin_view(self.sms_announce_view),
                 name='employee.announce.sms'),
            path('announce/sms/post/', self.admin_site.admin_view(self.send_sms),
                 name='employee.announce.sms.post')
        ]
        return employee_urls + urls
