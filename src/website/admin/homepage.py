from website.models import HomePage, HomePageHeroAnimatedTitle
import nested_admin
from django import forms
from django.contrib import admin

class HomePageHeroAnimatedTitleInline(admin.TabularInline):
    model = HomePageHeroAnimatedTitle
    extra = 1

@admin.register(HomePage)
class HomePageAdmin(admin.ModelAdmin):
    model = HomePage
    inlines = [HomePageHeroAnimatedTitleInline]