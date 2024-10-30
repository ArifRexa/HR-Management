from tabnanny import verbose
from django.db import models

from config.model.TimeStampMixin import TimeStampMixin
from employee.models.employee import Employee
from django.db.models import Q

class Agenda(models.Model):
    name = models.CharField(max_length=255,null=True,blank=True)
    
    def __str__(self):
        return self.name
    
# Create your models here.
class Reception(TimeStampMixin):
    AGENDA_CHOICE = [
        ('interview','Interview'),
        ('meeting','Meeting'),
        ('others','Others')
    ]
    STATUS_CHOICE = (("pending", "⌛ Pending"), ("approved", "✔ Approved"))
    
    name = models.CharField(max_length=255)
    comment = models.TextField(null=True,blank=True)
    agenda_name = models.ForeignKey(Agenda,on_delete=models.SET_NULL,null=True,blank=True,verbose_name='Agenda')
    status = models.CharField(max_length=10, choices=STATUS_CHOICE, default='pending',null=True,blank=True)
    approved_by = models.CharField(max_length=200,null=True,blank=True)
    def __str__(self):
        return f'{self.name} - {self.agenda_name}'

class Token(models.Model):
    unique_url = models.CharField(max_length=255, unique=True)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Token {self.unique_url} (Used: {self.is_used})'
    

class CEOWaitingList(TimeStampMixin):
    STATUS_CHOICE = (("pending", "⌛ Pending"), ("approved", "✔ Approved"))
    
    name = models.ForeignKey(Employee,on_delete=models.CASCADE,limit_choices_to=Q(active=True))
    status = models.CharField(max_length=10, choices=STATUS_CHOICE, default='pending',null=True,blank=True)

    
    def __str__(self):
        return f'{self.name}'
    
    class Meta:
        verbose_name_plural = 'CEO Waiting List'


class CEOStatus(TimeStampMixin):
    status_name = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = 'CEO Status'

class CEOCurrentStatus(TimeStampMixin):
    current_status = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = 'CEO Current Status'

    def __str__(self):
        return self.current_status