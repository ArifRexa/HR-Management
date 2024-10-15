from django.contrib import admin
from .models import Reception

@admin.register(Reception)
class ReceptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'agenda', 'created_at')
    list_filter = ('agenda',)