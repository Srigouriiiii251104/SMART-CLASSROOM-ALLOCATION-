# Project Report

## 1. Introduction

The Smart Classroom Allocation and Resource Management System is a full-stack academic operations platform designed to digitize classroom scheduling, resource booking, attendance capture, exam hall planning, and reporting. It addresses inefficiencies in manual campus coordination by combining automation, dashboards, and AI-style assistance in a single Django application.

## 2. Problem Statement

Traditional classroom management often relies on spreadsheets and manual coordination, which leads to:

- Room clashes
- Faculty overlap
- Poor resource utilization
- Slow attendance processing
- Difficult exam hall planning
- Limited reporting and analytics

## 3. Objectives

- Build a role-based web application for academic operations
- Automate timetable generation and classroom allocation
- Enable QR-based attendance and classroom access
- Manage projectors, labs, and smart devices efficiently
- Automate exam hall and seating arrangements
- Generate institutional reports and analytics

## 4. Scope

The project covers:

- Admin, faculty, and student portals
- Classroom and timetable management
- Resource booking and maintenance
- Attendance capture
- Exam seating automation
- Dashboard analytics
- PDF report generation
- AI chatbot and optional voice assistant

## 5. Methodology

- Requirement analysis
- Entity design and modular Django app planning
- Backend development with Django and DRF
- Frontend dashboard development with Bootstrap and JavaScript
- Heuristic scheduling logic for clash-free allocation
- Reporting and analytics integration
- Testing and validation

## 6. Modules

### Authentication Module

Supports role-based login, password reset, and secure access.

### Dashboard Module

Displays room usage, timetable summary, notifications, reports, and analytics.

### Classroom Allocation Module

Stores room capacities, smart room features, and QR codes.

### Timetable Generator

Uses a heuristic conflict-aware scheduler to assign rooms and time slots.

### Resource Management Module

Tracks equipment, bookings, availability, and maintenance records.

### Attendance Module

Handles manual and QR-based attendance with analytics-ready storage.

### Exam Allocation Module

Allocates halls, creates seating charts, and assigns invigilators.

### Report Module

Generates PDF exports for management and academic review.

### AI Assistant Module

Responds to common timetable and room availability queries.

## 7. Results

The implemented system provides:

- A modular full-stack Django codebase
- Working dashboards and management pages
- Automatic timetable generation
- QR attendance workflow
- Exam hall allocation and seating generation
- PDF export support
- Supporting academic documentation for final-year submission

## 8. Future Enhancements

- Live WebSocket updates
- Full NLP chatbot backed by LLM APIs
- Face recognition attendance with anti-spoofing
- SMS provider integration
- Mobile app companion
- Advanced optimization using OR-Tools

## 9. Conclusion

This project demonstrates how intelligent automation can improve classroom utilization, reduce scheduling conflicts, streamline academic administration, and provide actionable insights through a professional web platform.
