# management/commands/check_bulk_email_status.py

from django.core.management.base import BaseCommand
from django_q.models import Success, Failure

class Command(BaseCommand):
    help = 'Check the status of bulk application emails'

    def handle(self, *args, **options):
        # Get successful emails
        successes = Success.objects.filter(group='Bulk Application Emails')
        self.stdout.write(self.style.SUCCESS(f"\nSuccessfully sent emails: {successes.count()}"))
        for success in successes:
            if isinstance(success.result, dict):
                self.stdout.write(f"✓ {success.result.get('email', 'Unknown')}")

        # Get failed emails
        failures = Failure.objects.filter(group='Bulk Application Emails')
        self.stdout.write(self.style.ERROR(f"\nFailed emails: {failures.count()}"))
        for failure in failures:
            self.stdout.write(self.style.ERROR(f"✗ {failure.result}"))
