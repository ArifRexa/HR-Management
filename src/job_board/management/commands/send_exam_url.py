import datetime
from django.core.management import BaseCommand
from django.utils import timezone

from job_board.models.assessment import Assessment
from job_board.models.candidate import CandidateAssessment
from job_board.tasks import send_exam_url_if, mark_merit


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('passed_exam_id', type=int, help='Pass exam id')
        parser.add_argument('target_exam_id', type=int, help='Target exam id')

    def handle(self, *args, **options):
        self._can_start_exam_if_pass(options['passed_exam_id'], options['target_exam_id'])

    def _can_start_exam_if_pass(self, passe_exam_id, send_exam_id):
        timelimit = timezone.now() - datetime.timedelta(days=60)
        assessment = Assessment.objects.get(pk=passe_exam_id)
        candidate_assessments = CandidateAssessment.objects.filter(
            updated_at__gt=timelimit,
            assessment_id=passe_exam_id,
            score__gte=assessment.pass_score,
            step__contains={'auto_checked': False}
        ).all()
        print(candidate_assessments)
        if candidate_assessments.count() > 0:
            target_candidate_assessment = CandidateAssessment.objects.filter(
                candidate_job__in=list(candidate_assessments.values_list('candidate_job', flat=True)),
                assessment_id=send_exam_id,
                can_start_after__isnull=True
            ).all()
            self.__set_start_after(target_candidate_assessment)
            self.__set_start_after(candidate_assessments)

    @staticmethod
    def __set_start_after(target_candidate_assessment):
        for candidate_assessment in target_candidate_assessment:
            candidate_assessment.can_start_after = timezone.now()
            candidate_assessment.save()

    @staticmethod
    def __mark_auto_checked(candidate_assessments):
        for candidate_job in candidate_assessments:
            candidate_job.step['auto_checked'] = True
            candidate_job.save()
