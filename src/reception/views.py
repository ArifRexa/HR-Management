import shortuuid  # to generate short unique IDs
from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Reception

def generate_random_link(request):
    unique_url = shortuuid.uuid()  

    random_link = reverse('visitor_form', args=[unique_url])
    full_url = f"{request.build_absolute_uri(random_link)}"
    
    return redirect(full_url)


def visitor_form(request, unique_url):
    if request.method == 'POST':
        name = request.POST.get('name')
        agenda = request.POST.get('agenda')
        comment = request.POST.get('comment')

        Reception.objects.create(name=name, agenda=agenda, comment=comment)
        return redirect('success_page')

    return render(request, 'visitor_form.html')

def success_page(request):
    return render(request, 'success_page.html')
