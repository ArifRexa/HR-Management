from dateutil.relativedelta import relativedelta
from django.utils import timezone
from employee.models import Employee
from provident_fund.models import Account


# Seed pf account
def create_all_pfaccount():
    now = timezone.now().date().replace(day=1)

    now = now - relativedelta(days=1)
    starting_date_of_pf_account = now.replace(day=1)

    maturity_date = starting_date_of_pf_account + relativedelta(years=2)
    
    employees = Employee.objects.filter(active=True, pf_eligibility=True)
    accounts = list()
    
    for employee in employees:
        accounts.append(Account(
            employee=employee,
            start_date=starting_date_of_pf_account,
            maturity_date=maturity_date,
            scale=10.0,
        ))
    
    Account.objects.bulk_create(accounts)
    
