from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
from account.models import AccountJournal
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

@require_http_methods(["POST", "GET"])
@login_required(login_url="/admin/login/")
def payment_voucher(request, id):
    voucher = get_object_or_404(AccountJournal, id=id)
    print(voucher)
    response = HttpResponse(content_type='application/pdf')
    filename = str(timezone.now())
    response['Content-Disposition'] = f'attachment; filename="payment-voucher-{filename}.pdf"'
    
    return HttpResponse('PDF Download')