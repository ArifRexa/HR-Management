from django.core.mail import send_mail
from django.db.models import ExpressionWrapper, F, DurationField
from django.db.models.functions import Now
from django.template.loader import render_to_string
from django.utils import timezone

from asset_management.models.asset import AssetRequest, AssetRequestStatus


def send_pending_requests_report(days_back=7):
    """
    Task to send email with pending asset requests from the last X days
    Args:
        days_back (int): Number of days to look back (default: 7)
    """

    date_threshold = timezone.now().date() - timezone.timedelta(days=days_back)
    pending_requests = (
        AssetRequest.objects.filter(
            status=AssetRequestStatus.PENDING, created_at__lte=date_threshold
        )
        .annotate(
            due_days=ExpressionWrapper(
                Now() - F("created_at"), output_field=DurationField()
            )
        )
        .select_related("category", "created_by")
        .prefetch_related("asset_request_notes")
    )
    context = {
        "date": timezone.now().date(),
        "days_back": days_back,
        "requests": pending_requests,
    }

    html_content = render_to_string(
        "admin/asset/email/pending_requests_report.html", context
    )

    subject = "Pending Asset Requests Report"
    send_mail(
        subject=subject,
        message="Please view this email in HTML format to see the report.",
        from_email="coredeveloper.2013@gmail.com",
        recipient_list=["admin@mediusware.com"],
        html_message=html_content,
        fail_silently=False,
    )
    return f"Sent report with {pending_requests.count()} pending requests"
