from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from accounts.models import User
from attendance.models import AttendanceSession, AttendanceRecord
from academics.models import Course, Department, Program, Term, CourseOffering, Classroom, TimeSlot

class QRAttendanceTests(TestCase):
    def setUp(self):
        # create users
        self.admin = User.objects.create_user(username='admin2', password='adminpass', role=User.ROLE_ADMIN)
        self.faculty = User.objects.create_user(username='fac2', password='facpass', role=User.ROLE_FACULTY)
        self.student = User.objects.create_user(username='stu2', password='stupass', role=User.ROLE_STUDENT)

        # basic academic objects
        dep = Department.objects.create(code='CSE', name='CSE')
        prog = Program.objects.create(code='MCA', name='MCA', department=dep)
        term = Term.objects.create(name='T1', start_date=timezone.now().date()-timedelta(days=1), end_date=timezone.now().date()+timedelta(days=100), is_active=True)
        course = Course.objects.create(department=dep, program=prog, code='MCA999', title='Test Course')
        classroom = Classroom.objects.create(name='A-1', building='B', capacity=30)
        timeslot = TimeSlot.objects.create(day_of_week=0, start_time='09:00', end_time='10:00')
        offering = CourseOffering.objects.create(course=course, faculty=self.faculty, term=term, section='A')
        self.session = AttendanceSession.objects.create(timetable_entry=offering.timetable_entries.create(classroom=classroom, timeslot=timeslot, offering=offering), session_date=timezone.now().date(), created_by=self.faculty)

        # enroll student
        offering.enrollments.create(student=self.student)

        self.client = Client()

    def test_generate_qr_rate_limit(self):
        self.client.login(username='fac2', password='facpass')
        url = reverse('attendance:api_generate_qr')
        data = {'session_id': self.session.pk, 'duration': 60}
        for i in range(3):
            resp = self.client.post(url, data, content_type='application/json')
            self.assertEqual(resp.status_code, 200)
        # 4th should be rate limited
        resp = self.client.post(url, data, content_type='application/json')
        self.assertEqual(resp.status_code, 429)

    def test_qr_expiry_and_mark(self):
        # generate QR with short duration
        self.client.login(username='fac2', password='facpass')
        url = reverse('attendance:api_generate_qr')
        resp = self.client.post(url, {'session_id': self.session.pk, 'duration': 1}, content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        token = data['qr_token']
        # expire the token manually
        self.session.qr_expires_at = timezone.now() - timedelta(seconds=1)
        self.session.save()
        # student attempts to mark
        self.client.login(username='stu2', password='stupass')
        mark_url = reverse('attendance:api_mark')
        resp2 = self.client.post(mark_url, {'qr_token': token}, content_type='application/json')
        self.assertEqual(resp2.status_code, 400)

    def test_duplicate_scan_idempotent(self):
        self.client.login(username='fac2', password='facpass')
        gen_url = reverse('attendance:api_generate_qr')
        resp = self.client.post(gen_url, {'session_id': self.session.pk, 'duration': 60}, content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        token = resp.json()['qr_token']
        self.client.login(username='stu2', password='stupass')
        mark_url = reverse('attendance:api_mark')
        resp1 = self.client.post(mark_url, {'qr_token': token}, content_type='application/json')
        self.assertEqual(resp1.status_code, 201)
        resp2 = self.client.post(mark_url, {'qr_token': token}, content_type='application/json')
        # second call should succeed and not create duplicate records
        self.assertEqual(resp2.status_code, 201)
        records = AttendanceRecord.objects.filter(session=self.session, student=self.student)
        self.assertEqual(records.count(), 1)

    def test_student_cannot_generate_qr(self):
        self.client.login(username='stu2', password='stupass')
        url = reverse('attendance:api_generate_qr')
        resp = self.client.post(url, {'session_id': self.session.pk}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)

    def test_student_cannot_mark_manually(self):
        self.client.login(username='stu2', password='stupass')
        url = reverse('attendance:api_mark')
        resp = self.client.post(url, {'session_id': self.session.pk}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)

    def test_student_cannot_mark_uninitiated_token(self):
        token = self.session.qr_token
        self.client.login(username='stu2', password='stupass')
        url = reverse('attendance:api_mark')
        resp = self.client.post(url, {'qr_token': str(token)}, content_type='application/json')
        self.assertEqual(resp.status_code, 400)

    def test_qr_analytics_csv_export(self):
        self.client.login(username='admin2', password='adminpass')
        url = reverse('attendance:qr_analytics')
        # create a log entry so export has content
        self.session.qr_logs.create(requested_by=self.admin, ip_address='127.0.0.1')
        resp = self.client.post(url, {
            'action': 'export_csv',
            'start_date': timezone.now().date().isoformat(),
            'end_date': timezone.now().date().isoformat(),
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'], 'text/csv')
        self.assertIn('qr_generation_', resp['Content-Disposition'])
        content = resp.content.decode('utf-8')
        self.assertIn('id,session_id,requested_by_id,ip_address,created_at', content)
        self.assertIn('127.0.0.1', content)
