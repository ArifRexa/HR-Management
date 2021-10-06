from django.core.management import BaseCommand
from django.utils import timezone

from job_board.models.candidate import CandidateAssessment


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('assessment_id', type=int)

    def handle(self, *args, **options):
        candidate_assessments = CandidateAssessment.objects.filter(
            assessment_id=options['assessment_id'],
            exam_end_at__lte=timezone.now(),
            candidate_job__merit=None
        ).all()
        for candidate_assessment in candidate_assessments:
            print('hello', candidate_assessments)
            if candidate_assessment.score >= candidate_assessment.assessment.pass_score:
                candidate_assessment.candidate_job.merit = True
                candidate_assessment.candidate_job.save()
                print('mark merit', candidate_assessment.candidate_job)
                # TODO : Send email to candidate and admin
