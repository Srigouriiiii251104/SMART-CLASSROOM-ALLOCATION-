from django import forms

from .models import Classroom, CourseOffering, TimeSlot


class BootstrapModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css_class = "form-check-input" if isinstance(field.widget, forms.CheckboxInput) else "form-control"
            field.widget.attrs.setdefault("class", css_class)


class ClassroomForm(BootstrapModelForm):
    class Meta:
        model = Classroom
        fields = [
            "name",
            "building",
            "floor",
            "capacity",
            "is_smart",
            "has_projector",
            "has_computers",
            "is_exam_hall",
            "status",
            "notes",
        ]


class CourseOfferingForm(BootstrapModelForm):
    class Meta:
        model = CourseOffering
        fields = [
            "course",
            "faculty",
            "term",
            "section",
            "student_count",
            "sessions_per_week",
            "preferred_building",
            "resource_requirements",
            "delivery_mode",
            "notes",
        ]


class TimeSlotForm(BootstrapModelForm):
    class Meta:
        model = TimeSlot
        fields = ["day_of_week", "start_time", "end_time", "label"]
