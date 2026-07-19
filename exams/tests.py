from datetime import date, time

from django.test import TestCase

from accounts.models import User
from academics.models import Classroom, Course, CourseOffering, Department, Enrollment, Program, Term

from .models import ExamSchedule
from .services import allocate_exam_halls


class ExamAllocationTests(TestCase):
    def setUp(self):
        self.faculty = User.objects.create_user(username="faculty_exam", password="faculty123", role=User.ROLE_FACULTY)
        self.student = User.objects.create_user(username="student_exam", password="student123", role=User.ROLE_STUDENT)
        department = Department.objects.create(code="ECE", name="Electronics")
        program = Program.objects.create(code="BTECH", name="BTech", department=department)
        term = Term.objects.create(name="Exam Term", start_date=date.today(), end_date=date.today(), is_active=True)
        course = Course.objects.create(department=department, program=program, code="ECE101", title="Signals")
        offering = CourseOffering.objects.create(course=course, faculty=self.faculty, term=term, section="A", student_count=1)
        Enrollment.objects.create(offering=offering, student=self.student)
        Classroom.objects.create(name="Hall-1", building="Main", capacity=30, is_exam_hall=True)
        self.exam = ExamSchedule.objects.create(
            offering=offering,
            title="Signals Test",
            exam_date=date.today(),
            start_time=time(9, 0),
            end_time=time(11, 0),
        )

    def test_exam_allocation_creates_hall_and_seat_assignment(self):
        result = allocate_exam_halls(self.exam)

        self.assertTrue(result["allocated"])
        self.assertEqual(self.exam.hall_allocations.count(), 1)
        self.assertEqual(self.exam.seating_assignments.count(), 1)


class ExamListFilterTests(TestCase):
    def setUp(self):
        self.faculty = User.objects.create_user(username="faculty_exam_t", password="password", role=User.ROLE_FACULTY)
        self.student1 = User.objects.create_user(username="student_exam_1", password="password", role=User.ROLE_STUDENT)
        self.student2 = User.objects.create_user(username="student_exam_2", password="password", role=User.ROLE_STUDENT)
        
        department = Department.objects.create(code="ECE", name="Electronics")
        program = Program.objects.create(code="BTECH", name="BTech", department=department)
        term = Term.objects.create(name="Exam Term", start_date=date.today(), end_date=date.today(), is_active=True)
        
        course1 = Course.objects.create(department=department, program=program, code="ECE101", title="Signals")
        offering1 = CourseOffering.objects.create(course=course1, faculty=self.faculty, term=term, section="A", student_count=1)
        Enrollment.objects.create(offering=offering1, student=self.student1)
        
        course2 = Course.objects.create(department=department, program=program, code="ECE102", title="Circuits")
        offering2 = CourseOffering.objects.create(course=course2, faculty=self.faculty, term=term, section="A", student_count=1)
        Enrollment.objects.create(offering=offering2, student=self.student2)
        
        self.exam1 = ExamSchedule.objects.create(
            offering=offering1,
            title="Signals Midterm",
            exam_date=date.today(),
            start_time=time(9, 0),
            end_time=time(11, 0),
        )
        self.exam2 = ExamSchedule.objects.create(
            offering=offering2,
            title="Circuits Midterm",
            exam_date=date.today(),
            start_time=time(13, 0),
            end_time=time(15, 0),
        )

    def test_student_only_sees_enrolled_exams(self):
        from django.urls import reverse
        self.client.force_login(self.student1)
        response = self.client.get(reverse("exams:exam_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Signals Midterm")
        self.assertNotContains(response, "Circuits Midterm")
