# Viva Questions

## Technical Questions

1. Why did you choose Django for this project?
2. Why is a custom user model better than Django’s default user in this case?
3. How does the timetable generator avoid room and faculty clashes?
4. How is QR-based attendance implemented?
5. How does the resource booking module prevent overlapping reservations?
6. How does the system support PostgreSQL and MySQL in addition to SQLite?
7. Why did you separate the project into multiple Django apps?
8. What security measures are implemented in the application?
9. How are PDF reports generated?
10. How would you extend this project with face recognition in production?

## Conceptual Answers

1. Django gives rapid development, built-in authentication, ORM safety, and strong scalability.
2. A custom user model lets us model admin, faculty, and student roles cleanly.
3. The scheduler uses a conflict-aware heuristic that checks room usage, faculty overlap, capacity, and smart/lab needs.
4. Each attendance session generates a unique QR token and QR image that maps back to a secure attendance session record.
5. The booking model validates overlapping time ranges and available quantity before saving.
6. Database engine selection is environment-driven through Django settings.
7. Separate apps improve maintainability, testability, and modular development.
8. The project uses password hashing, CSRF protection, role checks, input validation, and ORM-based query protection.
9. ReportLab is used to render downloadable PDFs on demand.
10. Face recognition can be plugged into the attendance workflow using OpenCV and a verified student image pipeline.
