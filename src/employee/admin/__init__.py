from .employee import EmployeeAdmin
from .leave import LeaveManagement
from .overtime import OvertimeAdmin
from .resignation import ResignationAdmin
from .user import UserAdmin
from .skill import SkillAdmin, LearningAdmin
from .employee_activity import *
# from .employee_feedback import EmployeeFeedbackAdmin
from .tour_allowance import TourAllowanceAdmin
from .excuse_note import ExcuseNoteAdmin
from .config import ConfigAdmin
from .favourite_menu import FavouriteMenuAdmin
from .employee_bank import BankAccountAdmin
from .home_office import HomeOfficeManagement
from employee.admin.employeee_rating_admin import EmployeeRatingAdmin
from employee.admin.appointment import AppointmentAdmin

from .hr_policy import (
    HRPolicySectionAdmin,
    HRPolicyAdmin,
    HRContractPolicies,
    
)

from .needhelp_position import (
    # EmployeeNeedHelpAdmin,
    NeedHelpPosition,
    EmployeeAttendanceThree
)

from .test_admin import EmployeeAttendanceOneAdmin
