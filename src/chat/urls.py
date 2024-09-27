from django.urls import path
from chat.views import ChatPromptListAPIView, ChatUserCreateAPIView, ChatView, ChatRetrieveAPIView

urlpatterns = [
    path("", ChatView.as_view(), name="chat_list"),
    path("<uuid:chat_id>/", ChatRetrieveAPIView.as_view(), name="chat"),
    path("users/", ChatUserCreateAPIView.as_view(), name="users"),
    
    path("api/prompt/", ChatPromptListAPIView.as_view(), name="prompt"),
]
