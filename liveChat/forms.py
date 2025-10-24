from django import forms
from .models import Group, Chat

try:
    from typing import override  # Python 3.12+ (buat lokal kamu yang pakai 3.13)
except ImportError:
    def override(func):  # fallback buat Python 3.11 (PWS)
        return func


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ["match", "name"]


class ChatForm(forms.ModelForm):
    class Meta:
        model = Chat
        fields = ["group_id", "username", "message"]
