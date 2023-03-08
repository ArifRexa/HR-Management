import uuid

import datetime
from dateutil.relativedelta import relativedelta

from django.contrib.auth.models import User, Group
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.text import slugify
from django.utils.timesince import timesince
from tinymce.models import HTMLField

from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin
from settings.models import Designation, LeaveManagement, PayScale


class Employee(TimeStampMixin, AuthorMixin):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(null=True, blank=True)
    full_name = models.CharField(max_length=255)
    slug = models.SlugField(null=True, blank=True, unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    blood_group = models.CharField(max_length=20, null=True, blank=True)
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
    show_in_web = models.BooleanField(default=True)
    lunch_allowance = models.BooleanField(default=True)
    project_eligibility = models.BooleanField(default=True)
    leave_in_cash_eligibility = models.BooleanField(default=True)
    show_in_attendance_list = models.BooleanField(default=True)
    pf_eligibility = models.BooleanField(default=True)
    list_order = models.IntegerField(default=100)

    birthday_image = models.ImageField(null=True, blank=True)
    birthday_image_shown = models.BooleanField(default=False)

    def __str__(self):
        bank = self.bankaccount_set.filter(default=True).first()
        return self.full_name

    @property
    def top_skills(self):
        skills = self.employeeskill_set.order_by('-percentage').all()
        return skills[:4]

    @property
    def is_online(self):
        from employee.models.employee_activity import EmployeeOnline
        return EmployeeOnline.objects.filter(employee__active=True, employee__id=self.id).values_list('active', flat=True).first()

    @property
    def employee_project_list(self):
        from employee.models.employee_activity import EmployeeProject
        return EmployeeProject.objects.filter(employee_id=self.id).first().project.all().values('title')

    @property
    def top_one_skill(self):
        return self.employeeskill_set.order_by('-percentage').first()

    @property
    def default_bank(self):
        bank = self.bankaccount_set.filter(default=True).first()
        if bank:
            return bank.bank.name
        return ''
    
    @property
    def last_x_months_feedback(self):
        current_month = datetime.datetime.today()
        last_x_months = current_month + relativedelta(months=-6)
        return self.employeefeedback_set.filter(
            created_at__lte=current_month,
            created_at__gte=last_x_months,
        ).order_by("-created_at").exclude(employee__active=False)

    def save(self, *args, **kwargs, ):
        self.save_user()
        if not self.slug:
            self.slug = f'{slugify(self.full_name)}-{self.email}'
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

    def set_daily_hours(self, value):
        self.daily_project_hours = value
    
    def leave_passed(self, leave_type: str, year=timezone.datetime.now().year):
        return self.leave_set.filter(
            end_date__year=year,
            leave_type=leave_type,
            status='approved'
        ).aggregate(total=Coalesce(Sum('total_leave'), 0.0))['total']

    def leave_available_leaveincash(self, leave_type: str, year_end=timezone.now().replace(month=12, day=31).date()):
        available_leave = 0
        get_leave_by_type = getattr(self.leave_management, leave_type)
        
        if self.leave_in_cash_eligibility and self.permanent_date:
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


    def leave_available(self, leave_type: str, year_end=timezone.now().replace(month=12, day=31).date()):
        available_leave = 0
        get_leave_by_type = getattr(self.leave_management, leave_type)

        # Renamed for leave calculation
        # TODO: Need to upgrade calculation style without temporary fix
        permanent_date = self.joining_date
        
        if self.leave_in_cash_eligibility:
            if self.resignation_date:
                total_days_of_permanent = (self.resignation_date - permanent_date).days
            else:
                total_days_of_permanent = (year_end - permanent_date).days
            
            month_of_permanent = round(total_days_of_permanent / 30)
            if month_of_permanent < 12:
                available_leave = (month_of_permanent * get_leave_by_type) / 12
            else:
                available_leave = get_leave_by_type
        
        return round(available_leave)

    class Meta:
        db_table = 'employees'


@receiver(post_save, sender=Employee, dispatch_uid="create_employee_lunch")
def create_employee_lunch(sender, instance, **kwargs):
    if instance.pf_eligibility:
        now = timezone.now().date().replace(day=1)
        maturity_date = now + relativedelta(years=2)
        from provident_fund.models import Account
        Account.objects.get_or_create(
            employee=instance,
            defaults= {
                'start_date': now,
                'maturity_date': maturity_date,
                'scale': 10.0,
            }
        )

    from employee.models.employee_activity import EmployeeOnline, EmployeeProject
    EmployeeLunch.objects.update_or_create(employee=instance)
    EmployeeOnline.objects.get_or_create(employee=instance)
    EmployeeProject.objects.update_or_create(employee=instance)


class EmployeeLunch(TimeStampMixin):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)

    class Meta:
        permissions = (
            ("can_see_all_lunch", "Can able to see all lunch"),
        )
        verbose_name = 'Employee detail'
        verbose_name_plural = 'Employee details'


class PrayerInfo(AuthorMixin, TimeStampMixin):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    num_of_waqt_done = models.IntegerField(default=0)
    
    waqt_fajr = models.BooleanField(default=False)
    waqt_zuhr = models.BooleanField(default=False)
    waqt_asr = models.BooleanField(default=False)
    waqt_maghrib = models.BooleanField(default=False)
    waqt_isha = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        self.num_of_waqt_done = self.waqt_fajr \
                                + self.waqt_zuhr \
                                + self.waqt_asr \
                                + self.waqt_maghrib \
                                + self.waqt_isha
        
        return super(PrayerInfo, self).save(*args, **kwargs)
