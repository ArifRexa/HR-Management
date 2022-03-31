from django.contrib import admin

# Register your models here.
from website.models import Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'order', 'active')
    search_fields = ('title',)
