from django.forms import ModelForm
from threads.models import Thread, ReplyChild,Reply
from django.utils.html import strip_tags

class ThreadForm(ModelForm):
    class Meta:
        model = Thread
        fields = ["content", "tags", "image"]

        def clean_content(self):
            content = self.cleaned_data["content"]
            return strip_tags(content)