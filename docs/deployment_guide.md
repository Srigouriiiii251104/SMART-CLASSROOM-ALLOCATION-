# Deployment Guide

## Local Deployment

1. Install Python 3.12+
2. Install dependencies:
   - `python -m pip install -r requirements.txt`
3. Configure environment:
   - `copy .env.example .env`
4. Run database setup:
   - `python manage.py migrate`
5. Load demo content:
   - `python manage.py seed_demo_data`
6. Start server:
   - `python manage.py runserver`

## PostgreSQL Deployment

Set environment values:

- `DB_ENGINE=postgresql`
- `DB_NAME=smartclassroom`
- `DB_USER=postgres`
- `DB_PASSWORD=your-password`
- `DB_HOST=127.0.0.1`
- `DB_PORT=5432`

Install optional driver:

- `python -m pip install psycopg[binary]`

## MySQL Deployment

Set environment values:

- `DB_ENGINE=mysql`
- `DB_NAME=smartclassroom`
- `DB_USER=root`
- `DB_PASSWORD=your-password`
- `DB_HOST=127.0.0.1`
- `DB_PORT=3306`

Install optional driver:

- `python -m pip install mysqlclient`

## Production Notes

- Disable debug mode
- Replace the secret key
- Configure real email backend
- Use HTTPS and secure cookies
- Run `python manage.py collectstatic`
- Serve via Gunicorn/Uvicorn + Nginx on Linux or IIS/Waitress on Windows
