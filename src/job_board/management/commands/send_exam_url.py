from django.core.management import BaseCommand

from job_board.tasks import send_exam_url_if


class Command(BaseCommand):
    def handle(self, *args, **options):
        send_exam_url_if(3, 4)
