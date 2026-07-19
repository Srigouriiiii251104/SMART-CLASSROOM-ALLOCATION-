# Database Schema

## Main Tables

### Accounts

- `accounts_user`
  - Custom authentication table with `role`, `phone_number`, and Django auth fields.
- `accounts_facultyprofile`
  - Stores `employee_id`, department, designation, and specialization.
- `accounts_studentprofile`
  - Stores `student_id`, program, semester, and section.

### Academic Planning

- `academics_department`
- `academics_program`
- `academics_term`
- `academics_classroom`
  - Includes smart-room flags, capacity, status, and QR code fields.
- `academics_timeslot`
- `academics_course`
- `academics_courseoffering`
  - Faculty assignment, section, sessions per week, and room requirements.
- `academics_enrollment`
- `academics_timetableentry`

### Resource Management

- `resources_resourcecategory`
- `resources_resource`
- `resources_resourcebooking`
- `resources_maintenancerecord`

### Attendance

- `attendance_attendancesession`
- `attendance_attendancerecord`

### Notifications

- `notifications_app_notification`
- `notifications_app_announcement`

### Exams

- `exams_examschedule`
- `exams_examhallallocation`
- `exams_invigilatorassignment`
- `exams_seatingassignment`

### Reports

- `reports_generatedreport`

### Assistant

- `assistant_bot_chatbotinteraction`

## Key Constraints

- Unique user role-aware profiles per user
- Unique classroom QR token
- Unique time slot per weekday/time combination
- Unique offering per course/faculty/term/section
- Unique room assignment per time slot
- Unique attendance record per student/session
- Unique exam hall assignment and seat number per exam

## Database Support

- Default local configuration uses SQLite
- Production settings support PostgreSQL and MySQL through environment variables
