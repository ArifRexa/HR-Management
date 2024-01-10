from django.urls import path
from employee.views import (
    TodoApiList,
    TodoCreateAPI,
    TodoRetriveUpdateDeleteAPIView,
    ChangeEmployeeEntryPass,
)

urlpatterns = [
    path("todos/<int:pk>/", TodoRetriveUpdateDeleteAPIView.as_view()),
    path("todos/", TodoApiList.as_view(), name="todo_list"),
    path("todos/create", TodoCreateAPI.as_view(), name="todo_create"),
    path(
        "change-employee-entry-pass/",
        ChangeEmployeeEntryPass.as_view(),
        name="change_employee_entry_pass_api",
    ),
]
