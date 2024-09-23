from django.shortcuts import render
from django.views import generic

from chat.models import Chat
# Create your views here.

class ChatView(generic.ListView):
    queryset = Chat.objects.all()
    template_name = "room.html"