from academics.models import Term
from notifications_app.models import Notification


def global_ui_context(request):
    active_term = Term.objects.filter(is_active=True).first()
    unread_notifications = 0
    theme = request.session.get("theme", "light")

    if request.user.is_authenticated:
        unread_notifications = Notification.objects.filter(
            recipient=request.user,
            is_read=False,
        ).count()

    return {
        "app_name": "Smart Classroom Allocation and Resource Management System",
        "active_term": active_term,
        "ui_theme": theme,
        "unread_notifications": unread_notifications,
    }
