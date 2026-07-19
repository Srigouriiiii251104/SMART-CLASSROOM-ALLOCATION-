from collections import defaultdict

from django.core.exceptions import ValidationError

from .models import Classroom, CourseOffering, Term, TimeSlot, TimetableEntry


def get_active_term() -> Term | None:
    return Term.objects.filter(is_active=True).first()


def list_available_classrooms(
    timeslot: TimeSlot,
    min_capacity: int = 0,
    needs_smart: bool = False,
    requires_lab: bool = False,
    exclude_entry_id: int | None = None,
):
    occupied_rooms = TimetableEntry.objects.filter(timeslot=timeslot)
    if exclude_entry_id:
        occupied_rooms = occupied_rooms.exclude(pk=exclude_entry_id)

    classrooms = Classroom.objects.filter(status=Classroom.STATUS_AVAILABLE, capacity__gte=min_capacity)
    if needs_smart:
        classrooms = classrooms.filter(is_smart=True)
    if requires_lab:
        classrooms = classrooms.filter(has_computers=True)
    return classrooms.exclude(id__in=occupied_rooms.values_list("classroom_id", flat=True))


def detect_timetable_conflicts(term: Term):
    entries = TimetableEntry.objects.filter(offering__term=term).select_related(
        "offering__faculty",
        "classroom",
        "timeslot",
    )
    room_map = {}
    faculty_map = {}
    conflicts = []

    for entry in entries:
        room_key = (entry.classroom_id, entry.timeslot_id)
        faculty_key = (entry.offering.faculty_id, entry.timeslot_id)

        if entry.classroom_id and room_key in room_map:
            conflicts.append(
                {
                    "type": "room",
                    "current": entry.id,
                    "conflicts_with": room_map[room_key],
                    "message": f"Room clash in {entry.classroom}.",
                }
            )
        else:
            room_map[room_key] = entry.id

        if faculty_key in faculty_map:
            conflicts.append(
                {
                    "type": "faculty",
                    "current": entry.id,
                    "conflicts_with": faculty_map[faculty_key],
                    "message": f"Faculty clash for {entry.offering.faculty.display_name}.",
                }
            )
        else:
            faculty_map[faculty_key] = entry.id
    return conflicts


def _candidate_score(offering: CourseOffering, classroom: Classroom, timeslot: TimeSlot, usage_by_room, usage_by_slot, used_days):
    score = 300
    gap = classroom.capacity - max(offering.student_count, 1)
    score -= max(gap, 0)
    score -= usage_by_room[classroom.id] * 3
    score -= usage_by_slot[timeslot.id] * 5
    if offering.preferred_building and classroom.building == offering.preferred_building:
        score += 15
    if offering.course.smart_classroom_needed and classroom.is_smart:
        score += 20
    if offering.course.requires_lab and classroom.has_computers:
        score += 20
    if timeslot.day_of_week in used_days:
        score -= 30
    return score


def generate_timetable(term: Term | None = None) -> dict:
    term = term or get_active_term()
    if not term:
        raise ValidationError("No active term is available for timetable generation.")

    timeslots = list(TimeSlot.objects.all())
    classrooms = list(Classroom.objects.filter(status=Classroom.STATUS_AVAILABLE).order_by("capacity"))
    offerings = list(
        CourseOffering.objects.filter(term=term)
        .select_related("course", "faculty")
        .order_by("-student_count", "-sessions_per_week", "course__code")
    )

    if not timeslots or not classrooms or not offerings:
        raise ValidationError("Time slots, classrooms, and course offerings are required.")

    TimetableEntry.objects.filter(offering__term=term, is_locked=False).delete()

    usage_by_room = defaultdict(int)
    usage_by_slot = defaultdict(int)
    room_busy = set()
    faculty_busy = set()
    created = []
    unallocated = []

    locked_entries = TimetableEntry.objects.filter(offering__term=term, is_locked=True)
    for entry in locked_entries:
        if entry.classroom_id:
            room_busy.add((entry.timeslot_id, entry.classroom_id))
            usage_by_room[entry.classroom_id] += 1
        faculty_busy.add((entry.timeslot_id, entry.offering.faculty_id))
        usage_by_slot[entry.timeslot_id] += 1

    for offering in offerings:
        existing_entries = TimetableEntry.objects.filter(offering=offering)
        used_days = set(existing_entries.values_list("timeslot__day_of_week", flat=True))
        needed_sessions = offering.sessions_per_week - existing_entries.count()

        for _ in range(max(needed_sessions, 0)):
            best_match = None
            best_score = None

            for timeslot in timeslots:
                if (timeslot.id, offering.faculty_id) in faculty_busy:
                    continue

                candidate_rooms = classrooms
                if offering.course.smart_classroom_needed:
                    candidate_rooms = [room for room in candidate_rooms if room.is_smart]
                if offering.course.requires_lab:
                    candidate_rooms = [room for room in candidate_rooms if room.has_computers]

                for classroom in candidate_rooms:
                    if classroom.capacity < offering.student_count:
                        continue
                    if (timeslot.id, classroom.id) in room_busy:
                        continue
                    score = _candidate_score(
                        offering,
                        classroom,
                        timeslot,
                        usage_by_room,
                        usage_by_slot,
                        used_days,
                    )
                    if best_score is None or score > best_score:
                        best_score = score
                        best_match = (timeslot, classroom)

            if not best_match:
                unallocated.append(
                    {
                        "offering": str(offering),
                        "reason": "No conflict-free classroom/time slot combination was found.",
                    }
                )
                continue

            timeslot, classroom = best_match
            entry = TimetableEntry(
                offering=offering,
                classroom=classroom,
                timeslot=timeslot,
                session_type=TimetableEntry.TYPE_LAB if offering.course.requires_lab else TimetableEntry.TYPE_LECTURE,
            )
            entry.full_clean()
            entry.save()
            created.append(entry)
            used_days.add(timeslot.day_of_week)
            room_busy.add((timeslot.id, classroom.id))
            faculty_busy.add((timeslot.id, offering.faculty_id))
            usage_by_room[classroom.id] += 1
            usage_by_slot[timeslot.id] += 1

    return {
        "term": term.name,
        "created_count": len(created),
        "unallocated": unallocated,
        "conflicts": detect_timetable_conflicts(term),
    }


def move_timetable_entry(entry: TimetableEntry, classroom: Classroom, timeslot: TimeSlot) -> TimetableEntry:
    entry.classroom = classroom
    entry.timeslot = timeslot
    entry.full_clean()
    entry.save(update_fields=["classroom", "timeslot"])
    return entry
