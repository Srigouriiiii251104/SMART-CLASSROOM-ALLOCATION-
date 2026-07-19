from datetime import date, time

from django.test import TestCase

from accounts.models import User

from .models import Classroom, Course, CourseOffering, Department, Program, Term, TimeSlot
from .services import detect_timetable_conflicts, generate_timetable


class TimetableGenerationTests(TestCase):
    def setUp(self):
        self.faculty = User.objects.create_user(
            username="faculty_test",
            password="faculty123",
            role=User.ROLE_FACULTY,
        )
        department = Department.objects.create(code="CSE", name="Computer Science")
        program = Program.objects.create(code="MCA", name="MCA", department=department)
        term = Term.objects.create(name="Test Term", start_date=date.today(), end_date=date.today(), is_active=True)
        course = Course.objects.create(
            department=department,
            program=program,
            code="MCA999",
            title="Scheduling Systems",
            smart_classroom_needed=True,
        )
        self.offering = CourseOffering.objects.create(
            course=course,
            faculty=self.faculty,
            term=term,
            section="A",
            student_count=30,
            sessions_per_week=2,
        )
        Classroom.objects.create(name="Room-A", building="A", capacity=40, is_smart=True)
        Classroom.objects.create(name="Room-B", building="A", capacity=45, is_smart=True)
        TimeSlot.objects.create(day_of_week=0, start_time=time(9, 0), end_time=time(10, 0))
        TimeSlot.objects.create(day_of_week=1, start_time=time(9, 0), end_time=time(10, 0))

    def test_generate_timetable_creates_required_sessions_without_conflicts(self):
        result = generate_timetable()

        self.assertEqual(result["created_count"], 2)
        self.assertFalse(result["unallocated"])
        self.assertEqual(self.offering.timetable_entries.count(), 2)
        self.assertFalse(detect_timetable_conflicts(self.offering.term))
