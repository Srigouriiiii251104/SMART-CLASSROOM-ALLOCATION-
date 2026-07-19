# Smart Classroom Allocation and Resource Management System

An advanced full-stack Django project for smart classroom scheduling, resource booking, QR-based attendance, exam hall allocation, analytics dashboards, PDF reporting, and AI-assisted campus queries.

## Tech Stack

- Backend: Python, Django, Django REST Framework, SimpleJWT
- Database: SQLite by default, configurable for PostgreSQL or MySQL
- Frontend: HTML, CSS, Bootstrap 5, JavaScript, Chart.js
- Reporting: ReportLab
- QR Features: `qrcode`, Pillow
- Optional AI/Voice Features: SpeechRecognition, pyttsx3, OpenCV hooks

## Core Features

- Multi-role authentication for admin, faculty, and students
- Session-based login plus JWT endpoints
- Modern analytics dashboard with charts and notifications
- Classroom CRUD, smart room metadata, QR generation, and availability checks
- AI-style timetable generation using conflict-aware scheduling heuristics
- Drag-and-drop timetable board with clash-safe move API
- Resource inventory, booking workflow, and maintenance tracking
- Attendance sessions with QR support and analytics-ready records
- Exam hall allocation with seating chart generation and invigilator assignment
- PDF exports for timetable, attendance, exams, and resources
- AI chatbot and optional voice assistant for timetable and room queries
- Dark/light mode, responsive layout, and modular project architecture

## Project Apps

- `accounts`: Custom user model, roles, profiles, login, theme toggle
- `dashboard`: Role-aware dashboards and analytics
- `academics`: Classrooms, courses, terms, enrollment, timetable engine
- `resources`: Resource booking and maintenance management
- `attendance`: Attendance sessions and QR-based marking
- `notifications_app`: In-app notifications and announcement delivery
- `exams`: Exam scheduling, hall allocation, invigilators, seating
- `reports`: PDF reports and report tracking
- `assistant_bot`: Chat assistant and optional voice interface

## Quick Start

1. Install dependencies:
   - `python -m pip install -r requirements.txt`
2. Copy environment variables:
   - `copy .env.example .env`
3. Apply migrations:
   - `python manage.py migrate`
4. Seed demo data:
   - `python manage.py seed_demo_data`
5. Start the server:
   - `python manage.py runserver`

## Demo Credentials

- Admin: `admin` / `admin123`
- Faculty: `faculty1` / `faculty123`
- Student: `student1` / `student123`

## API Highlights

- `POST /api/token/`
- `POST /api/token/refresh/`
- `GET /academics/api/timetable/`
- `POST /academics/api/timetable/generate/`
- `POST /academics/api/timetable/move/`
- `GET /resources/api/availability/`
- `POST /resources/api/bookings/`
- `POST /attendance/api/mark/`
- `POST /assistant/api/query/`

## Optional Packages

Install `requirements-optional.txt` if you want:

- Voice assistant support
- PostgreSQL/MySQL production drivers
- OpenCV-based face recognition extensions

## Verification

- `python manage.py check`
- `python manage.py makemigrations`
- `python manage.py test`

## Documentation

- [Folder Structure](docs/folder_structure.md)
- [Database Schema](docs/database_schema.md)
- [ER Diagram](docs/er_diagram.md)
- [DFD Diagram](docs/dfd_diagram.md)
- [API Documentation](docs/api_documentation.md)
- [Deployment Guide](docs/deployment_guide.md)
- [PPT Content](docs/ppt_content.md)
- [Viva Questions](docs/viva_questions.md)
- [Project Report](docs/project_report.md)
