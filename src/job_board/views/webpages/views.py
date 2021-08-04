from django.views.generic import TemplateView

from job_board.models.candidate import CandidateAssessment


class WebsiteView(TemplateView):
    template_name = 'website/index.html'


class MailView(TemplateView):
    template_name = 'mail/evaluation_url_to_admin.html'

    def get_context_data(self, **kwargs):
        candidate_assessment = CandidateAssessment.objects.first()
        return {
            'candidate_assessment': candidate_assessment,
            'url': f'https://job.mediusware.com/exam/{candidate_assessment.unique_id}'
        }
