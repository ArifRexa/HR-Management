from __future__ import annotations
import typing as t
from django.db.models import Manager
from datetime import datetime, timedelta
from dataclasses import dataclass
from dataclasses import field
from employee.models import (
    Employee,
)
from employee.models.employee import (
    EmployeeUnderTPM,
)
from project_management.models import Project
from project_management.models import Client
from project_management.models import EmployeeProjectHour





WORKING_DAYS_IN_A_WEEK = 5



def _get_date_range_by_week(week=0, days=7):
    """
    week: int
        1 (next week)
        0 (current week)
        -1 (last week)
        -2 (2nd last week)
    """
    now = datetime.now()
    start_day_of_year = datetime(
        year=now.year,
        month=1,
        day=1,
    )
    week_day_of_year_start = start_day_of_year.weekday()
    target_week = (now + timedelta(weeks=week)).isocalendar()[1]

    start_day = (
        start_day_of_year
        + timedelta(
            weeks=target_week - 1,
            days=-week_day_of_year_start
        )
    ).date()
    end_date = start_day + timedelta(
        days=days - 1
    )
    return (start_day, end_date)



@dataclass
class TPMObj:
    tpm: Employee
    last_week_date_range: t.List[t.Tuple[t.Optional[datetime]]] = field(default_factory=lambda: [(None, None)]*4, init=False)
    last_week_hours: t.List[float] = field(default_factory=lambda: [0.0]*4, init=False)

    employees: t.List[Employee] = field(default_factory=list, init=False)
    projects: t.List[Project] = field(default_factory=list, init=False)
    clients: t.List[Client] = field(default_factory=list, init=False)

    _employee_ids: t.List[int] = field(default_factory=list, init=False)
    _project_ids: t.List[int] = field(default_factory=list, init=False)

    __employee_hash: t.Dict[int, Employee] = field(default_factory=dict, init=False, repr=False)
    __project_hash: t.Dict[int, Project] = field(default_factory=dict, init=False, repr=False)
    __client_hash: t.Dict[int, Client] = field(default_factory=dict, init=False, repr=False)
    __cached_employee_hours_qs: t.Optional[Manager[EmployeeProjectHour]] = field(default=None, init=False, repr=False)

    def add_employee(self, data: Employee):
        employee_id = data.pk
        if employee_id in self.__employee_hash:
            return

        self.__cached_employee_hours_qs = None
        self._employee_ids.append(employee_id)
        self.__employee_hash[employee_id] = data
        self.employees.append(data)

    def add_project(self, data: Project):
        project_id = data.pk
        if project_id in self.__project_hash:
            return

        self.__cached_employee_hours_qs = None
        self._project_ids.append(project_id)
        self.__project_hash[project_id] = data
        self.projects.append(data)

    def add_client(self, data: t.Optional[Client]):
        if not data:
            return
        client_id = data.pk
        if client_id in self.__client_hash:
            return

        self.__client_hash[client_id] = data
        self.clients.append(data)

    def _get_employee_hours(self) -> Manager[EmployeeProjectHour]:
        if self.__cached_employee_hours_qs is None:
            start_date, end_date = _get_date_range_by_week(-1)
            start_date = end_date - timedelta(days=7*4) # last 4 weeks
            self.__cached_employee_hours_qs = EmployeeProjectHour.objects.filter(
                employee__in=self._employee_ids,
                project_hour__project__in=self._project_ids,
                project_hour__date__gt=start_date,
                project_hour__date__lte=end_date,
            ).select_related(
                'project_hour'
            )
        return self.__cached_employee_hours_qs

    def _update_hours_count(
            self,
            data: EmployeeProjectHour,
            start_date: datetime,
            end_date: datetime,
            week_index=0
        ) -> float:
        hours = self.last_week_hours[week_index]
        data_date = data.project_hour.date
        data_hours = data.hours or 0.0
        if data_date <= end_date and data_date > start_date:
            hours += data_hours
        self.last_week_hours[week_index] = hours
        return hours

    def update_hours_count(self):
        self.last_week_hours = [0.0] * 4
        self.last_week_date_range = week_ranges = [
            _get_date_range_by_week(week=-1, days=WORKING_DAYS_IN_A_WEEK),
            _get_date_range_by_week(week=-2, days=WORKING_DAYS_IN_A_WEEK),
            _get_date_range_by_week(week=-3, days=WORKING_DAYS_IN_A_WEEK),
            _get_date_range_by_week(week=-4, days=WORKING_DAYS_IN_A_WEEK),
        ]
        employee_hours = self._get_employee_hours()
        for entry in employee_hours:
            for week_index, (start_date, end_date) in enumerate(week_ranges):
                self._update_hours_count(
                    data=entry,
                    start_date=start_date,
                    end_date=end_date,
                    week_index=week_index
                )



@dataclass
class TPMsBuilder:

    __tpm_hash: t.Dict[int, TPMObj] = field(default_factory=dict, init=False)
    tpm_list: t.List[TPMObj] = field(default_factory=list, init=False)

    def get_or_create(self, data: EmployeeUnderTPM) -> TPMObj:
        tpm_id = data.tpm.pk
        if tpm_id not in self.__tpm_hash:
            tpm = TPMObj(
                tpm=data.tpm
            )
            self.__tpm_hash[tpm_id] = tpm
            self.tpm_list.append(tpm)
        tpm = self.__tpm_hash[tpm_id]
        tpm.add_employee(data=data.employee)
        tpm.add_project(data=data.project)
        tpm.add_client(data=data.project.client)
        return tpm

    def update_hours_count(self):
        for tpm in self.tpm_list:
            tpm.update_hours_count()
