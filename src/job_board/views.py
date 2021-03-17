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
        data = {
            'job': job,
            'job_form': job_form,
        }
        return render(request, 'job/job-apply.html', data)

    def post(self, request, id):
        job = get_object_or_404(Job, pk=id)
        print(request.POST.keys()['job_applys'])
        return HttpResponse(request.POST.keys()['job_applys'])
        form = JobApplyForm(request.POST or None)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.job = job
            instance.data = "data"
            instance.save()

        # dict_data = json.loads(data)
        # for dic_single in dict_data:
        #     print(dic_single)
        # return HttpResponse(request.FILES.get('job_applys[file]'))
        # for key, ob in request.POST:
        #     print(key)
        #     print(ob)

        # uploaded_file = request.FILES['file']
        # fs = FileSystemStorage()
        # name = fs.save(uploaded_file.name, uploaded_file)

        data = {
            'job': job,
        }
        messages.success(request, 'Apply Successfully')
        return render(request, 'job/job-apply.html', data)
