from django.db import models
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.utils import timezone

from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin
from employee.models import Employee


class Unit(AuthorMixin, TimeStampMixin):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class Product(AuthorMixin, TimeStampMixin):
    title = models.CharField(max_length=255)
    unit = models.ForeignKey(Unit, on_delete=models.RESTRICT)

    def __str__(self):
        return self.title

    @property
    def current_stock(self):
        total_in = self.stock_set.filter(type__exact='in').aggregate(score=Coalesce(Sum('quantity'), 0.0))['score']
        total_out = self.stock_set.filter(type__exact='out').aggregate(score=Coalesce(Sum('quantity'), 0.0))['score']
        return total_in - total_out


class Stock(AuthorMixin, TimeStampMixin):
    TYPE_CHOICE = (
        ('in', 'Stock In'),
        ('out', 'Stock Out')
    )
    employee = models.ForeignKey(Employee, on_delete=models.RESTRICT, limit_choices_to={'active': True}, null=True,
                                 blank=True, related_name='stocks')
    product = models.ForeignKey(Product, on_delete=models.RESTRICT)
    quantity = models.FloatField()
    date = models.DateField(default=timezone.now)
    type = models.CharField(max_length=10, choices=TYPE_CHOICE)
    note = models.TextField(blank=True, null=True)
