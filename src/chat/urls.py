from django.urls import path
from chat.views import ChatUserCreateAPIView, ChatView

urlpatterns = [
    path("", ChatView.as_view(), name="chat"),
    path("users/", ChatUserCreateAPIView.as_view(), name="users"),
]