from django import forms
from django.db import connection
from django.db.utils import OperationalError, ProgrammingError

from .models import Match, Participation, SportCategory


def _is_category_table_ready() -> bool:
    """Return True when the sport category table is available."""

    try:
        existing_tables = set(connection.introspection.table_names())
    except (OperationalError, ProgrammingError):
        return False

    return SportCategory._meta.db_table in existing_tables


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

        if not _is_category_table_ready():
            self.fields["category"].queryset = SportCategory.objects.none()
            self.fields["category"].disabled = True


class ParticipationForm(forms.ModelForm):
    class Meta:
        model = Participation
        fields = ["name", "contact", "message"]
        widgets = {"message": forms.Textarea(attrs={"rows": 3})}


class MatchSearchForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=SportCategory.objects.all(),
        required=False,
        empty_label="Semua kategori",
    )
    keyword = forms.CharField(
        max_length=100, required=False, label="Kata kunci"
    )
    available_only = forms.BooleanField(
        required=False, initial=False, label="Hanya yang slot tersedia"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not _is_category_table_ready():
            self.fields["category"].queryset = SportCategory.objects.none()
            self.fields["category"].disabled = True
