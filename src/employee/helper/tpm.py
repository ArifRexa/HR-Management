from __future__ import annotations
import typing as t
from django.db.models import Manager
from datetime import datetime, timedelta
from dataclasses import dataclass
from dataclasses import field
from employee.forms import employee_online
from employee.models import (
    Employee,
)
from employee.models.employee import (
    EmployeeUnderTPM,
)
from project_management.models import Project
from project_management.models import Client
from project_management.models import ProjectHour

from django.db.models import Sum
from django.db.models.functions import TruncWeek


WORKING_DAYS_IN_A_WEEK = 5


def _get_date_range_by_week(week=0, days=7):
    """
    week: int
        1 (next week)
        0 (current week)
        -1 (last week)
        -2 (2nd last week)
    days: int
        The number of days in the range (default is 7 for a full week).
    """
    now = datetime.now()
    # Calculate the current week's start (Monday)
    current_week_start = now - timedelta(days=now.weekday())  # Monday of the current week
    # Calculate the target week's start by adding `week` offset
    target_week_start = current_week_start + timedelta(weeks=week)
    # Define the end date for the range
    end_date = target_week_start + timedelta(days=days - 1)
    return target_week_start.date(), end_date.date()


@dataclass
class TPMObj:
    tpm: Employee
    last_week_date_range: t.List[t.Tuple[t.Optional[datetime]]] = field(
        default_factory=lambda: [(None, None)] * 4, init=False
    )
    last_week_hours: t.List[float] = field(
        default_factory=lambda: [0.0] * 4, init=False
    )

    employees: t.List[Employee] = field(default_factory=list, init=False)
    projects: t.List[Project] = field(default_factory=list, init=False)
    last_four_project_hours: t.Dict[int, t.List[float]] = field(
        default_factory=dict, init=False
    )
    clients: t.List[Client] = field(default_factory=list, init=False)

    _employee_ids: t.List[int] = field(default_factory=list, init=False)
    _project_ids: t.List[int] = field(default_factory=list, init=False)

    __employee_hash: t.Dict[int, Employee] = field(
        default_factory=dict, init=False, repr=False
    )
    __project_hash: t.Dict[int, Project] = field(
        default_factory=dict, init=False, repr=False
    )
    __client_hash: t.Dict[int, Client] = field(
        default_factory=dict, init=False, repr=False
    )
    __cached_employee_hours_qs: t.Optional[Manager[ProjectHour]] = field(
        default=None, init=False, repr=False
    )

    @property
    def tpm_expected_hour(self):
        total = 0
        for i in self.employees:
            total += i.monthly_expected_hours or 0
        return total

    @property
    def get_weekly_expected_hour(self):
        return self.tpm_expected_hour / 4

    def add_employee(self, data: Employee):
        # FIXME: Add this if needed for null employee and project
        if not data:
            return
        employee_id = data.pk
        if employee_id in self.__employee_hash:
            return

        self.__cached_employee_hours_qs = None
        self._employee_ids.append(employee_id)
        self.__employee_hash[employee_id] = data
        self.employees.append(data)

        self.employees.sort(key=lambda e: e.monthly_expected_hours or 0, reverse=True)

    def add_project(self, data: Project):
        project_id = data.pk
        if project_id in self.__project_hash:
            return

        self.__cached_employee_hours_qs = None
        self._project_ids.append(project_id)
        self.__project_hash[project_id] = data
        self.projects.append(data)

    def add_project_hours(self):
        for project in self.projects:
            # Initialize a list with 0s for the last four weeks
            weekly_hours = [0] * 4

            # Group hours by week for the current project
            last_four_hours = (
                ProjectHour.objects.filter(project=project)
                .exclude(hour_type="bonus")
                .annotate(week=TruncWeek("date"))
                .values("week")
                .annotate(total_hours=Sum("hours"))
                .order_by("-week")[:4]
            )

            # Create a mapping of the last four weeks' start dates
            week_start_dates = [
                _get_date_range_by_week(week=-1)[0],
                _get_date_range_by_week(week=-2)[0],
                _get_date_range_by_week(week=-3)[0],
                _get_date_range_by_week(week=-4)[0],
            ]

            # Map each week's total hours to the correct index in weekly_hours
            for ph in last_four_hours:
                week_start = ph["week"]
                if week_start in week_start_dates:
                    week_index = week_start_dates.index(week_start)
                    weekly_hours[week_index] = ph["total_hours"]

            # Store the summed hours in the dictionary using the project ID as the key
            self.last_four_project_hours[project.id] = weekly_hours

    def add_client(self, data: t.Optional[Client]):
        if not data:
            return
        client_id = data.pk
        if client_id in self.__client_hash:
            return

        self.__client_hash[client_id] = data
        self.clients.append(data)

    def _get_employee_hours(self) -> Manager[ProjectHour]:
        if self.__cached_employee_hours_qs is None:
            start_date, end_date = _get_date_range_by_week(-1)
            start_date = end_date - timedelta(days=7 * 4)  # last 4 weeks
            self.__cached_employee_hours_qs = ProjectHour.objects.filter(
                project__in=self._project_ids,
                date__gt=start_date,
                date__lte=end_date,
            )
        return self.__cached_employee_hours_qs

    def _update_hours_count(
        self, data: ProjectHour, start_date: datetime, end_date: datetime, week_index=0
    ) -> float:
        hours = self.last_week_hours[week_index]
        data_date = data.date
        data_hours = data.hours or 0.0
        if data_date <= end_date and data_date > start_date:
            hours += data_hours
        self.last_week_hours[week_index] = hours
        return hours

    def update_hours_count(self):
        # Initialize the weekly totals
        weekly_totals = [0.0] * 4
        self.last_week_date_range = week_ranges = [
            _get_date_range_by_week(week=-1, days=WORKING_DAYS_IN_A_WEEK),
            _get_date_range_by_week(week=-2, days=WORKING_DAYS_IN_A_WEEK),
            _get_date_range_by_week(week=-3, days=WORKING_DAYS_IN_A_WEEK),
            _get_date_range_by_week(week=-4, days=WORKING_DAYS_IN_A_WEEK),
        ]

        # Iterate over all projects and accumulate hours
        for project_id, hours_list in self.last_four_project_hours.items():
            for week_index, hours in enumerate(hours_list):
                weekly_totals[week_index] += hours

        # Update the last_week_hours with the aggregated totals
        self.last_week_hours = weekly_totals
        # Sort projects based on the last week's project hours in ascending order
        self.projects.sort(key=lambda p: self.last_four_project_hours.get(p.id, [0])[0])
        print(f"TPM: {self.tpm.full_name}, Last Week Hours: {self.last_week_hours}")

    def get_formatted_date_ranges(self) -> t.List[str]:
        formatted_ranges = []
        for start_date, end_date in self.last_week_date_range:
            if start_date:
                formatted_ranges.append(start_date.strftime("%B %d"))
            if end_date:
                formatted_ranges.append(end_date.strftime("%B %d"))
        return formatted_ranges


@dataclass
class TPMsBuilder:
    __tpm_hash: t.Dict[int, TPMObj] = field(default_factory=dict, init=False)
    tpm_list: t.List[TPMObj] = field(default_factory=list, init=False)
    added_projects: t.Set[int] = field(default_factory=set, init=False)

    def get_or_create(self, data: EmployeeUnderTPM) -> TPMObj:
        tpm_id = data.tpm.pk
        if tpm_id not in self.__tpm_hash:
            tpm = TPMObj(tpm=data.tpm)
            self.__tpm_hash[tpm_id] = tpm
            self.tpm_list.append(tpm)
        tpm = self.__tpm_hash[tpm_id]
        tpm.add_employee(data=data.employee)
        # if data.project.pk not in self.added_projects:
        #     tpm.add_project(data.project)
        #     self.added_projects.add(
        #         data.project.pk
        #     )  # Mark this project as added globally
        # tpm.add_client(data=data.project.client)
        # FIXME: Add this if needed for null employee and project
        if data.project:
            if data.project.pk not in self.added_projects:
                tpm.add_project(data.project)
                self.added_projects.add(
                    data.project.pk
                )  # Mark this project as added globally
            tpm.add_client(data=data.project.client)
        return tpm

    def update_hours_count(self):
        for tpm in self.tpm_list:
            tpm.update_hours_count()

    def get_total_expected_and_got_hour_tpm(self):
        all_tmp_expected_hour = sum(tpm.tpm_expected_hour for tpm in self.tpm_list)
        all_tmp_got_hour = sum(sum(tmp.last_week_hours) for tmp in self.tpm_list)

        return all_tmp_expected_hour, all_tmp_got_hour

    def get_formatted_weekly_sums(self) -> str:
        weekly_sums = [0] * 4  # Initialize sums for the last four weeks
        for tpm in self.tpm_list:
            for i in range(4):
                weekly_sums[i] += tpm.last_week_hours[i]

        # Format the sums for each week in brackets
        formatted_sums = ",".join(
            [f"{int(sum)}" for i, sum in enumerate((weekly_sums))]
        )
        return formatted_sums
