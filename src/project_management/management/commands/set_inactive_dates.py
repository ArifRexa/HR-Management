from django.core.management.base import BaseCommand
from django.utils import timezone

from project_management.models import Client



class Command(BaseCommand):
    help = "Set current date in the inactive_from field for all clients when client have active=False."


    def handle(self, *args, **options):
        current_date = timezone.now().date()
        count = Client.objects.filter(
            active=False,
        ).update(
            inactive_from=current_date,
        )
        self.stdout.write(self.style.SUCCESS(f"Set the inactive_from value as {current_date.isoformat()} for {count} clients."))
