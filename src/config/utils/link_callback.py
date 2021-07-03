import os
from io import BytesIO

from django.contrib.staticfiles import finders
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

import config.settings
from config import settings


def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    result = finders.find(uri)
    if result:
        if not isinstance(result, (list, tuple)):
            result = [result]
        result = list(os.path.realpath(path) for path in result)
        path = result[0]
    else:
        static_url = settings.STATIC_URL  # Typically /static/
        static_root = settings.STATIC_ROOT  # Typically /home/userX/project_static/
        media_url = settings.MEDIA_URL  # Typically /media/
        media_root = settings.MEDIA_ROOT  # Typically /home/userX/project_static/media/

        if uri.startswith(media_url):
            path = os.path.join(media_root, uri.replace(media_url, ""))
        elif uri.startswith(static_url):
            path = os.path.join(static_root, uri.replace(static_url, ""))
        else:
            return uri

    # make sure that file exists
    if not os.path.isfile(path):
        raise Exception(
            'media URI must start with %s or %s' % (static_url, media_url)
        )
    return path


def render_to_pdf(template_path, context):
    context['watermark'] = f"{config.settings.STATIC_ROOT}/stationary/letter_head.jpeg"
    template = get_template(template_path)
    html = template.render(context)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("utf-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None
