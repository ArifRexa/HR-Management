from django.contrib import admin, messages
from job_board.models.candidate_email import CandidateEmail,CandidateEmailAttatchment

class CandidateEmailAttatchmentInline(admin.TabularInline):  
    model = CandidateEmailAttatchment
    extra = 0  


@admin.register(CandidateEmail)
class CandidateEmailAdmin(admin.ModelAdmin):
    list_display = (
        'subject',
    )
      
    inlines = (CandidateEmailAttatchmentInline,)

    def has_module_permission(self, request):
        return False
