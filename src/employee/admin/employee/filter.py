from django.contrib.admin import SimpleListFilter
from django.utils.translation import gettext_lazy as _

from employee.models.employee_skill import EmployeeSkill

class MonthFilter(SimpleListFilter):
    title = _('month')
    parameter_name = 'month'

    def lookups(self, request, model_admin):
        return [
            (1, _('January')),
            (2, _('February')),
            (3, _('March')),
            (4, _('April')),
            (5, _('May')),
            (6, _('June')),
            (7, _('July')),
            (8, _('August')),
            (9, _('September')),
            (10, _('October')),
            (11, _('November')),
            (12, _('December')),
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(month=self.value())
        return queryset


class TopSkillFilter(SimpleListFilter):
    title = _('Skill')
    parameter_name = 'employeeskill__id__exact'

    def lookups(self, request, model_admin):
        skills = EmployeeSkill.objects.filter(percentage__gte=60)
        return [(skill.id, skill.skill.title) for skill in skills]


    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(employeeskill__id__exact=self.value())
        return queryset