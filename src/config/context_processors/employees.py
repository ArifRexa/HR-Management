from datetime import date, datetime, time, timedelta

from django import forms
from django.contrib.auth.models import AnonymousUser
from django.db.models import (
    BooleanField,
    Case,
    Count,
    F,
    Min,
    OuterRef,
    Prefetch,
    Q,
    Subquery,
    Sum,
    Value,
    When,
)
from django.utils import timezone
from django.utils.html import format_html

from config.settings import employee_ids as management_ids
from employee.admin.employee.extra_url.formal_view import EmployeeNearbySummery
from employee.forms.employee_need_help import EmployeeNeedHelpForm
from employee.forms.employee_online import EmployeeStatusForm
from employee.forms.employee_project import (
    BookConferenceRoomForm,
    EmployeeProjectForm,
)
from employee.models import (
    Employee,
    EmployeeNeedHelp,
    EmployeeOnline,
    EmployeeSkill,
    FavouriteMenu,
    Leave,
    LeaveManagement,
)
from employee.models.employee import (
    BookConferenceRoom,
    EmployeeAvailableSlot,
    Inbox,
    LateAttendanceFine,
)
from employee.models.employee_activity import EmployeeProject
from employee.models.employee_feedback import EmployeeFeedback
from project_management.models import DailyProjectUpdate, Project
from settings.models import Announcement, Notice


def formal_summery(request):
    if not request.path == "/admin/":
        return {}
    if not request.user.is_authenticated:
        return {}

    employee = request.user.employee

    employee_formal_summery = EmployeeNearbySummery()

    leaves_nearby, leaves_nearby_count = (
        employee_formal_summery.employee_leave_nearby()
    )
    permanents, permanents_count = employee_formal_summery.permanents()
    anniversaries, anniversaries_count = employee_formal_summery.anniversaries()

    employee_online = (
        EmployeeOnline.objects.filter(
            employee__active=True,
        )
        .order_by(
            "-employee__need_cto",
            "-employee__need_hr",
            "active",
            "employee__full_name",
        )
        .exclude(
            employee_id__in=management_ids,
        )
        .select_related(
            "employee",
        )
    )
    best_skill_qs = (
        EmployeeSkill.objects.filter(employee_id=OuterRef("employee_id"))
        .order_by("-percentage")
        .values("skill__title")[:1]
    )
    employee_filter = Q(employee__active=True) & Q(
        employee__project_eligibility=True
    )
    if not employee.operation and not employee.is_tpm:
        employee_filter &= Q(employee=employee)
    employee_projects = (
        EmployeeProject.objects.filter(employee_filter)
        .exclude(employee_id__in=management_ids)
        .annotate(
            project_count=Count("project"),
            project_order=Min("project"),
            project_exists=Case(
                When(project_count=0, then=Value(False)),
                default=Value(True),
                output_field=BooleanField(),
            ),
            is_online=F("employee__employeeonline__active"),
            employee_skill=Subquery(best_skill_qs),
        )
        .order_by(
            "project_exists",
            "employee__full_name",
        )
        .select_related(
            "employee",
        )
        .prefetch_related(
            Prefetch(
                "employee__employeeskill_set",
                queryset=EmployeeSkill.objects.order_by("-percentage"),
            ),
            Prefetch("employee__employeeskill_set__skill"),
            Prefetch(
                "project",
                queryset=Project.objects.filter(active=True),
            ),
        )
    )

    order_keys = {
        "1": "employee__full_name",
        "-1": "-employee__full_name",
        "2": "project_order",
        "-2": "-project_order",
    }

    order_by = request.GET.get("ord", None)
    if order_by:
        order_by_list = ["project_exists", order_keys.get(order_by, "1")]
        if order_by not in ["1", "-1"]:
            order_by_list.append("employee__full_name")

        employee_projects = employee_projects.order_by(*order_by_list)

    current_month_feedback_done = True
    if str(employee.id) not in management_ids:
        current_month_feedback_done = EmployeeFeedback.objects.filter(
            employee_id=employee.id,
            created_at__date__month=timezone.now().date().month,
        ).exists()

    return {
        "leaves": leaves_nearby,
        "leaves_count": leaves_nearby_count,
        "employee_online": employee_online,
        "employee_projects": employee_projects,
        "ord": order_by,
        "current_month_feedback_done": current_month_feedback_done,
        "announcement": get_announcement(request=request),
        "birthday_today": get_managed_birthday_image(request),
        "increments": employee_formal_summery.increments,
        "permanents": permanents,
        "permanents_count": permanents_count,
        "anniversaries": anniversaries,
        "anniversaries_count": anniversaries_count,
        "is_management": str(employee.id) in management_ids,
        # TODO: Need Optimization
        "birthdays": employee_formal_summery.birthdays,
        "new_employees": employee_formal_summery.new_employee,
        "new_lead_or_managers": employee_formal_summery.new_lead_or_manager,
    }


def total_attendance_fine(request):
    if not request.path == "/admin/":
        return {}
    if not request.user.is_authenticated:
        return ""
    obj = request.user.employee
    current_date = datetime.now()
    current_month = current_date.month
    last_month = current_date.month - 1
    current_year = current_date.year
    current_late_fine = LateAttendanceFine.objects.filter(
        employee=obj, month=current_month, year=current_year
    ).aggregate(fine=Sum("total_late_attendance_fine"))
    last_late_fine = LateAttendanceFine.objects.filter(
        employee=obj, month=last_month, year=current_year
    ).aggregate(fine=Sum("total_late_attendance_fine"))
    current_fine = (
        current_late_fine.get("fine", 0.00)
        if current_late_fine.get("fine")
        else 0.00
    )
    last_fine = (
        last_late_fine.get("fine", 0.00) if last_late_fine.get("fine") else 0.00
    )

    last_month_date = current_date + timedelta(days=-30)
    html = f"{current_fine} ( {current_date.strftime('%b')} )  </br>{last_fine} ( {last_month_date.strftime('%b')} ) "
    is_super = request.user.is_superuser
    return {"is_super": is_super, "late_attendance_fine": format_html(html)}


def total_late_entry_count(request):
    if not request.user.is_authenticated:
        current_date = timezone.now()
        current_month_name = current_date.strftime("%b").lower()
        last_month_date = current_date - timedelta(days=30)
        last_month_name = last_month_date.strftime("%b").lower()
        html = f"<div class='text-start'>0 ({current_month_name})<br>0 ({last_month_name})<div>"
        return {"is_super": False, "late_attendance_count": format_html(html)}

    obj = getattr(request.user, "employee", None)
    current_date = timezone.now()
    current_month = current_date.month
    last_month = current_date.month - 1 or 12
    current_year = current_date.year
    last_year = current_year if last_month != 12 else current_year - 1

    current_month_name = current_date.strftime("%b").lower()
    last_month_date = current_date - timedelta(days=30)
    last_month_name = last_month_date.strftime("%b").lower()

    if not obj:
        html = f"0 ({current_month_name})<br>0 ({last_month_name})"
    else:
        current_late_count = LateAttendanceFine.objects.filter(
            employee=obj, month=current_month, year=current_year
        ).count()
        last_late_count = LateAttendanceFine.objects.filter(
            employee=obj, month=last_month, year=last_year
        ).count()
        html = f"{current_late_count} ({current_month_name})<br>{last_late_count} ({last_month_name})"

    is_super = request.user.is_superuser
    return {"is_super": is_super, "late_attendance_count": format_html(html)}


def employee_status_form(request):
    if not request.path == "/admin/":
        return {"status_form": None}
    if (
        request.user.is_authenticated
        and str(request.user.employee.id) not in management_ids
    ):
        employee_online = EmployeeOnline.objects.get(
            employee_id=request.user.employee.id
        )
        return {"status_form": EmployeeStatusForm(instance=employee_online)}
    else:
        return {"status_form": None}


def employee_project_form(request):
    if not request.path == "/admin/":
        return {"employee_project_form": None}
    if (
        request.user.is_authenticated
        and str(request.user.employee.id) not in management_ids
    ):
        employee_project = EmployeeProject.objects.get(
            employee_id=request.user.employee.id
        )
        return {
            "employee_project_form": EmployeeProjectForm(
                instance=employee_project
            )
        }
    else:
        return {"employee_project_form": None}


def employee_need_help_form(request):
    if not request.path == "/admin/":
        return {"employee_need_help_form": None}
    if (
        request.user.is_authenticated
        and str(request.user.employee.id) not in management_ids
    ):
        employee_need_help, _ = EmployeeNeedHelp.objects.get_or_create(
            employee_id=request.user.employee.id,
        )
        return {
            "employee_need_help_form": EmployeeNeedHelpForm(
                instance=employee_need_help
            )
        }
    else:
        return {"employee_need_help_form": None}


def unread_inbox(request):
    if not request.path == "/admin/":
        return {}
    if not request.user.is_authenticated:
        return {}
    if not request.user.has_perm("employee.can_see_all_employee_inbox"):
        qs = Inbox.objects.filter(
            employee=request.user.employee, is_read=False
        ).count()
        return {"unread_inbox_count": qs}
    return {}


def all_notices(request):
    if not request.path == "/admin/":
        return {"notices": []}
    return {
        "notices": Notice.objects.filter(
            start_date__lte=timezone.now(), end_date__gte=timezone.now()
        ).order_by("-rank", "-created_at")
    }


def get_announcement(request):
    if not request.path == "/admin/":
        return []
    data = []
    now = timezone.now()

    # Get Announcements
    announcements = (
        Announcement.objects.filter(
            is_active=True,
            start_datetime__lte=now,
            end_datetime__gte=now,
        )
        .order_by(
            "-updated_at",
            "-rank",
        )
        .values_list("description", flat=True)
    )

    # need_help_positions = (
    #     NeedHelpPosition.objects.filter(
    #         employeeneedhelp__employee__active=True,
    #     )
    #     .distinct()
    #     .order_by("id")
    # )
    # for need_help_position in need_help_positions:
    #     title = need_help_position.title
    #     names = list(
    #         need_help_position.employeeneedhelp_set.values_list(
    #             "employee__full_name",
    #             flat=True,
    #         )
    #     )
    #     if names and (
    #         title != "CEO"
    #         or (
    #             title == "CEO"
    #             and request.user.employee.id == 30  # Employee ID must be 30
    #         )
    #     ):
    #         names_str = ", ".join(names)
    #         data.append(
    #             f"{names_str} need{'s' if len(names)==1 else ''} the {title}'s help."
    #         )

    # Announcements
    data.extend(announcements)

    # Get Leaves
    leaves_today = (
        Leave.objects.filter(
            employee__active=True,
            start_date__lte=now,
            end_date__gte=now,
        )
        .exclude(
            status="rejected",
        )
        .select_related(
            "employee",
        )
    )
    if leaves_today.exists():
        approved_leaves = Leave.objects.filter(status="Approved")
        count = approved_leaves.count()
        for i in range(0, count):
            today_date = datetime.now().date()
            if today_date == approved_leaves[i].start_date:
                data.extend(
                    [
                        f"{approved_leaves[i].employee.full_name} is on {approved_leaves[i].leave_type} leave today."
                    ]
                )

    # # Get Home Offices
    # home_offices_today = (
    #     HomeOffice.objects.filter(
    #         employee__active=True,
    #         start_date__lte=now,
    #         end_date__gte=now,
    #     )
    #     .exclude(
    #         status="rejected",
    #     )
    #     .select_related(
    #         "employee",
    #     )
    # )
    # if home_offices_today.exists():
    #     homeoffices = [
    #         homeoffice.employee.full_name for homeoffice in home_offices_today
    #     ]
    #     data.extend(
    #         [f"{homeoffice} is on Home Office today." for homeoffice in homeoffices]
    #     )

    # Get Birthdays
    birthdays_today = Employee.objects.filter(
        active=True,
        date_of_birth__day=now.date().day,
        date_of_birth__month=now.date().month,
    ).values_list("full_name", flat=True)
    if birthdays_today:
        birthdays_text = ", ".join(birthdays_today)
        data.append(
            f"{birthdays_text} {'has' if len(birthdays_today) == 1 else 'have'} birthday today."
        )

    # Format Data
    if data:
        initial = f'<span style="background-color:tomato;padding:0.4rem 0.8rem;border-radius:0.4rem;">ANNOUNCEMENTS</span> {"&nbsp;" * 8}🚨'
        data = initial + f" {'&nbsp;' * 8}🚨".join(
            [f'<span class="single_announcement">{d}</span>' for d in data]
        )
        data = format_html(data)

    return data if data else None


def get_managed_birthday_image(request):
    if not request.path == "/admin/":
        return False
    path = request.get_full_path()
    if not path == "/admin/":
        return False

    if isinstance(request.user, AnonymousUser):
        birthday = False
    else:
        birthday = False
        if request.user.employee.date_of_birth == datetime.today().date():
            if not request.user.employee.birthday_image_shown:
                try:
                    birthday = request.user.employee.birthday_image.url
                except:
                    birthday = False
                Employee.objects.filter(user=request.user).update(
                    birthday_image_shown=True
                )
            else:
                Employee.objects.filter(user=request.user).update(
                    birthday_image_shown=False
                )
    return birthday


def favourite_menu_list(request):
    if request.user.is_authenticated and request.user.employee is not None:
        f_menu = FavouriteMenu.objects.filter(
            employee_id=request.user.employee.id
        )
        data = {}
        data["object_list"] = f_menu
        return data
    return []


def project_lists(request):
    if not request.path == "/admin/":
        return []
    if request.user.is_authenticated:
        data = {}
        data["active_projects"] = Project.objects.filter(active=True)
        return data
    return []


from django.core.cache import cache
from django.utils.functional import SimpleLazyObject


def bookings_processor(request):
    def get_bookings():
        today = date.today()
        start = datetime.combine(today, time.min)
        end = datetime.combine(today, time.max)
        bookings = (
            BookConferenceRoom.objects.filter(created_at__range=(start, end))
            .select_related("project_name", "manager_or_lead")
            .order_by("start_time")
            .only("manager_or_lead", "project_name", "start_time")
        )
        return bookings

    return {"conference_room_bookings": SimpleLazyObject(get_bookings)}


def conference_room_bookings(request):
    return bookings_processor(request)


def conference_room_bookings_form(request):
    form = BookConferenceRoomForm

    # Return the form in a dictionary
    return {"my_form": form}


def employee_context_processor(request):
    if not request.path == "/admin/":
        return {}
    if request.user.is_authenticated:
        try:
            employee = Employee.objects.get(user=request.user)
        except Employee.DoesNotExist:
            employee = None

        if employee:
            is_manager = employee.manager
            is_lead = employee.lead
            is_sqa = employee.sqa

        else:
            is_manager = False
            is_lead = False
            is_sqa = False

    else:
        employee = None
        is_manager = False
        is_lead = False
        is_sqa = False

    return {
        "employee": employee,
        "is_manager": is_manager,
        "is_lead": is_lead,
        "is_sqa": is_sqa,
    }


def employee_project_list(request):
    print("project list")
    if not request.path == "/admin/":
        return {"employee_project_list": None}

    if not request.user.is_authenticated:
        return {"employee_project_list": None}

    def _get_projects():
        user = request.user
        key = f"employee_projects_{user.id}_{date.today().isoformat()}"
        proj = cache.get(key)
        if proj is None:
            try:
                if user.employee.operation:
                    emp = (
                        Employee.objects.filter(user=user)
                        .select_related("user")
                        .prefetch_related(
                            # "employeeproject_set__project",
                            Prefetch(
                                "employeeproject__project",
                                queryset=Project.objects.all(),
                                to_attr="project_list",
                            )
                        )
                    )
                else:
                    emp = Employee.objects.select_related(
                        "user"
                    ).prefetch_related(
                        # "employeeproject_set__project",
                        Prefetch(
                            "employeeproject__project",
                            queryset=Project.objects.all(),
                            to_attr="project_list",
                        )
                    )
                p = getattr(emp.get(user=user), "project_list", [])
                print(p)
                emp = emp.get(user=user)
                proj = list(
                    emp.employee_project_list.values_list("title", flat=True)
                )
            except Employee.DoesNotExist:
                print(f"Employee not found for user {user.id}")
                proj = []
            cache.set(key, proj, timeout=86400)
        return proj

    return {"employee_project_list": SimpleLazyObject(_get_projects)}


def approval_info_leave_daily_update(request):
    if not request.path == "/admin/":
        return {}
    if not request.user.is_authenticated:
        return ""  # Return empty response if user is not authenticated

    pending_leave = LeaveManagement.objects.filter(
        status="pending", manager=request.user.employee
    ).count()
    daily_update_pending = DailyProjectUpdate.objects.filter(
        status="pending", manager=request.user.employee
    ).count()

    # Determine if counts are greater than 0 to apply style
    leave_color = "red" if pending_leave > 0 else "green"
    update_color = "red" if daily_update_pending > 0 else "green"

    # Create HTML string with conditional styles
    leave_html = f'<span style="color: {leave_color};"> Leave Approval: {pending_leave}</span>'
    update_html = f'<span style="color: {update_color};"> Daily Update: {daily_update_pending}</span>'
    html = f"   {leave_html}<br/>   {update_html}"

    # Query to check if the user is manager, lead, or TPM
    is_manager_lead_tpm = Employee.objects.filter(
        Q(user=request.user, manager=True)
        | Q(user=request.user, lead=True)
        | Q(user=request.user, is_tpm=True)
    ).exists()

    return {
        "approval_info_leave_daily_update": format_html(html),
        "is_manager_lead_tpm": is_manager_lead_tpm,
    }


def last_four_week_project_hour(request):
    if not request.path == "/admin/":
        return {}
    if not request.user.is_authenticated:
        return ""

    employee = request.user.employee
    monthly_expected_hours = int(employee.monthly_expected_hours or 0)
    weekly_expected_hours = int(monthly_expected_hours / 4)

    return {
        "weekly_expected_hours": weekly_expected_hours,
        "monthly_expected_hours": monthly_expected_hours,
    }


def can_show_permanent_increment(reqeust):
    can_show = False
    if reqeust.user.has_perm("employee.can_show_permanent_increment"):
        can_show = True
    return {"can_show_permanent_increment": can_show}


# forms.py
class EmployeeAvailableSlotForm(forms.ModelForm):
    date = forms.DateField(widget=forms.HiddenInput())

    class Meta:
        model = EmployeeAvailableSlot
        fields = ["slot", "date"]


def available_slot_form(request):
    form = EmployeeAvailableSlotForm()
    if request.user.is_authenticated:
        current_slot = EmployeeAvailableSlot.objects.filter(
            employee=request.user.employee
        ).last()
    else:
        current_slot = None
    # Return the form in a dictionary
    return {
        "slot_form": form,
        "today": timezone.now().date(),
        "current_slot": current_slot.slot if current_slot else None,
    }


from django.db.models import Max


def all_employees_last_slot(request):
    """
    Active employees + their latest slot choice (Half/Full/N/A).
    MySQL 5.x compatible.
    """
    # 1. latest slot id per employee
    today = timezone.now().date()
    latest_ids = (
        EmployeeAvailableSlot.objects.filter(date__date=today).exclude(slot="n/a").values("employee")
        .annotate(max_id=Max("id"))
        .values_list("max_id", flat=True)
    )

    # 2. fetch only those rows
    slots = {
        s.employee_id: s.get_slot_display()  # 'Half Time' / 'Full Time' / 'N/A'
        for s in EmployeeAvailableSlot.objects.filter(id__in=latest_ids)
    }

    # 3. attach to active employees
    employees = Employee.objects.filter(active=True).order_by("full_name")
    available_employee = []
    for emp in employees:
        if slots.get(emp.id, None):
            emp.slot_label = slots.get(emp.id, "—")
            available_employee.append(emp)

    return {"all_employees_last_slot": available_employee}
