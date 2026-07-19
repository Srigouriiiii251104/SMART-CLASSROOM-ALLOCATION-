from django.test import TestCase
from django.urls import reverse

from .models import FacultyProfile, StudentProfile, User


class AccountAuthFlowTests(TestCase):
    def test_signup_creates_student_and_profile(self):
        response = self.client.post(
            reverse("accounts:signup"),
            {
                "role": User.ROLE_STUDENT,
                "first_name": "Test",
                "last_name": "Student",
                "username": "newstudent",
                "email": "newstudent@example.com",
                "phone_number": "",
                "student_id": "",
                "semester": 2,
                "section": "B",
                "password1": "ComplexPass123",
                "password2": "ComplexPass123",
            },
        )

        self.assertRedirects(response, reverse("dashboard:home"))
        user = User.objects.get(username="newstudent")
        self.assertEqual(user.role, User.ROLE_STUDENT)
        self.assertTrue(StudentProfile.objects.filter(user=user).exists())

    def test_signup_creates_teacher_profile(self):
        response = self.client.post(
            reverse("accounts:signup"),
            {
                "role": User.ROLE_FACULTY,
                "first_name": "Test",
                "last_name": "Teacher",
                "username": "newteacher",
                "email": "newteacher@example.com",
                "phone_number": "",
                "employee_id": "FAC-9001",
                "password1": "ComplexPass123",
                "password2": "ComplexPass123",
            },
        )

        self.assertRedirects(response, reverse("dashboard:home"))
        user = User.objects.get(username="newteacher")
        self.assertEqual(user.role, User.ROLE_FACULTY)
        self.assertTrue(FacultyProfile.objects.filter(user=user).exists())

    def test_login_rejects_wrong_role_selection(self):
        User.objects.create_user(
            username="studentrole",
            password="student12345",
            role=User.ROLE_STUDENT,
        )

        response = self.client.post(
            reverse("login"),
            {
                "username": "studentrole",
                "password": "student12345",
                "role": User.ROLE_ADMIN,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "not the selected role")
