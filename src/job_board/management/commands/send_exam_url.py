from django.core.management import BaseCommand

from job_board.tasks import send_exam_url_if, mark_merit


class Command(BaseCommand):
    def handle(self, *args, **options):
        mark_merit(4)
