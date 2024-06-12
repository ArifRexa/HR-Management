from django.contrib.admin import SimpleListFilter
from django.utils.translation import gettext_lazy as _

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
