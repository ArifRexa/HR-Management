from django.contrib.auth.models import User, Group
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models import Sum
from django.db.models.functions import Coalesce
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
    tax_info = models.CharField(null=True, blank=True, max_length=255,
                                help_text='i.e: 59530389237, Circle–138, Zone-11, Dhaka')
    manager = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    def __str__(self):
        bank = self.bankaccount_set.filter(default=True).first()
        return self.full_name

    @property
    def top_skills(self):
        skills = self.employeeskill_set.order_by('-percentage').all()
        return skills

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

    def leave_passed(self, leave_type: str, year=timezone.datetime.now().year):
        return self.leave_set.filter(
            end_date__year=year,
            leave_type=leave_type,
            status='approved'
        ).aggregate(total=Coalesce(Sum('total_leave'), 0.0))['total']

    def leave_available(self, leave_type: str, year_end=timezone.now().replace(month=12, day=31).date()):
        available_leave = 0
        get_leave_by_type = getattr(self.leave_management, leave_type)
        if self.permanent_date:
            if self.resignation_date:
                total_days_of_permanent = (self.resignation_date - self.permanent_date).days
            else:
                total_days_of_permanent = (year_end - self.permanent_date).days
            month_of_permanent = round(total_days_of_permanent / 30)
            if month_of_permanent < 12:
                available_leave = (month_of_permanent * get_leave_by_type) / 12
            else:
                available_leave = get_leave_by_type
        return round(available_leave)

    class Meta:
        db_table = 'employees'
