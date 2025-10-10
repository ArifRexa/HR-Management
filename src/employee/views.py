# white_listed_ips = ['103.180.244.213', '127.0.0.1', '134.209.155.127', '45.248.149.252']
from datetime import datetime
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from config.admin.utils import not_for_management, white_listed_ip_check
from config.context_processors.employees import EmployeeAvailableSlotForm
from config.settings import MACHINE_SECRETS
from employee.forms.appointment_form import AppointmentForm
from employee.forms.employee_need_help import EmployeeNeedHelpForm
from employee.forms.employee_online import EmployeeStatusForm
from employee.forms.employee_project import (
    BookConferenceRoomForm,
    EmployeeProjectForm,
)
from employee.mail import cto_help_mail, hr_help_mail, send_need_help_mails
from employee.models import (
    BookConferenceRoom,
    Config,
    Employee,
    EmployeeNeedHelp,
    EmployeeOnline,
)
from employee.models.employee import Appointment, EmployeeAvailableSlot
from employee.models.employee_activity import EmployeeProject


@white_listed_ip_check
@require_http_methods(["POST", "GET"])
@login_required(login_url="/admin/login/")
@not_for_management
def change_status(request, *args, **kwargs):
    employee_status = EmployeeOnline.objects.get(employee=request.user.employee)

    now = timezone.now().date()

    # feedback = request.user.employee.employeefeedback_set.filter(
    #     created_at__date__year=now.year,
    #     created_at__date__month=now.month,
    # )
    # TODO : feedback should not be applied for Himel vai

    # if not feedback.exists() and now.day > 20:
    #     messages.error(request, "Please provide feedback first")
    #     return redirect("/admin/")

    if request.method == "POST":
        form = EmployeeStatusForm(request.POST, instance=employee_status)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Your status has been change successfully"
            )
            return redirect(request.META.get("HTTP_REFERER"))
        else:
            messages.error(request, "Something went wrong")
            return redirect(request.META.get("HTTP_REFERER"))
    else:
        if employee_status.active:
            employee_status.active = False
            employee_status.save()
        else:
            employee_status.active = True
            employee_status.save()

        messages.success(request, "Your status has been change successfully")
        return redirect("/admin/")


@require_http_methods(["POST"])
@login_required(login_url="/admin/login/")
@not_for_management
def change_project(request, *args, **kwargs):
    employee_project = EmployeeProject.objects.get(
        employee=request.user.employee
    )
    form = EmployeeProjectForm(request.POST, instance=employee_project)
    if form.is_valid():
        form.save()
        messages.success(request, "Your project has been changed successfully")
        return redirect("/admin/")
    else:
        messages.error(request, "Something went wrong")
        return redirect("/admin/")


@require_http_methods(["POST"])
@login_required(login_url="/admin/login/")
@not_for_management
def make_ceo_appoinment(request, *args, **kwargs):
    form = AppointmentForm(request.POST)
    if form.is_valid():
        form.save()
        messages.success(request, "CEO appointment has been booked.")
        return redirect("/admin/")
    else:
        messages.error(request, "Something went wrong")
    return redirect("/admin/")


@require_http_methods(["GET"])
@login_required(login_url="/admin/login/")
@not_for_management
def cancel_ceo_appointment(request, id, *args, **kwargs):
    if id != None:
        Appointment.objects.get(id=id).delete()
        messages.success(request, "CEO appointment has been cancelled.")
        return redirect("/admin/")
    else:
        messages.error(request, "Something went wrong")
    return redirect("/admin/")


@require_http_methods(["POST"])
@login_required(login_url="/admin/login/")
@not_for_management
def change_help_need(request, *args, **kwargs):
    employee_help_need = EmployeeNeedHelp.objects.get(
        employee_id=request.user.employee.id,
    )
    form = EmployeeNeedHelpForm(request.POST, instance=employee_help_need)
    if form.is_valid():
        obj = form.save()

        today = datetime.date.today()
        dayname = today.strftime("%A")
        off_list = ["Saturday", "Sunday"]
        if dayname not in off_list:
            try:
                send_need_help_mails(obj)
            except Exception as e:
                print("Email error, ", e)

        messages.success(
            request, "Your need help statuses updated successfully"
        )
        return redirect("/admin/")
    else:
        messages.error(request, "Something went wrong")
        return redirect("/admin/")


@require_http_methods(["POST", "GET"])
@login_required(login_url="/admin/login/")
@not_for_management
def need_cto_help(request, *args, **kwargs):
    employee = Employee.objects.get(id=request.user.employee.id)
    if request.user.employee.need_cto:
        employee.need_cto = False
        employee.need_cto_at = None
        employee.save()
        messages.success(request, "I got help from Tech Lead. Thank You.")
        return redirect("/admin/")
    else:
        employee.need_cto = True
        employee.need_cto_at = timezone.now()
        employee.save()

        today = datetime.date.today()
        dayname = today.strftime("%A")
        off_list = ["Saturday", "Sunday"]

        if dayname not in off_list:
            print("send email")
            if Config.objects.first().cto_email is not None:
                email_list = Config.objects.first().cto_email.strip()
                email_list = email_list.split(",")
                cto_help_mail(
                    request.user.employee,
                    {"waitting_at": timezone.now(), "receiver": email_list},
                )

        messages.success(
            request,
            "Your request has successfully submited. Tech Lead will contact with you.",
        )
        return redirect("/admin/")


@require_http_methods(["POST", "GET"])
@login_required(login_url="/admin/login/")
@not_for_management
def need_hr_help(request, *args, **kwargs):
    employee = Employee.objects.get(id=request.user.employee.id)
    if request.user.employee.need_hr:
        employee.need_hr = False
        employee.need_hr_at = None
        employee.save()
        messages.success(request, "Got help from HR. Thank You.")
        return redirect("/admin/")
    else:
        employee.need_hr = True
        employee.need_hr_at = timezone.now()
        employee.save()

        today = datetime.date.today()
        dayname = today.strftime("%A")
        off_list = ["Saturday", "Sunday"]

        if dayname not in off_list:
            if Config.objects.first().hr_email is not None:
                email_list = Config.objects.first().hr_email.strip()
                email_list = email_list.split(",")
                hr_help_mail(
                    request.user.employee,
                    {"waiting_at": timezone.now(), "receiver": email_list},
                )

        messages.success(
            request,
            "Your request has successfully submited. HR will contact with you.",
        )
        return redirect("/admin/")


@require_http_methods(["POST", "GET"])
@login_required(login_url="/admin/login/")
def booking_conference_room(request):
    employee = request.user.employee

    if request.method == "POST":
        form = BookConferenceRoomForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.manager_or_lead = employee
            booking.save()
            messages.success(request, "Conference room booked successfully.")
            return redirect("booking_conference_room")
        else:
            start_time = form.cleaned_data.get("start_time", "an invalid time")

            messages.error(
                request,
                f"The time slot {start_time} is already booked. Please schedule a free time between 11:00 AM to 8:00 PM.",
            )

    else:
        form = BookConferenceRoomForm()

    return redirect("/admin/")


@login_required(login_url="/admin/login/")
def delete_booking(request, booking_id):
    try:
        booking = get_object_or_404(BookConferenceRoom, id=booking_id)
        booking.delete()
        messages.success(request, "Booking deleted successfully.")
    except BookConferenceRoom.DoesNotExist:
        messages.error(request, "Booking does not exist.")
    return redirect("/admin/")


@login_required(login_url="/admin/login/")
def update_booking(request, booking_id):
    try:
        booking = BookConferenceRoom.objects.get(id=booking_id)
        if request.method == "POST":
            form = BookConferenceRoomForm(request.POST, instance=booking)
            if form.is_valid():
                form.save()
                messages.success(request, "Booking updated successfully.")
                return redirect("/admin/")
            else:
                start_time = form.cleaned_data.get(
                    "start_time", "an invalid time"
                )
                start_time_formatted = start_time.strftime("%I:%M %p")
                messages.error(
                    request,
                    f"The time slot {start_time_formatted} is already booked. Please schedule a free time between 11:00 AM to 8:00 PM.",
                )

        else:
            form = BookConferenceRoomForm(instance=booking)
        return render(
            request,
            "admin/employee/update_conference_booking.html",
            {"form": form},
        )
    except BookConferenceRoom.DoesNotExist:
        messages.error(request, "Booking does not exist.")
        return redirect("/admin/")


from rest_framework import serializers
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import IsAuthenticated

from employee.models.employee import Task


class TodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"


class EntryPassSerializer(serializers.Serializer):
    mechine_token = serializers.CharField()
    entry_pass_id = serializers.CharField()
    intent = serializers.CharField()
    created_at = serializers.DateTimeField(required=False)


class TodoApiList(ListAPIView):
    serializer_class = TodoSerializer
    queryset = Task.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().filter(created_by=self.request.user)


from rest_framework.response import Response


class ChangeEmployeeEntryPass(CreateAPIView):
    serializer_class = EntryPassSerializer
    queryset = EmployeeOnline.objects.all()
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        mechine_secrets = MACHINE_SECRETS
        data = request.data

        mechine_token = data.get("mechine_token")
        if not mechine_token:
            return Response(
                data={"message": "mechine_token missing"}, status=403
            )

        if not mechine_token == mechine_secrets:
            return Response(data={"message": "Wrong Machine"}, status=403)

        entry_pass_id = data.get("entry_pass_id")
        if not entry_pass_id:
            return Response(
                data={"message": "entry_pass_id missing"}, status=403
            )

        intent = data.get("intent")
        if not intent:
            return Response(data={"message": "intent missing"}, status=403)

        employee = Employee.objects.filter(
            entry_pass_id=str(entry_pass_id)
        ).first()

        if not employee:
            return Response(data={"message": "Employee not found!"}, status=403)

        employee_status = EmployeeOnline.objects.get(employee=employee)
        status = True if intent == "1" else False

        employee_status.active = status
        employee_status.save()
        return Response(data={"message": "Success"}, status=201)


class TodoCreateAPI(CreateAPIView):
    serializer_class = TodoSerializer
    queryset = Task.objects.all()
    permission_classes = [IsAuthenticated]


class TodoRetriveUpdateDeleteAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = TodoSerializer
    queryset = Task.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().filter(created_by=self.request.user)


def employee_project_select_form(request, employee_id):
    employee_project = EmployeeProject.objects.get(employee_id=employee_id)
    context = {
        "show_form": True,
        "employee_project_form": EmployeeProjectForm(instance=employee_project),
    }
    return render(
        request, "admin/form/employee_project_form.html", context=context
    )


# @require_POST
# @login_required
# def save_available_slot(request):
#     """
#     HTMX endpoint:
#     - looks for an existing slot-row for the logged-in employee on the given date
#     - creates or updates that row
#     - returns a small HTML fragment (or JSON) that HTMX can swap into the page
#     """
#     form = EmployeeAvailableSlotForm(request.POST)
#     if not form.is_valid:
#         date_str = request.POST.get("date")
#         try:
#             date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
#         except (ValueError, TypeError):
#             date_obj = datetime.today().date()

#         context = {
#                 "today": date_obj,
#                 "current_slot": request.POST.get("slot"),
#                 "error": form.errors["slot"][0]
#                 if form.errors.get("slot")
#                 else "Invalid choice.",
#                 "toast_message": "somethings wrong",
#                 "toast_type": "error",
#                 "toast": True
#             }
#         response = render(request, "admin/form/available_slot.html", context)
#         response['HX-Refresh'] = 'true'
#         return response

#     slot_value = request.POST["slot"]
#     date_value = timezone.now()

#     should_notify = slot_value in ["half", "full"]

#     existing = (
#         EmployeeAvailableSlot.objects
#         .filter(employee=request.user.employee, date__date=date_value)
#         .last()
#     )

#     created = False
#     if existing:
#         if existing.slot != slot_value:
#             # Slot changed → create new entry (or update, but you prefer new)
#             instance = EmployeeAvailableSlot.objects.create(
#                 employee=request.user.employee,
#                 date=date_value,
#                 slot=slot_value,
#                 available=slot_value != "n/a",
#             )
#             created = True
#         else:
#             instance = existing
#     else:
#         # New entry
#         instance = EmployeeAvailableSlot.objects.create(
#             employee=request.user.employee,
#             date=date_value,
#             slot=slot_value,
#             available=slot_value != "n/a",
#         )
#         created = True

#     # 🔔 Send email only if NEW and slot is half/full
#     if created and should_notify:
#         employee = request.user.employee
#         send_mail(
#             subject=f"New Availability: {employee.user.get_full_name()} is available",
#             message=(
#                 f"Employee: {employee.user.get_full_name()} ({employee.user.email})\n"
#                 f"Designation: {employee.top_one_skill}\n"
#                 f"Date: {date_value}\n"
#                 f"Slot: {slot_value.title()} Time\n\n"
#                 "Please review in the admin panel."
#             ),
#             from_email='"Mediusware-Admin" <hr@mediusware.com>',
#             recipient_list=["mailarif3126@gmail.com"],  # or your team email
#             fail_silently=True,
#         )

#     return render(
#         request,
#         "admin/form/available_slot.html",
#         context={
#             "today": date_value,
#             "current_slot": instance.slot,
#             "toast_message": "successfully add available slot",
#             "toast_type": "success",
#             "toast": True
#         },
#     )






@require_POST
@login_required
def save_available_slot(request):
    """
    HTMX endpoint:
    - looks for an existing slot-row for the logged-in employee on the given date
    - creates or updates that row
    - returns a small HTML fragment (or JSON) that HTMX can swap into the page
    """
    form = EmployeeAvailableSlotForm(request.POST)
    if not form.is_valid:
        date_str = request.POST.get("date")
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            date_obj = datetime.today().date()

        context = {
                "today": date_obj,
                "current_slot": request.POST.get("slot"),
                "error": form.errors["slot"][0]
                if form.errors.get("slot")
                else "Invalid choice.",
                "toast_message": "somethings wrong",
                "toast_type": "error",
                "toast": True
            }
        response = render(request, "admin/form/available_slot.html", context)
        response['HX-Refresh'] = 'true'
        return response

    slot_value = request.POST["slot"]
    date_value = timezone.now()

    should_notify = slot_value in ["half", "full"]

    existing = (
        EmployeeAvailableSlot.objects
        .filter(employee=request.user.employee, date__date=date_value)
        .last()
    )

    created = False
    if existing:
        if existing.slot != slot_value:
            # Slot changed → create new entry (or update, but you prefer new)
            instance = EmployeeAvailableSlot.objects.create(
                employee=request.user.employee,
                date=date_value,
                slot=slot_value,
                available=slot_value != "n/a",
            )
            created = True
        else:
            instance = existing
    else:
        # New entry
        instance = EmployeeAvailableSlot.objects.create(
            employee=request.user.employee,
            date=date_value,
            slot=slot_value,
            available=slot_value != "n/a",
        )
        created = True

    print("*"*100)

    # 🔔 Send email only if it's a NEW "full" or "half" entry
    if created and should_notify:
        try:
            today_date = timezone.now().date()
            # Fetch all available employees for today
            # available_entries = EmployeeAvailableSlot.objects.filter(
            #     date__date=today_date,
            #     slot__in=["full", "half"]
            # ).select_related('employee__user').order_by('-date')

            # Get ALL entries for today, ordered newest first
            all_entries = EmployeeAvailableSlot.objects.filter(
                date__date=today_date,
                slot__in=["full", "half"]  # include "n/a" to catch latest even if now unavailable
            ).select_related('employee__user').order_by('-date')
            # Build a dict: employee_id → latest entry
            latest_per_employee = {}
            for entry in all_entries:
                emp_id = entry.employee_id
                # Only keep the FIRST (newest) entry per employee
                if emp_id not in latest_per_employee:
                    latest_per_employee[emp_id] = entry

            # Now filter: only include if latest slot is "full" or "half"
            available_employees = [
                entry for entry in latest_per_employee.values()
                if entry.slot in ["full", "half"]
            ]

            # Sort by time (newest first) for consistent email order
            available_employees.sort(key=lambda x: x.date, reverse=True)

            employees_data = []
            for entry in available_employees:
                emp = entry.employee
                employees_data.append({
                    "name": emp.user.get_full_name() or emp.user.username,
                    # "email": emp.user.email,
                    "skill": getattr(emp, 'top_one_skill', 'N/A'),
                    "slot": entry.slot.title(),
                    "time": entry.date.strftime("%I:%M %p").lower().replace("am", "a.m.").replace("pm", "p.m.")
                })

            email_context = {
                "date": today_date.strftime("%B %d, %Y"),
                "employees": employees_data,
            }

            html_message = render_to_string("mails/available_employees_table.html", email_context)
            plain_message = strip_tags(html_message)

            send_mail(
                subject=f"Team Availability Update – {today_date.strftime('%B %d, %Y')}",
                message=plain_message,
                from_email='"Mediusware-Admin" <hr@mediusware.com>',
                recipient_list=["mwtanvir98@gmail.com", "rashed@mediusware.com", "hr@mediusware.com"],  # Update as needed
                html_message=html_message,
                fail_silently=False,  # Set to True in production if preferred
            )
        except Exception as e:
            print(f"Failed to send availability email: {e}")
            # Optionally notify user, but usually not needed for background email

    # Prepare context for HTMX response
    today = timezone.now().date()
    available_employees = EmployeeAvailableSlot.objects.filter(
        date__date=today,
        slot__in=["full", "half"]
    ).select_related('employee__user').order_by('-date')

    context = {
        "today": today,
        "current_slot": instance.slot,
        "toast_message": "Successfully updated availability",
        "toast_type": "success",
        "toast": True,
        "available_employees": available_employees,
    }

    return render(request, "admin/form/available_slot.html", context)