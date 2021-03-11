from django.contrib import admin

# Register your models here.
from django.db import models
from .models import Job, JobForm


class JobFormInline(admin.TabularInline):
    model = JobForm


class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'last_date')
    inlines = (JobFormInline,)


admin.site.register(Job, JobAdmin)
