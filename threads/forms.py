from django.forms import ModelForm
from threads.models import Thread, ReplyChild,Reply
from django.utils.html import strip_tags

class ThreadForm(ModelForm):
    class Meta:
        model = Thread
        fields = ["title", "content", "category", "thumbnail", "is_featured"]

        def clean_title(self):
            title = self.cleaned_data["title"]
            return strip_tags(title)

        def clean_content(self):
            content = self.cleaned_data["content"]
            return strip_tags(content)