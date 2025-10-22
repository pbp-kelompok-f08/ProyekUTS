from django import forms
from .models import Group, Chat
from typing import override

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ["match", "name"]

class ChatForm(forms.ModelForm):
    class Meta:
        model = Chat
        fields = ["group_id", "username", "message"]