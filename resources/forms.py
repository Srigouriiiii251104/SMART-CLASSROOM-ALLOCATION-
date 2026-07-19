from django import forms

from .models import Resource, ResourceBooking


class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = [
            "category",
            "classroom",
            "name",
            "code",
            "quantity",
            "is_portable",
            "status",
            "notes",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault("class", "form-control")


class ResourceBookingForm(forms.ModelForm):
    class Meta:
        model = ResourceBooking
        fields = [
            "resource",
            "classroom",
            "booking_date",
            "start_time",
            "end_time",
            "quantity",
            "purpose",
            "notes",
        ]
        widgets = {
            "booking_date": forms.DateInput(attrs={"type": "date"}),
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css_class = "form-check-input" if isinstance(field.widget, forms.CheckboxInput) else "form-control"
            field.widget.attrs.setdefault("class", css_class)
