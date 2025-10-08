from django.urls import path
from employee.views import (
    TodoApiList,
    TodoCreateAPI,
    TodoRetriveUpdateDeleteAPIView,
    ChangeEmployeeEntryPass,
    booking_conference_room,
    delete_booking,
    employee_project_select_form,
    save_available_slot,
    update_booking
)

urlpatterns = [
    path("todos/<int:pk>/", TodoRetriveUpdateDeleteAPIView.as_view()),
    path("todos/", TodoApiList.as_view(), name="todo_list"),
    path("todos/create", TodoCreateAPI.as_view(), name="todo_create"),
    path('booking_conference_room/', booking_conference_room, name='booking_conference_room'),
    path('delete_booking/<int:booking_id>/', delete_booking, name='delete_booking'),
    path('update_booking/<int:booking_id>/', update_booking, name='update_booking'),
    path(
        "change-employee-entry-pass/",
        ChangeEmployeeEntryPass.as_view(),
        name="change_employee_entry_pass_api",
    ),
    path("employee-project-form/<int:employee_id>/", employee_project_select_form, name="employee_project_form"),
    path("save-slot/", save_available_slot, name="save_available_slot"),
]
