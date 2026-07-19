# Feature Requirements — Teacher & Student Dashboards

This document captures the polished feature list provided for the Smart Classroom Allocation and Resource Management System. Use it as a developer spec, work breakdown, or an AI prompt for implementation planning.

---

## Teacher Dashboard

### 1. Timetable Management

- Add, edit, delete, and update class timetables.
- View timetable by:
  - Day
  - Week
  - Subject
  - Semester
  - Classroom
- Notify students automatically whenever the timetable is updated.

### 2. Resource Management
Teachers should be able to:

- Upload study materials (PDF, PPT, DOC, Images, Videos)
- Add notes
- Share assignment files
- Add library references/books
- Categorize resources by:
  - Subject
  - Unit
  - Semester
  - Course

Students should receive notifications whenever new resources are uploaded.

### 3. Attendance Management

#### Manual Attendance

- Mark students Present/Absent/Late.
- Edit attendance later if required.
- View attendance history.

#### QR Code Attendance

- Generate a unique QR code for each class.
- QR code should expire after a short duration (e.g., 1–2 minutes).
- Students scan the QR code to mark attendance.
- Prevent duplicate attendance.
- Record:
  - Date
  - Time
  - Subject
  - Faculty
  - Classroom

### 4. Examination Room Allocation

Room allocation should be **automatic** based on the student database.

Allocation should consider:

- Student USN/Register Number
- Semester
- Department
- Section
- Number of seats per room
- Room capacity

Teachers should be able to:

- View allocated rooms.
- Modify allocations if needed.
- Print seating arrangements.
- Export seating arrangements to PDF/Excel.

### 5. Reports (Currently Not Working)

Fix the Reports module completely.

Reports should include:

- Attendance reports
- Subject-wise attendance
- Student-wise attendance
- Daily attendance
- Monthly attendance
- Resource usage reports
- Faculty reports
- QR attendance logs
- Examination room allocation reports

Export options:

- PDF
- Excel
- CSV

---

# Student Dashboard

### 1. Timetable
Students should be able to:

- View today's timetable.
- View weekly timetable.
- Receive notifications for timetable changes.

### 2. Attendance
Students should be able to:

- View attendance percentage.
- View subject-wise attendance.
- View total classes attended.
- View absent classes.
- View attendance history.

Display:

- Progress bars
- Percentage charts
- Monthly attendance

### 3. QR Attendance
Students should:

- Scan the teacher's QR code.
- Receive confirmation after successful attendance.
- Prevent duplicate scans.
- Attendance should only work during the allowed class time.

### 4. Resources
Students should be able to access:

- Notes
- PDFs
- PPTs
- Assignments
- Videos
- Previous year question papers
- Library books/resources
- E-books
- Reference materials

Resources should be filterable by:

- Subject
- Semester
- Faculty
- Course

### 5. Examination Room
Students should be able to:

- View their allocated examination room.
- View seat number.
- View building/block.
- View floor number.
- View exam date and timing.
- Receive notifications if room allocation changes.

### 6. Reports (Currently Not Working)
Fix the Student Reports module.

Students should be able to:

- Download attendance reports.
- Download semester attendance.
- Download subject-wise reports.
- Download resource usage reports.
- View attendance analytics.

Export options:

- PDF
- Excel

---

# Admin / System Requirements

- Automatically allocate examination rooms from the student database.
- Synchronize attendance between teacher and student dashboards.
- Real-time updates for timetable, attendance, resources, and exam rooms.
- Role-based access control (Admin, Teacher, Student).
- Dashboard analytics for attendance, resources, and examination management.
- Fix all broken Reports functionality across Teacher and Student dashboards.
- Ensure QR attendance is secure, time-limited, and resistant to duplicate or fraudulent submissions.

---

# Suggested Prioritization (recommended)
1. QR attendance: secure token generation, short expiry, server-side validation, duplicate prevention.
2. Timetable CRUD and notification sync (teacher → students).
3. Attendance recording UI and reports (teacher & student views).
4. Resource uploads + categorization + notifications.
5. Examination room allocation engine + export (PDF/Excel).
6. Full reports module fixes and exports.

# Notes
- Avoid storing secrets in repository files; use environment variables.
- Build incremental unit tests for timetable conflict checks and room allocation.
- Design APIs for integrations (mobile apps, chatbot, external LMS).


