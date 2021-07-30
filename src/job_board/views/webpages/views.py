from django.views.generic import TemplateView


class WebsiteView(TemplateView):
    template_name = 'website/index.html'
