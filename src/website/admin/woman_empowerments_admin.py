from django.contrib import admin

from website.models_v2.woman_empowermens import Environment, Photo, WomanAchievement, WomanEmpowerment, WomanInspiration

class WomanAchievementInline(admin.TabularInline):
    model = WomanAchievement
    extra = 1

class WomanInspirationInline(admin.TabularInline):
    model = WomanInspiration
    extra = 1

class EnvironmentInline(admin.TabularInline):
    model = Environment
    extra = 1

class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 1

@admin.register(WomanEmpowerment)
class WomanEmpowermentAdmin(admin.ModelAdmin):
    list_display = ('title',)
    inlines = [WomanAchievementInline, WomanInspirationInline, EnvironmentInline, PhotoInline]

