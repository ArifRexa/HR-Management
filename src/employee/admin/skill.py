from django.contrib import admin

from employee.models import Skill


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('title', 'note')
    search_fields = ('title',)
    list_per_page = 20

    def has_module_permission(self, request):
        return False
