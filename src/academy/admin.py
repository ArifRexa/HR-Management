from django.contrib import admin

from academy.models import MarketingSlider

# Register your models here.

@admin.register(MarketingSlider)
class MarketingSliderAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    date_hierarchy = 'created_at'
    search_fields = ['title']
