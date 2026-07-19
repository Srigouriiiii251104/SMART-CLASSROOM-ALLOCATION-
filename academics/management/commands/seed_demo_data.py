from datetime import date, time, timedelta

from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import FacultyProfile, StudentProfile, User
from academics.models import (
    Classroom,
    Course,
    CourseOffering,
    Department,
    Enrollment,
    Program,
    Term,
    TimeSlot,
)
from academics.services import generate_timetable
from attendance.models import AttendanceRecord, AttendanceSession
from exams.models import ExamSchedule
from resources.models import Resource, ResourceCategory


FACULTY_SEED = [
    {
        "username": "faculty1",
        "first_name": "Meera",
        "last_name": "Nair",
        "email": "meera.nair@example.com",
        "employee_id": "FAC101",
        "designation": "Assistant Professor",
        "specialization": "Python Systems",
    },
    {
        "username": "faculty2",
        "first_name": "Arjun",
        "last_name": "Patel",
        "email": "arjun.patel@example.com",
        "employee_id": "FAC102",
        "designation": "Associate Professor",
        "specialization": "Cloud Platforms",
    },
    {
        "username": "faculty3",
        "first_name": "Kavya",
        "last_name": "Iyer",
        "email": "kavya.iyer@example.com",
        "employee_id": "FAC103",
        "designation": "Assistant Professor",
        "specialization": "Database Engineering",
    },
    {
        "username": "faculty4",
        "first_name": "Rohan",
        "last_name": "Sen",
        "email": "rohan.sen@example.com",
        "employee_id": "FAC104",
        "designation": "Assistant Professor",
        "specialization": "UX and Analytics",
    },
]

STUDENT_SEED = [
    ("student1", "Aarav", "Sharma"),
    ("student2", "Diya", "Menon"),
    ("student3", "Ishaan", "Verma"),
    ("student4", "Kavya", "Reddy"),
    ("student5", "Neha", "Joseph"),
    ("student6", "Arjun", "Sinha"),
    ("student7", "Ananya", "Rao"),
    ("student8", "Rohan", "Kulkarni"),
    ("student9", "Priya", "Das"),
    ("student10", "Vivek", "Nair"),
    ("student11", "Sneha", "Patel"),
    ("student12", "Karthik", "Babu"),
    ("student13", "Isha", "Fernandes"),
    ("student14", "Rahul", "Mehta"),
    ("student15", "Sanjana", "Pillai"),
    ("student16", "Aditya", "Roy"),
    ("student17", "Nithya", "Krishnan"),
    ("student18", "Harsh", "Vora"),
]

CLASSROOM_SEED = [
    {
        "name": "A-101",
        "building": "Academic Block A",
        "capacity": 48,
        "is_smart": True,
        "has_projector": True,
        "is_exam_hall": True,
    },
    {
        "name": "A-102",
        "building": "Academic Block A",
        "capacity": 40,
        "is_smart": False,
        "has_projector": True,
        "is_exam_hall": True,
    },
    {
        "name": "Lab-201",
        "building": "Tech Block",
        "capacity": 32,
        "is_smart": True,
        "has_projector": True,
        "has_computers": True,
        "is_exam_hall": False,
    },
    {
        "name": "Lab-202",
        "building": "Tech Block",
        "capacity": 36,
        "is_smart": True,
        "has_projector": True,
        "has_computers": True,
        "is_exam_hall": True,
    },
    {
        "name": "Studio-105",
        "building": "Innovation Wing",
        "capacity": 30,
        "is_smart": True,
        "has_projector": True,
        "is_exam_hall": True,
    },
]

TIMESLOT_SEED = [
    (0, time(9, 0), time(10, 0), "Morning Block 1"),
    (0, time(10, 15), time(11, 15), "Morning Block 2"),
    (0, time(11, 30), time(12, 30), "Late Morning"),
    (0, time(13, 30), time(14, 30), "Afternoon Block"),
    (1, time(9, 0), time(10, 0), "Morning Block 1"),
    (1, time(10, 15), time(11, 15), "Morning Block 2"),
    (1, time(11, 30), time(12, 30), "Late Morning"),
    (1, time(13, 30), time(14, 30), "Afternoon Block"),
    (2, time(9, 0), time(10, 0), "Morning Block 1"),
    (2, time(10, 15), time(11, 15), "Morning Block 2"),
    (2, time(11, 30), time(12, 30), "Late Morning"),
    (2, time(13, 30), time(14, 30), "Afternoon Block"),
    (3, time(9, 0), time(10, 0), "Morning Block 1"),
    (3, time(10, 15), time(11, 15), "Morning Block 2"),
    (3, time(11, 30), time(12, 30), "Late Morning"),
    (3, time(13, 30), time(14, 30), "Afternoon Block"),
    (4, time(9, 0), time(10, 0), "Morning Block 1"),
    (4, time(10, 15), time(11, 15), "Morning Block 2"),
    (4, time(11, 30), time(12, 30), "Late Morning"),
    (4, time(13, 30), time(14, 30), "Afternoon Block"),
    (5, time(9, 0), time(10, 0), "Morning Block 1"),
    (5, time(10, 15), time(11, 15), "Morning Block 2"),
    (5, time(11, 30), time(12, 30), "Late Morning"),
    (6, time(9, 0), time(10, 0), "Morning Block 1"),
    (6, time(10, 15), time(11, 15), "Morning Block 2"),
    (6, time(11, 30), time(12, 30), "Late Morning"),
]

COURSE_SEED = [
    {
        "code": "MCA101",
        "title": "Advanced Python Lab",
        "requires_lab": True,
        "smart_classroom_needed": True,
        "sessions_per_week": 3,
        "preferred_building": "Tech Block",
    },
    {
        "code": "MCA102",
        "title": "Cloud Computing",
        "requires_lab": False,
        "smart_classroom_needed": True,
        "sessions_per_week": 2,
        "preferred_building": "Academic Block A",
    },
    {
        "code": "MCA103",
        "title": "Database Engineering",
        "requires_lab": True,
        "smart_classroom_needed": False,
        "sessions_per_week": 3,
        "preferred_building": "Tech Block",
    },
    {
        "code": "MCA104",
        "title": "Web Interface Design",
        "requires_lab": False,
        "smart_classroom_needed": True,
        "sessions_per_week": 2,
        "preferred_building": "Innovation Wing",
    },
    {
        "code": "MCA105",
        "title": "Data Analytics Workshop",
        "requires_lab": True,
        "smart_classroom_needed": True,
        "sessions_per_week": 2,
        "preferred_building": "Tech Block",
    },
]


def _upsert_user(username: str, password: str, **defaults) -> User:
    user, _ = User.objects.update_or_create(username=username, defaults=defaults)
    user.set_password(password)
    user.save()
    return user


def _recent_dates_for_day(day_of_week: int, today: date, occurrences: int = 3) -> list[date]:
    week_start = today - timedelta(days=today.weekday())
    dates = []
    weeks_back = 0
    while len(dates) < occurrences:
        candidate = week_start - timedelta(days=7 * weeks_back) + timedelta(days=day_of_week)
        if candidate <= today:
            dates.append(candidate)
        weeks_back += 1
    return sorted(dates)


def _attendance_pattern(student_index: int, entry_index: int, session_index: int) -> tuple[str, str]:
    marker = (student_index * 5 + entry_index * 3 + session_index) % 13
    if marker == 0:
        return AttendanceRecord.STATUS_ABSENT, AttendanceRecord.METHOD_MANUAL
    if marker == 1:
        return AttendanceRecord.STATUS_LATE, AttendanceRecord.METHOD_QR
    if marker == 2:
        return AttendanceRecord.STATUS_EXCUSED, AttendanceRecord.METHOD_MANUAL
    method = AttendanceRecord.METHOD_QR if marker % 2 == 0 else AttendanceRecord.METHOD_MANUAL
    return AttendanceRecord.STATUS_PRESENT, method


class Command(BaseCommand):
    help = "Seed demo data for the Smart Classroom project."

    @transaction.atomic
    def handle(self, *args, **options):
        today = date.today()
        cse, _ = Department.objects.update_or_create(
            code="CSE",
            defaults={"name": "Computer Science", "description": "Postgraduate computing and smart classroom workflows."},
        )
        mca, _ = Program.objects.update_or_create(
            code="MCA",
            defaults={
                "name": "Master of Computer Applications",
                "department": cse,
                "duration_semesters": 4,
            },
        )
        term, _ = Term.objects.update_or_create(
            name="2026 Odd Semester",
            defaults={
                "start_date": today - timedelta(days=21),
                "end_date": today + timedelta(days=120),
                "is_active": True,
            },
        )
        if not term.is_active:
            term.is_active = True
            term.save(update_fields=["is_active"])

        _upsert_user(
            "admin",
            "admin123",
            role=User.ROLE_ADMIN,
            email="admin@example.com",
            first_name="Campus",
            last_name="Admin",
            is_staff=True,
            is_superuser=True,
        )

        faculty_users = []
        for payload in FACULTY_SEED:
            faculty = _upsert_user(
                payload["username"],
                "faculty123",
                role=User.ROLE_FACULTY,
                first_name=payload["first_name"],
                last_name=payload["last_name"],
                email=payload["email"],
            )
            FacultyProfile.objects.update_or_create(
                user=faculty,
                defaults={
                    "employee_id": payload["employee_id"],
                    "department": cse,
                    "designation": payload["designation"],
                    "specialization": payload["specialization"],
                },
            )
            faculty_users.append(faculty)

        student_users = []
        for index, (username, first_name, last_name) in enumerate(STUDENT_SEED, start=1):
            student = _upsert_user(
                username,
                "student123",
                role=User.ROLE_STUDENT,
                first_name=first_name,
                last_name=last_name,
                email=f"{username}@example.com",
            )
            StudentProfile.objects.update_or_create(
                user=student,
                defaults={
                    "student_id": f"MCA26A{index:03d}",
                    "department": cse,
                    "program": mca,
                    "semester": 1,
                    "section": "A",
                },
            )
            student_users.append(student)

        for payload in CLASSROOM_SEED:
            Classroom.objects.update_or_create(name=payload["name"], defaults=payload)

        for day, start, end, label in TIMESLOT_SEED:
            TimeSlot.objects.update_or_create(
                day_of_week=day,
                start_time=start,
                end_time=end,
                defaults={"label": label},
            )

        offerings = []
        for index, payload in enumerate(COURSE_SEED):
            course, _ = Course.objects.update_or_create(
                code=payload["code"],
                defaults={
                    "department": cse,
                    "program": mca,
                    "title": payload["title"],
                    "credit_hours": 3,
                    "requires_lab": payload["requires_lab"],
                    "smart_classroom_needed": payload["smart_classroom_needed"],
                    "description": f"{payload['title']} for MCA semester 1.",
                },
            )

            offering = CourseOffering.objects.filter(course=course, term=term, section="A").first()
            if not offering:
                offering = CourseOffering(course=course, term=term, section="A")

            offering.faculty = faculty_users[index % len(faculty_users)]
            offering.student_count = len(student_users)
            offering.sessions_per_week = payload["sessions_per_week"]
            offering.preferred_building = payload["preferred_building"]
            offering.delivery_mode = CourseOffering.DELIVERY_PHYSICAL
            offering.resource_requirements = ["projector"] + (["computers"] if payload["requires_lab"] else [])
            offering.notes = "Seeded demo offering for classroom allocation and attendance."
            offering.full_clean()
            offering.save()
            offerings.append(offering)

        for offering in offerings:
            for student in student_users:
                enrollment, _ = Enrollment.objects.get_or_create(offering=offering, student=student)
                if enrollment.status != Enrollment.STATUS_ACTIVE:
                    enrollment.status = Enrollment.STATUS_ACTIVE
                    enrollment.save(update_fields=["status"])

        projector_category, _ = ResourceCategory.objects.update_or_create(
            name="Projectors",
            defaults={"description": "Portable and fixed classroom projection units."},
        )
        smart_board_category, _ = ResourceCategory.objects.update_or_create(
            name="Smart Boards",
            defaults={"description": "Interactive teaching boards for live classroom use."},
        )
        Resource.objects.update_or_create(
            code="PRJ-001",
            defaults={
                "name": "Portable Projector",
                "category": projector_category,
                "quantity": 3,
                "available_quantity": 3,
                "is_portable": True,
            },
        )
        Resource.objects.update_or_create(
            code="SBR-101",
            defaults={
                "name": "Smart Board A-101",
                "category": smart_board_category,
                "classroom": Classroom.objects.get(name="A-101"),
                "quantity": 1,
                "available_quantity": 1,
                "is_portable": False,
            },
        )

        seminar_hall_category, _ = ResourceCategory.objects.update_or_create(
            name="Seminar Halls",
            defaults={"description": "Large presentation and lecture halls for special sessions."},
        )
        Resource.objects.update_or_create(
            code="SEM-001",
            defaults={
                "name": "Main Seminar Hall",
                "category": seminar_hall_category,
                "classroom": Classroom.objects.get(name="Studio-105"),
                "quantity": 1,
                "available_quantity": 1,
                "is_portable": False,
                "notes": "Premium seminar hall with soundproofing and dual projectors.",
            },
        )

        timetable_result = generate_timetable(term)

        seeded_sessions = 0
        seeded_records = 0
        for offering_index, offering in enumerate(
            CourseOffering.objects.filter(term=term)
            .select_related("faculty", "course")
            .prefetch_related("timetable_entries__timeslot", "enrollments__student")
        ):
            enrolled_students = list(
                offering.enrollments.filter(status=Enrollment.STATUS_ACTIVE)
                .select_related("student")
                .order_by("student__username")
            )
            for entry_index, entry in enumerate(offering.timetable_entries.select_related("timeslot").all()):
                for session_index, session_date in enumerate(_recent_dates_for_day(entry.timeslot.day_of_week, today)):
                    session, _ = AttendanceSession.objects.update_or_create(
                        timetable_entry=entry,
                        session_date=session_date,
                        defaults={
                            "created_by": offering.faculty,
                            "allow_manual": True,
                            "allow_qr": True,
                            "face_recognition_enabled": False,
                            "notes": "Seeded attendance session for demo roster tracking.",
                        },
                    )
                    seeded_sessions += 1

                    for student_index, enrollment in enumerate(enrolled_students):
                        status, method = _attendance_pattern(student_index, offering_index + entry_index, session_index)
                        marked_by = enrollment.student if method == AttendanceRecord.METHOD_QR else offering.faculty
                        AttendanceRecord.objects.update_or_create(
                            session=session,
                            student=enrollment.student,
                            defaults={
                                "status": status,
                                "access_method": method,
                                "marked_by": marked_by,
                            },
                        )
                        seeded_records += 1

        for index, offering in enumerate(offerings[:3], start=1):
            ExamSchedule.objects.update_or_create(
                offering=offering,
                title=f"{offering.course.title} Assessment {index}",
                defaults={
                    "exam_date": today + timedelta(days=14 + (index * 5)),
                    "start_time": time(10, 0),
                    "end_time": time(12, 0),
                    "exam_type": ExamSchedule.TYPE_INTERNAL if index < 3 else ExamSchedule.TYPE_PRACTICAL,
                    "status": ExamSchedule.STATUS_SCHEDULED,
                    "notes": "Seeded exam schedule for dashboard and reporting demos.",
                },
            )

        self.stdout.write(self.style.SUCCESS("Demo data created successfully."))
        self.stdout.write(
            self.style.SUCCESS(
                f"Users: 1 admin, {len(faculty_users)} faculty, {len(student_users)} students | "
                f"Timetable slots: {timetable_result['created_count']} | "
                f"Attendance sessions: {seeded_sessions} | Attendance records: {seeded_records}"
            )
        )
