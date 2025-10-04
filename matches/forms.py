from django import forms
from django.db.utils import OperationalError, ProgrammingError

from .models import Match, Participation, SportCategory


def _safe_category_queryset():
    try:
        return SportCategory.objects.all()
    except (OperationalError, ProgrammingError):
        return SportCategory.objects.none()


class MatchForm(forms.ModelForm):
    event_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"})
    )

    class Meta:
        model = Match
        fields = [
            "title",
            "category",
            "location",
            "event_date",
            "description",
            "max_members",
        ]

    def clean_max_members(self):
        max_members = self.cleaned_data["max_members"]
        if max_members <= 0:
            raise forms.ValidationError(
                "Jumlah maksimal anggota harus lebih dari nol."
            )
        return max_members

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = _safe_category_queryset()


class ParticipationForm(forms.ModelForm):
    class Meta:
        model = Participation
        fields = ["name", "contact", "message"]
        widgets = {"message": forms.Textarea(attrs={"rows": 3})}


class MatchSearchForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=SportCategory.objects.none(),
        required=False,
        empty_label="Semua kategori",
    )
    keyword = forms.CharField(
        max_length=100, required=False, label="Kata kunci"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = _safe_category_queryset()
    available_only = forms.BooleanField(
        required=False, initial=False, label="Hanya yang slot tersedia"
    )
