from datetime import date, time

from django.test import TestCase
from django.urls import reverse

from accounts.models import StudentProfile, User
from academics.models import (
    Classroom,
    Course,
    CourseOffering,
    Department,
    Enrollment,
    Program,
    Term,
    TimeSlot,
    TimetableEntry,
)

from .models import AttendanceSession


class AttendanceSessionDetailTests(TestCase):
    def setUp(self):
        self.faculty = User.objects.create_user(
            username="faculty_roster",
            password="faculty123",
            role=User.ROLE_FACULTY,
            first_name="Riya",
            last_name="Thomas",
        )
        self.student = User.objects.create_user(
            username="student_roster",
            password="student123",
            role=User.ROLE_STUDENT,
            first_name="Dev",
            last_name="Kumar",
        )
        department = Department.objects.create(code="CSE", name="Computer Science")
        program = Program.objects.create(code="MCA", name="MCA", department=department)
        term = Term.objects.create(name="Roster Term", start_date=date.today(), end_date=date.today(), is_active=True)
        course = Course.objects.create(
            department=department,
            program=program,
            code="MCA201",
            title="Attendance Analytics",
        )
        offering = CourseOffering.objects.create(
            course=course,
            faculty=self.faculty,
            term=term,
            section="A",
            student_count=1,
            sessions_per_week=1,
        )
        StudentProfile.objects.create(
            user=self.student,
            student_id="MCA26A999",
            department=department,
            program=program,
            semester=1,
            section="A",
        )
        Enrollment.objects.create(offering=offering, student=self.student)
        classroom = Classroom.objects.create(name="A-401", building="A", capacity=30)
        timeslot = TimeSlot.objects.create(day_of_week=0, start_time=time(9, 0), end_time=time(10, 0))
        entry = TimetableEntry.objects.create(offering=offering, classroom=classroom, timeslot=timeslot)
        self.session = AttendanceSession.objects.create(timetable_entry=entry, session_date=date.today(), created_by=self.faculty)

    def test_session_detail_shows_enrolled_students_with_pending_status(self):
        self.client.force_login(self.faculty)

        response = self.client.get(reverse("attendance:session_detail", args=[self.session.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dev Kumar")
        self.assertContains(response, "Pending")
        self.assertContains(response, "MCA26A999")


class AttendanceManualMarkViewTests(TestCase):
    def setUp(self):
        self.faculty = User.objects.create_user(username="faculty_m", password="password", role=User.ROLE_FACULTY)
        self.student = User.objects.create_user(username="student_m", password="password", role=User.ROLE_STUDENT)
        self.other_faculty = User.objects.create_user(username="faculty_other", password="password", role=User.ROLE_FACULTY)
        
        department = Department.objects.create(code="CSE", name="Computer Science")
        program = Program.objects.create(code="MCA", name="MCA", department=department)
        term = Term.objects.create(name="T1", start_date=date.today(), end_date=date.today(), is_active=True)
        course = Course.objects.create(department=department, program=program, code="MCA201", title="Java")
        offering = CourseOffering.objects.create(course=course, faculty=self.faculty, term=term, section="A", student_count=1)
        
        StudentProfile.objects.create(user=self.student, student_id="STU-001", department=department, program=program, semester=1, section="A")
        Enrollment.objects.create(offering=offering, student=self.student)
        
        classroom = Classroom.objects.create(name="A-401", building="A", capacity=30)
        timeslot = TimeSlot.objects.create(day_of_week=0, start_time=time(9, 0), end_time=time(10, 0))
        entry = TimetableEntry.objects.create(offering=offering, classroom=classroom, timeslot=timeslot)
        self.session = AttendanceSession.objects.create(timetable_entry=entry, session_date=date.today(), created_by=self.faculty)

    def test_faculty_can_mark_attendance_manually(self):
        self.client.force_login(self.faculty)
        url = reverse("attendance:mark_manual", args=[self.session.pk, self.student.pk])
        response = self.client.post(url, {"status": "present"})
        self.assertRedirects(response, reverse("attendance:session_detail", args=[self.session.pk]))
        
        from .models import AttendanceRecord
        record = AttendanceRecord.objects.get(session=self.session, student=self.student)
        self.assertEqual(record.status, "present")
        self.assertEqual(record.access_method, "manual")

    def test_student_cannot_mark_attendance_manually(self):
        self.client.force_login(self.student)
        url = reverse("attendance:mark_manual", args=[self.session.pk, self.student.pk])
        response = self.client.post(url, {"status": "present"})
        self.assertRedirects(response, reverse("attendance:session_detail", args=[self.session.pk]))
        
        from .models import AttendanceRecord
        self.assertFalse(AttendanceRecord.objects.filter(session=self.session, student=self.student).exists())
