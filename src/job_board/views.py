from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.core.exceptions import PermissionDenied

# Create your views here.
from django.views.generic import TemplateView

from job_board.models import Assessment


class AssessmentPreview(LoginRequiredMixin, AccessMixin, TemplateView):
    template_name = 'admin/assessment/preview.html'

    def get_context_data(self, **kwargs):
        assessment = Assessment.objects.filter(**kwargs).first()
        return {
            'assessment': assessment
        }

    def dispatch(self, request, *args, **kwargs):
        if request.user.has_perm('preview_assessment'):
            return super(AssessmentPreview, self).dispatch(request, *args, **kwargs)
        raise PermissionDenied("Permission denied")
