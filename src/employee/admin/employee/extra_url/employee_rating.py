from django.contrib import admin
from django.template.response import TemplateResponse
from django.contrib import messages

class EmployeeRatingView(admin.ModelAdmin):

    def employee_ratings_view(self, request, *args, **kwargs):
        context = dict(
            self.admin_site.each_context(request),
        )
        return TemplateResponse(request, "admin/employee/rating_list.html", context)