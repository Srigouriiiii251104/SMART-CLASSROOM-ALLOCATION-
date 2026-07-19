from django import forms

from .models import AttendanceSession


class AttendanceSessionForm(forms.ModelForm):
    class Meta:
        model = AttendanceSession
        fields = [
            "timetable_entry",
            "session_date",
            "allow_manual",
            "allow_qr",
            "face_recognition_enabled",
            "notes",
        ]
        widgets = {
            "session_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css_class = "form-check-input" if isinstance(field.widget, forms.CheckboxInput) else "form-control"
            field.widget.attrs.setdefault("class", css_class)
