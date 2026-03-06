# emailapp/utils.py
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from .models import Subscription


def send_announcement_email(announcement):
    subscribers = Subscription.objects.filter(is_active=True)

    for sub in subscribers:
        html_content = render_to_string(
            "emails/announcement.html",
            {
                "title": announcement.title,
                "message": announcement.message,
                "image": announcement.image.url if announcement.image else "",
                "button_text": "View Announcement",
                "button_link": "http://127.0.0.1:8000/announcements/",
                "unsubscribe_url": f"http://127.0.0.1:8000/unsubscribe/{sub.token}/",
            }
        )

        msg = EmailMultiAlternatives(
            subject=announcement.title,
            body="",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[sub.email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
