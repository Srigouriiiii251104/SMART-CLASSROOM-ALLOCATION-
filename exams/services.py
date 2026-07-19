from collections import deque

from accounts.models import User
from academics.models import Classroom

from .models import ExamHallAllocation, ExamSchedule, InvigilatorAssignment, SeatingAssignment


def _available_halls(exam: ExamSchedule):
    blocked_hall_ids = ExamHallAllocation.objects.filter(
        exam__exam_date=exam.exam_date,
        exam__start_time__lt=exam.end_time,
        exam__end_time__gt=exam.start_time,
    ).exclude(exam=exam).values_list("classroom_id", flat=True)
    return list(
        Classroom.objects.filter(
            status=Classroom.STATUS_AVAILABLE,
            is_exam_hall=True,
        )
        .exclude(id__in=blocked_hall_ids)
        .order_by("capacity")
    )


def allocate_exam_halls(exam: ExamSchedule):
    students = deque(
        exam.offering.enrollments.filter(status="active")
        .select_related("student")
        .order_by("student__username")
    )
    halls = _available_halls(exam)
    faculty_pool = list(User.objects.filter(role=User.ROLE_FACULTY).exclude(pk=exam.offering.faculty_id))

    exam.hall_allocations.all().delete()
    exam.seating_assignments.all().delete()
    exam.invigilator_assignments.all().delete()

    selected_halls = []
    remaining = len(students)
    available_halls = halls.copy()

    while remaining > 0 and available_halls:
        exact_fit = next((hall for hall in available_halls if hall.capacity >= remaining), None)
        hall = exact_fit or available_halls[-1]
        selected_halls.append(hall)
        available_halls.remove(hall)
        remaining -= hall.capacity

    if remaining > 0:
        return {"allocated": False, "message": "Not enough hall capacity available for this exam."}

    faculty_index = 0
    for hall in selected_halls:
        seats_for_hall = min(hall.capacity, len(students))
        allocation = ExamHallAllocation(exam=exam, classroom=hall, allocated_students=seats_for_hall)
        allocation.full_clean()
        allocation.save()

        for seat_index in range(1, seats_for_hall + 1):
            enrollment = students.popleft()
            seat_number = f"R{((seat_index - 1) // 5) + 1:02d}-S{((seat_index - 1) % 5) + 1:02d}"
            SeatingAssignment.objects.create(
                exam=exam,
                student=enrollment.student,
                classroom=hall,
                seat_number=seat_number,
            )

        if faculty_pool:
            faculty = faculty_pool[faculty_index % len(faculty_pool)]
            InvigilatorAssignment.objects.create(exam=exam, faculty=faculty, classroom=hall)
            faculty_index += 1

    exam.status = ExamSchedule.STATUS_SCHEDULED
    exam.save(update_fields=["status"])
    return {"allocated": True, "message": "Exam halls and seating assignments generated successfully."}
