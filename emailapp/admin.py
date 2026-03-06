from django.contrib import admin
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

from .models import Subscription, Announcement


# =========================
# SUBSCRIPTION ADMIN
# =========================
@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "is_active",
        "subscribed_at",
        "unsubscribed_at",
    )
    list_filter = ("is_active",)
    search_fields = ("email",)
    readonly_fields = ("token", "subscribed_at", "unsubscribed_at")
    ordering = ("-is_active", "-subscribed_at")


# =========================
# ANNOUNCEMENT ADMIN
# =========================
@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("title", "is_important", "is_sent", "created_at")
    list_filter = ("is_sent", "is_important")
    search_fields = ("title",)
    readonly_fields = ("is_sent", "created_at")
    actions = ["send_announcement"]

    def send_announcement(self, request, queryset):
        sent_count = 0

        # ✅ Site URL (local / AWS)
        site_url = getattr(settings, "SITE_URL", None)
        if not site_url:
            site_url = request.build_absolute_uri("/").rstrip("/")

        for ann in queryset:
            if ann.is_sent:
                continue

            # ✅ IMPORTANT logic here
            if ann.is_important:
                subscribers = Subscription.objects.all()  # active + inactive
            else:
                subscribers = Subscription.objects.filter(is_active=True)

            for sub in subscribers:
                # Image
                image = None
                if ann.image:
                    image = request.build_absolute_uri(ann.image.url)
                elif ann.image_url:
                    image = ann.image_url

                html = render_to_string(
                    "emails/announcement.html",
                    {
                        "title": ann.title,
                        "message": ann.message,
                        "image": image,
                        "is_important": ann.is_important,
                        "unsubscribe_url": f"{site_url}/unsubscribe/{sub.token}/",
                    },
                )

                msg = EmailMultiAlternatives(
                    subject=f"🚨 IMPORTANT: {ann.title}" if ann.is_important else ann.title,
                    body="",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[sub.email],
                )
                msg.attach_alternative(html, "text/html")
                msg.send(fail_silently=False)

                sent_count += 1

            ann.is_sent = True
            ann.save()

        self.message_user(
            request,
            f"✅ Email sent to {sent_count} users."
        )

    send_announcement.short_description = "📢 Send Announcement Email"
