from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import FacultyProfile, StudentProfile


User = get_user_model()

ROLE_UI_CHOICES = [
    (User.ROLE_STUDENT, "Student"),
    (User.ROLE_FACULTY, "Teacher"),
    (User.ROLE_ADMIN, "Admin"),
]


class BootstrapFormMixin:
    def apply_bootstrap(self):
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.HiddenInput):
                continue
            css_class = "form-check-input" if isinstance(field.widget, forms.CheckboxInput) else "form-control"
            field.widget.attrs.setdefault("class", css_class)


class RoleAwareLoginForm(BootstrapFormMixin, AuthenticationForm):
    role = forms.ChoiceField(choices=ROLE_UI_CHOICES, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_bootstrap()
        self.fields["username"].widget.attrs["placeholder"] = "Enter username"
        self.fields["password"].widget.attrs["placeholder"] = "Enter password"
        self.initial.setdefault("role", User.ROLE_STUDENT)

    def clean(self):
        cleaned_data = super().clean()
        selected_role = cleaned_data.get("role") or self.data.get("role")
        if self.user_cache and selected_role and self.user_cache.role != selected_role:
            raise forms.ValidationError(
                f"This account is registered as {self.user_cache.get_role_display()}, not the selected role."
            )
        return cleaned_data


class SignupForm(BootstrapFormMixin, UserCreationForm):
    role = forms.ChoiceField(choices=ROLE_UI_CHOICES, widget=forms.HiddenInput())
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField()
    phone_number = forms.CharField(max_length=20, required=False)
    employee_id = forms.CharField(max_length=30, required=False)
    student_id = forms.CharField(max_length=30, required=False)
    semester = forms.IntegerField(min_value=1, required=False, initial=1)
    section = forms.CharField(max_length=20, required=False, initial="A")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "role",
            "first_name",
            "last_name",
            "username",
            "email",
            "phone_number",
            "employee_id",
            "student_id",
            "semester",
            "section",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_bootstrap()
        self.initial.setdefault("role", User.ROLE_STUDENT)
        self.fields["username"].widget.attrs["placeholder"] = "Choose a username"
        self.fields["email"].widget.attrs["placeholder"] = "name@example.com"
        self.fields["phone_number"].widget.attrs["placeholder"] = "Optional phone number"
        self.fields["employee_id"].widget.attrs["placeholder"] = "Optional teacher ID"
        self.fields["student_id"].widget.attrs["placeholder"] = "Optional student ID"
        self.fields["password1"].widget.attrs["placeholder"] = "Create a password"
        self.fields["password2"].widget.attrs["placeholder"] = "Confirm the password"

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get("role")
        employee_id = cleaned_data.get("employee_id")
        student_id = cleaned_data.get("student_id")

        if role == User.ROLE_FACULTY and employee_id and FacultyProfile.objects.filter(employee_id=employee_id).exists():
            self.add_error("employee_id", "This teacher ID is already in use.")

        if role == User.ROLE_STUDENT and student_id and StudentProfile.objects.filter(student_id=student_id).exists():
            self.add_error("student_id", "This student ID is already in use.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        role = self.cleaned_data["role"]
        user.role = role
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        user.phone_number = self.cleaned_data["phone_number"]
        user.is_staff = role == User.ROLE_ADMIN

        if commit:
            user.save()
            self._create_role_profile(user)
        return user

    def _create_role_profile(self, user):
        if user.role == User.ROLE_FACULTY:
            FacultyProfile.objects.get_or_create(
                user=user,
                defaults={
                    "employee_id": self.cleaned_data.get("employee_id") or f"FAC-{user.pk:04d}",
                },
            )
        elif user.role == User.ROLE_STUDENT:
            StudentProfile.objects.get_or_create(
                user=user,
                defaults={
                    "student_id": self.cleaned_data.get("student_id") or f"STU-{user.pk:04d}",
                    "semester": self.cleaned_data.get("semester") or 1,
                    "section": self.cleaned_data.get("section") or "A",
                },
            )
