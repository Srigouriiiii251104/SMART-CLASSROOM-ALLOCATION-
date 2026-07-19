from datetime import date, time

from django.core.exceptions import ValidationError
from django.test import TestCase

from accounts.models import User
from academics.models import Classroom, Term, TimeSlot, Course, CourseOffering, TimetableEntry, Department, Program
from .models import Resource, ResourceBooking, ResourceCategory


class ResourceBookingTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="student_test", password="student123", role=User.ROLE_STUDENT)
        self.classroom = Classroom.objects.create(name="Lab-X", building="Tech", capacity=25)
        category = ResourceCategory.objects.create(name="Projectors")
        self.resource = Resource.objects.create(
            category=category,
            classroom=self.classroom,
            name="Projector X",
            code="PRJ-X",
            quantity=1,
            available_quantity=1,
        )

    def test_overlapping_resource_booking_is_rejected(self):
        ResourceBooking.objects.create(
            resource=self.resource,
            requested_by=self.user,
            classroom=self.classroom,
            booking_date=date.today(),
            start_time=time(10, 0),
            end_time=time(11, 0),
            quantity=1,
            purpose="Class Demo",
            status=ResourceBooking.STATUS_APPROVED,
        )
        conflicting = ResourceBooking(
            resource=self.resource,
            requested_by=self.user,
            classroom=self.classroom,
            booking_date=date.today(),
            start_time=time(10, 30),
            end_time=time(11, 30),
            quantity=1,
            purpose="Second Demo",
        )

        with self.assertRaises(ValidationError):
            conflicting.full_clean()

    def test_resource_booking_clash_with_class_is_rejected(self):
        dep = Department.objects.create(code='CSE_T', name='CSE')
        prog = Program.objects.create(code='MCA_T', name='MCA', department=dep)
        term = Term.objects.create(name='T_RES_TEST', start_date=date.today(), end_date=date.today(), is_active=True)
        course = Course.objects.create(department=dep, program=prog, code='MCA777', title='Systems')
        offering = CourseOffering.objects.create(course=course, faculty=self.user, term=term, section='A')
        timeslot = TimeSlot.objects.create(day_of_week=date.today().weekday(), start_time=time(14, 0), end_time=time(15, 0))
        
        # Schedule a class in self.classroom
        TimetableEntry.objects.create(offering=offering, classroom=self.classroom, timeslot=timeslot)
        
        # Attempt to book a resource inside self.classroom during that class timeslot
        clashing_booking = ResourceBooking(
            resource=self.resource,
            requested_by=self.user,
            classroom=self.classroom,
            booking_date=date.today(),
            start_time=time(14, 15),
            end_time=time(14, 45),
            quantity=1,
            purpose="Self Study",
        )
        
        with self.assertRaises(ValidationError):
            clashing_booking.full_clean()


class ResourceCreationTests(TestCase):
    def setUp(self):
        self.faculty = User.objects.create_user(username="faculty_res", password="password", role=User.ROLE_FACULTY)
        self.student = User.objects.create_user(username="student_res", password="password", role=User.ROLE_STUDENT)
        self.category = ResourceCategory.objects.create(name="Study Materials")

    def test_faculty_can_create_resource(self):
        from django.urls import reverse
        self.client.force_login(self.faculty)
        url = reverse("resources:resource_add")
        response = self.client.post(url, {
            "category": self.category.pk,
            "name": "New Projector",
            "code": "PRJ-NEW",
            "quantity": 2,
            "is_portable": True,
            "status": "available",
            "notes": "Added via frontend"
        })
        self.assertRedirects(response, reverse("resources:resource_list"))
        self.assertTrue(Resource.objects.filter(code="PRJ-NEW").exists())

    def test_student_cannot_create_resource(self):
        from django.urls import reverse
        self.client.force_login(self.student)
        url = reverse("resources:resource_add")
        response = self.client.post(url, {
            "category": self.category.pk,
            "name": "Hackable Projector",
            "code": "PRJ-HACK",
            "quantity": 1,
            "is_portable": True,
            "status": "available"
        })
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Resource.objects.filter(code="PRJ-HACK").exists())
