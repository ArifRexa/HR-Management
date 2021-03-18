import datetime

from django.contrib import messages

from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from django.views import View
from rest_framework.utils import json

from .forms import JobApplyForm
from .models import Job, JobForm, JobApply


def home(request):
    return render(request, 'job/home.html')


def jobs(request):
    jobs = Job.objects.all()
    data = {
        'jobs': jobs
    }
    return render(request, 'job/jobs_list.html', data)


class jobDetails(View):
    def get(self, request, id):
        job = get_object_or_404(Job, pk=id)
        data = {
            'job': job,
        }
        return render(request, 'job/job-details.html', data)


class jobApply(View):
    def get(self, request, id):
        job = get_object_or_404(Job, pk=id)
        job_form = JobForm.objects.filter(job_id=job.id)
        apply = JobApply.objects.filter(job_id=job.id)
        data = {
            'job': job,
            'job_form': job_form,
            'apply': apply,
        }
        Arr = [("Forename", "Paul"), ("Surname", "Dinh")]
        print(Arr)
        for appl in apply:
            print(appl.data)
            # for Key1, Value1 in appl.data:
            #     print(Key1, "=", Value1)

        for Key, Value in Arr:
            print(Key, "=", Value)

        return render(request, 'job/job-apply.html', data)

    def post(self, request, id):
        job = get_object_or_404(Job, pk=id)
        form_list = []

        uploaded_file = request.FILES['cv']
        fs = FileSystemStorage()
        file_name = fs.save(uploaded_file.name, uploaded_file)

        lists = list(request.POST.items())  # list of key-value tuples
        for idx, val in enumerate(lists):
            if (idx > 0):
                form_list.append(val)

        apply = JobApply()
        apply.data = form_list
        apply.file = file_name
        apply.job_id = job.id
        apply.save()
        messages.success(request, 'Apply Successfully')
        return redirect('jobs')
