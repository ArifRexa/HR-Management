from django.contrib.auth.models import User, Group
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone
from django.utils.timesince import timesince

from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin
from settings.models import Designation, LeaveManagement, PayScale


class Employee(TimeStampMixin, AuthorMixin):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    date_of_birth = models.DateField(null=True, blank=True)
    email = models.EmailField(max_length=255, null=True)
    address = models.TextField(null=True)
    phone = models.CharField(max_length=60, help_text='Use (,) comma for separate phone numbers')
    joining_date = models.DateField(default=timezone.now)
    national_id_no = models.CharField(max_length=20, blank=True, null=True)
    permanent_date = models.DateField(null=True, blank=True)
    designation = models.ForeignKey(Designation, on_delete=models.RESTRICT)
    leave_management = models.ForeignKey(LeaveManagement, on_delete=models.RESTRICT)
    pay_scale = models.ForeignKey(PayScale, on_delete=models.RESTRICT)
    manager = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    def __str__(self):
        bank = self.bankaccount_set.filter(default=True).first()
        return self.full_name

    @property
    def default_bank(self):
        bank = self.bankaccount_set.filter(default=True).first()
        if bank:
            return bank.bank.name
        return ''

    def save(self, *args, **kwargs, ):
        self.save_user()
        super().save(*args, **kwargs)

    def save_user(self):
        name_array = self.full_name.split()
        self.user.is_staff = True
        self.user.first_name = name_array[0]
        self.user.last_name = name_array[1] if len(name_array) > 1 else ''
        self.user.email = self.email
        self.set_in_employee_group()
        if not self.active:
            self.user.is_active = False
        self.user.save()

    def set_in_employee_group(self):
        group = Group.objects.get(name='Employee')
        group.user_set.add(self.user)

    @property
    def joining_date_human(self):
        return timesince(self.joining_date)

    @property
    def permanent_date_human(self):
        return timesince(self.permanent_date)

    def approved_resignation(self):
        return self.resignation_set.filter(status='approved').first()

    @property
    def resignation_date(self):
        is_resigned = self.resignation_set.filter(status='approved').first()
        if is_resigned:
            return is_resigned.date
        return None

    @property
    def current_salary(self):
        return self.salaryhistory_set.latest('id')

    @property
    def joining_salary(self):
        return self.salaryhistory_set.first()

    @property
    def permanent_salary(self):
        salary = self.salaryhistory_set.filter(active_from=self.permanent_date).first()
        if salary:
            return salary
        return self.current_salary

    class Meta:
        db_table = 'employees'
