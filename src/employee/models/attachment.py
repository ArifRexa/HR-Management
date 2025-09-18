import os

from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.text import slugify

from account.models import get_current_financial_year
from config.model.AuthorMixin import AuthorMixin
from config.model.TimeStampMixin import TimeStampMixin
from employee.models import Employee
from settings.models import FinancialYear


def user_directory_path(instance, filename):
    username = instance.employee.user.username
    filename = get_file_name(instance.file_name, filename)
    return f"hr/employee/{username}/{filename}"


class DocumentName(models.Model):
    name = models.CharField(max_length=155, unique=True)

    def __str__(self):
        return self.name


class Attachment(TimeStampMixin, AuthorMixin):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    # file_name = models.CharField(null=True, blank=True, max_length=155)
    
    file_name = models.ForeignKey(
        DocumentName,
        on_delete=models.SET_NULL,
        null=True,
        to_field="name",
        related_name="attachment",
    )
    file = models.FileField(
        help_text="*.pdf, *.doc, *.png, *.jpeg",
        upload_to=user_directory_path,
        validators=[
            FileExtensionValidator(
                allowed_extensions=["pdf", "doc", "png", "jpeg", "jpg"]
            )
        ],
    )
    tds_year = models.ForeignKey(
        FinancialYear,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="TDS Year",
        help_text="Use for Tax Acknowledgement Document",
    )


def get_file_name(given_name, filename):
    file_extension = os.path.basename(filename).split(".")[-1]
    if given_name:
        return slugify(given_name) + "." + file_extension
    return filename


class EmployeeTaxAcknowledgement(Attachment):
    
    class Meta:
        proxy = True
        verbose_name = "Tax Acknowledgement"
        verbose_name_plural = "Tax Acknowledgements"
        permissions = (("view_all_tax_acknowledgement", "View All Tax Acknowledgement"),)
