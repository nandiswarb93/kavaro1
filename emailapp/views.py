from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.shortcuts import redirect
from django.contrib import messages

from .models import Subscription


# =========================
# SUBSCRIBE PAGE
# =========================
def subscribe_page(request):
    return render(request, "landing/landing.html")


from django.conf import settings
from django.db import IntegrityError

from django.core.validators import validate_email
from django.core.exceptions import ValidationError

def save_email(request):
    if request.method == "POST":
        email = request.POST.get("email")
        current_page = request.META.get('HTTP_REFERER', '/')

        if not email:
            messages.error(request, "Email is required.")
            return redirect(current_page)

        # ✅ Email format validation
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Enter a valid email address.")
            return redirect(current_page)

        # 🔥 Avoid duplicate crash
        subscription, created = Subscription.objects.get_or_create(
            email=email
        )

        if not created and subscription.is_active:
            messages.info(request, "You are already subscribed 😊")
            return redirect(current_page)

        if not created and not subscription.is_active:
            subscription.is_active = True
            subscription.unsubscribed_at = None
            subscription.save()

        # ✅ Send Email
        subject = "Thanks for Subscribing 🎉"

        html_content = render_to_string("emails/welcome.html", {
            "email": email,
            "unsubscribe_link": request.build_absolute_uri(
                f"/unsubscribe/{subscription.token}/"
            )
        })

        email_message = EmailMultiAlternatives(
            subject,
            "",
            settings.EMAIL_HOST_USER,
            [email]
        )

        email_message.attach_alternative(html_content, "text/html")
        email_message.send()

        messages.success(request, "Subscribed successfully 🎉")

        return redirect(current_page)

# =========================
# UNSUBSCRIBE (CONFIRM + ACTION)
# =========================
def unsubscribe(request, token):
    sub = get_object_or_404(Subscription, token=token)

    # POST = confirm unsubscribe
    if request.method == "POST":
        if sub.is_active:
            sub.is_active = False
            sub.unsubscribed_at = timezone.now()
            sub.save()

        return render(request, "emails/unsubscribed.html", {"email": sub.email})

    # GET = show confirmation page
    return render(request, "emails/unsubscribe_confirm.html", {"email": sub.email})
