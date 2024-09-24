from django.shortcuts import render
from django.views import generic

from rest_framework import generics

from chat.models import Chat, ChatUser
from chat.serializer import ChatUserSerializer
# Create your views here.

class ChatView(generic.ListView):
    queryset = Chat.objects.all()
    template_name = "room.html"
    
    
class ChatUserCreateAPIView(generics.CreateAPIView):
    queryset = ChatUser.objects.all()
    serializer_class = ChatUserSerializer