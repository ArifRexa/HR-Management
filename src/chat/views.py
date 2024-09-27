from cgitb import lookup
from typing import Any
from django.db.models.base import Model as Model
from django.shortcuts import render
from django.views import generic

from rest_framework import generics

from chat.models import Chat, ChatPrompt, ChatUser, Message
from chat.serializer import ChatPromptSerializer, ChatUserSerializer
# Create your views here.

class ChatView(generic.ListView):
    queryset = Chat.objects.all()
    template_name = "room.html"
    context_object_name = "chats"
    
class ChatRetrieveAPIView(generic.DetailView):
    queryset = Chat.objects.all()
    template_name = "room.html"
    context_object_name = "chat"
    pk_url_kwarg = 'chat_id'
    

    def get_context_data(self, **kwargs):
        context = super(ChatRetrieveAPIView, self).get_context_data(**kwargs)
        context["chats"] = Chat.objects.all()
        context["messages"] = Message.objects.filter(chat=self.get_object()).order_by('timestamp')
        return context
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        last_message = None
        if obj:
            last_message = obj.messages.last()
        if last_message and not last_message.is_seen:
            last_message.is_seen = True
            last_message.save()
        return obj
    
    
    
class ChatUserCreateAPIView(generics.CreateAPIView):
    queryset = ChatUser.objects.all()
    serializer_class = ChatUserSerializer
    

class ChatPromptListAPIView(generics.ListAPIView):
    queryset = ChatPrompt.objects.all()
    serializer_class = ChatPromptSerializer
    pagination_class = None