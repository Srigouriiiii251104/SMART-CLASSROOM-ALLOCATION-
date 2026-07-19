# API Documentation

## Authentication

- `POST /api/token/`
  - Obtain JWT access and refresh tokens.
- `POST /api/token/refresh/`
  - Refresh access token.

## Timetable APIs

- `GET /academics/api/timetable/`
  - Returns timetable entries.
  - Query params: `term`
- `POST /academics/api/timetable/generate/`
  - Generates a conflict-aware timetable.
  - Body: `{"term_id": 1}`
- `POST /academics/api/timetable/move/`
  - Updates timetable entry room/time after drag-and-drop.
  - Body: `{"entry_id": 1, "timeslot_id": 2, "classroom_id": 3}`
- `GET /academics/api/classrooms/free/`
  - Finds free rooms for a given slot.
  - Query params: `timeslot_id`, `min_capacity`, `needs_smart`, `requires_lab`

## Resource APIs

- `GET /resources/api/availability/`
  - Query params: `date`, `start_time`, `end_time`, `category_id`
- `GET /resources/api/bookings/`
  - Returns resource booking list.
- `POST /resources/api/bookings/`
  - Creates a booking request.

## Attendance APIs

- `POST /attendance/api/mark/`
  - Manual or QR-based attendance marking.
  - Body examples:
    - `{"session_id": 1, "student_id": 4, "status": "present", "access_method": "manual"}`
    - `{"qr_token": "uuid-token"}`

## Assistant APIs

- `POST /assistant/api/query/`
  - Body: `{"query": "show free classrooms"}`
  - Returns chatbot response text.

## Response Style

- JSON responses use standard DRF serialization
- Errors return `detail` with HTTP 400/404 when applicable
