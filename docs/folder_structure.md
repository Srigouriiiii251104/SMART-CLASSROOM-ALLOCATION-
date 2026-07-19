# Folder Structure

```text
smartclassroom/
├── accounts/
├── academics/
├── assistant_bot/
├── attendance/
├── dashboard/
├── exams/
├── notifications_app/
├── reports/
├── resources/
├── smartclassroom/
├── static/
│   ├── css/
│   └── js/
├── templates/
│   ├── accounts/
│   ├── academics/
│   ├── assistant_bot/
│   ├── attendance/
│   ├── dashboard/
│   ├── exams/
│   ├── registration/
│   ├── resources/
│   └── shared/
├── docs/
├── manage.py
├── requirements.txt
├── requirements-optional.txt
└── README.md
```

## Architectural Notes

- Each business domain is separated into its own Django app.
- REST-style APIs are colocated with app-specific services and serializers.
- Templates are grouped by feature area for maintainability.
- Static assets are centralized under `static/`.
- Academic deliverables and project-writing material live under `docs/`.
