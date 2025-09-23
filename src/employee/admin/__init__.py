from employee.admin.appointment import AppointmentAdmin
from employee.admin.employeee_rating_admin import EmployeeRatingAdmin

from .config import ConfigAdmin
from .employee import EmployeeAdmin
from .employee_activity import *
from .employee_bank import BankAccountAdmin
from .employee_feedback import EmployeePerformanceFeedbackAdmin
from .excuse_note import ExcuseNoteAdmin
from .favourite_menu import FavouriteMenuAdmin
from .home_office import HomeOfficeManagement
from .hr_policy import (
    HRContractPolicies,
    HRPolicyAdmin,
    HRPolicySectionAdmin,
)
from .leave import LeaveManagement
from .needhelp_position import (
    # EmployeeNeedHelpAdmin,
    NeedHelpPosition,
)
from .overtime import OvertimeAdmin
from .resignation import ResignationAdmin
from .skill import LearningAdmin, SkillAdmin
from .tour_allowance import TourAllowanceAdmin
from .user import UserAdmin
