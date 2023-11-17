from django.contrib import admin

from job_board.models.promotion import SMSPromotion


@admin.register(SMSPromotion)
class SMSPromotionAdmin(admin.ModelAdmin):
    list_display = ('title', 'sms_body', 'is_default')
    list_editable = ('is_default',)

    def has_module_permission(self, request):
        return False
