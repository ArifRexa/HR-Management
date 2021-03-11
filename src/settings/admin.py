from django.contrib import admin

# Register your models here.
from .models import Designation, PayScale, Leave

admin.site.register(Designation)
admin.site.register(PayScale)
admin.site.register(Leave)
