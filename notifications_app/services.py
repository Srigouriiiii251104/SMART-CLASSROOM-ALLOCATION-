import json
import os
from urllib import request

from django.conf import settings
from django.core.mail import send_mail

from accounts.models import User

from .models import Announcement, Notification


def create_notification(recipient, title: str, message: str, category: str = "general", link: str = ""):
    return Notification.objects.create(
        recipient=recipient,
        title=title,
        message=message,
        category=category,
        link=link,
    )


def broadcast_announcement(announcement: Announcement):
    recipients = User.objects.all()
    if announcement.audience == Announcement.AUDIENCE_FACULTY:
        recipients = recipients.filter(role=User.ROLE_FACULTY)
    elif announcement.audience == Announcement.AUDIENCE_STUDENTS:
        recipients = recipients.filter(role=User.ROLE_STUDENT)

    for user in recipients:
        create_notification(user, announcement.title, announcement.message, category="announcement")


def send_email_notification(notification: Notification):
    if not notification.recipient.email:
        return
    send_mail(
        subject=notification.title,
        message=notification.message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[notification.recipient.email],
        fail_silently=True,
    )


def send_sms_notification(notification: Notification):
    webhook_url = os.getenv("SMS_WEBHOOK_URL")
    if not webhook_url:
        return
    payload = json.dumps(
        {
            "to": notification.recipient.phone_number,
            "message": f"{notification.title}: {notification.message}",
        }
    ).encode("utf-8")
    http_request = request.Request(webhook_url, data=payload, headers={"Content-Type": "application/json"})
    request.urlopen(http_request, timeout=5)


def send_telegram_notification(notification: Notification):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not bot_token or not chat_id:
        return
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = json.dumps({"chat_id": chat_id, "text": f"{notification.title}\n{notification.message}"}).encode("utf-8")
    http_request = request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    request.urlopen(http_request, timeout=5)
