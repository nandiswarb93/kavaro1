import random, re, time, requests
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login
from django.contrib import messages

# ================= OTP ENABLE / DISABLE =================
EMAIL_OTP_ENABLED = True
MOBILE_OTP_ENABLED =False

# OTP storage
otp_storage = {}

# ================= HELPERS =================
def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(email, otp):
    send_mail(
        'Your OTP',
        f'Your OTP is: {otp}',
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )

def send_otp_sms(mobile, otp):
    url = "https://www.fast2sms.com/dev/bulkV2"
    payload = {
        "sender_id": "TXTIND",
        "message": f"Your OTP is {otp}",
        "language": "english",
        "route": "q",
        "numbers": mobile
    }
    headers = {
        "authorization": settings.FAST2SMS_API_KEY,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    try:
        requests.post(url, data=payload, headers=headers)
    except Exception as e:
        print("SMS Error:", e)

# -------   PASSWORD VALIDATION --------- #

def is_valid_password(password):
    return re.match(
        r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$',
        password
    )

def is_valid_name(name):
    return re.match(r'^[A-Za-z ]+$', name)

def base_context():
    return {
        "EMAIL_OTP_ENABLED": EMAIL_OTP_ENABLED,
        "MOBILE_OTP_ENABLED": MOBILE_OTP_ENABLED
    }

# ================= SIGNUP =================

def signup(request):
    context = {
        **base_context(),
        "errors": {}
    }

    if request.method == "POST":
        fname = request.POST.get("full_name")
        contact = request.POST.get("contact")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        errors = {}

        is_email = re.match(r"[^@]+@[^@]+\.[^@]+", contact)
        is_mobile = re.match(r'^[6-9]\d{9}$', contact)

        if not is_valid_name(fname):
            errors["full_name"] = "Only alphabets allowed"

        if not is_email and not is_mobile:
            errors["contact"] = "Enter valid Email"

        if is_email and not EMAIL_OTP_ENABLED:
            errors["contact"] = "Email OTP disabled"

        if not password or not is_valid_password(password):
            errors["password"] = "Weak password"

        if password != confirm_password:
            errors["confirm_password"] = "Passwords do not match"

        if User.objects.filter(username=contact).exists():
            errors["contact"] = "User already exists"

        if errors:
            context["errors"] = errors
            return render(request, "registration/signup.html", context)

        # OTP generate
        otp = generate_otp()
        otp_storage[contact] = {
            "otp": otp,
            "timestamp": time.time(),
            "data": {
                "name": fname,
                "password": password,
                "is_email": True
            }
        }

        send_otp_email(contact, otp)

        request.session["signup_contact"] = contact
        return redirect("base:verify_otp")

    return render(request, "registration/signup.html", context)


# -------   OTP VERIFICATION --------- #

def verify_otp(request):
    contact = request.session.get("signup_contact")

    if not contact:
        return redirect("base:signup")

    context = {
        "contact": contact,
        "error": None
    }

    if request.method == "POST":
        entered_otp = request.POST.get("otp")
        data = otp_storage.get(contact)

        if not data:
            context["error"] = "No OTP found"

        elif time.time() - data["timestamp"] > 300:
            context["error"] = "OTP expired"

        elif entered_otp == data["otp"]:
            User.objects.create_user(
                username=contact,
                email=contact,
                first_name=data["data"]["name"],
                password=data["data"]["password"]
            )

            otp_storage.pop(contact)
            request.session.pop("signup_contact")

            messages.success(request, "Account created successfully")
            return redirect("base:login")

        else:
            context["error"] = "Invalid OTP"

    return render(request, "registration/verify_otp.html", context)

# ================= LOGIN PAGE LOGIC =================


def login_view(request):
    context = {
        **base_context(),
        "otp_section": False,
        "contact": None,
        "resend_disabled": True,
        "active_tab": "password"
    }

    # ================= PASSWORD LOGIN =================
    if request.method == "POST" and "password_login" in request.POST:
        contact = request.POST.get("email_or_mobile")
        password = request.POST.get("password")

        user = User.objects.filter(email=contact).first() if "@" in contact else User.objects.filter(username=contact).first()

        if user and user.check_password(password):
            auth_login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Invalid credentials")

    # ================= SEND OTP  OR GENERATING OTP =================
    elif request.method == "POST" and "send_otp" in request.POST:
        contact = request.POST.get("email_or_mobile")

        user = User.objects.filter(email=contact).first() if "@" in contact else User.objects.filter(username=contact).first()

        if not user:
            messages.error(request, "User not found")
            context["active_tab"] = "otp"
        else:
            # 🔴 Check enable/disable
            if "@" in contact and not EMAIL_OTP_ENABLED:
                messages.error(request, "Email OTP disabled")
            elif "@" not in contact and not MOBILE_OTP_ENABLED:
                messages.error(request, "Mobile OTP disabled")
            else:
                otp = generate_otp()
                otp_storage[contact] = {
                    "otp": otp,
                    "timestamp": time.time(),
                    "is_email": "@" in contact
                }

                if "@" in contact:
                    send_otp_email(contact, otp)
                else:
                    send_otp_sms(contact, otp)

                context.update({
                    "otp_section": True,
                    "contact": contact,
                    "active_tab": "otp"
                })
                messages.success(request, "OTP sent")

    # ================= OTP VERIFICATION  =================
    elif request.method == "POST" and "verify" in request.POST:
        contact = request.POST.get("contact")
        otp_entered = request.POST.get("otp")

        data = otp_storage.get(contact)

        context.update({
            "otp_section": True,
            "contact": contact,
            "active_tab": "otp"
        })

        if not data:
            messages.error(request, "No OTP generated")

        elif time.time() - data["timestamp"] > 300:
            messages.error(request, "OTP expired")
            context["resend_disabled"] = False

        elif otp_entered == data["otp"]:
            user = User.objects.filter(email=contact).first() if data["is_email"] else User.objects.filter(username=contact).first()

            if user:
                auth_login(request, user)
                otp_storage.pop(contact)
                return redirect("home")

        else:
            messages.error(request, "Invalid OTP")

    # ================= RESEND OTP  OR REGENERATE OTP =================
    elif request.method == "POST" and "resend" in request.POST:
        contact = request.POST.get("contact")

        if contact in otp_storage and time.time() - otp_storage[contact]["timestamp"] < 60:
            wait = int(60 - (time.time() - otp_storage[contact]["timestamp"]))
            messages.error(request, f"Wait {wait}s before resend")
        else:
            otp = generate_otp()
            otp_storage[contact] = {
                "otp": otp,
                "timestamp": time.time(),
                "is_email": "@" in contact
            }

            if "@" in contact:
                send_otp_email(contact, otp)
            else:
                send_otp_sms(contact, otp)

            messages.success(request, "OTP resent")

        context.update({
            "otp_section": True,
            "contact": contact,
            "active_tab": "otp",
            "resend_disabled": True
        })

    return render(request, "registration/login.html", context)
# ================= FORGOT PASSWORD =================
def forgot_password(request):
    context = {
        **base_context(),
        "errors": {},
        "otp_section": False,
        "contact": None,
        "resend_disabled": True
    }

    # SEND OTP
    if request.method == "POST" and "send_otp" in request.POST:
        contact = request.POST.get("email_or_mobile")

        user = User.objects.filter(email=contact).first() if "@" in contact else User.objects.filter(username=contact).first()

        if not user:
            context["errors"]["contact"] = "User not found"
            return render(request, "registration/forgot_password.html", context)

        if "@" in contact and not EMAIL_OTP_ENABLED:
            context["errors"]["contact"] = "Email OTP disabled"
            return render(request, "registration/forgot_password.html", context)

        if "@" not in contact and not MOBILE_OTP_ENABLED:
            context["errors"]["contact"] = "Mobile OTP disabled"
            return render(request, "registration/forgot_password.html", context)

        otp = generate_otp()
        otp_storage[contact] = {"otp": otp, "timestamp": time.time(), "is_email": "@" in contact}

        if "@" in contact:
            send_otp_email(contact, otp)
        else:
            send_otp_sms(contact, otp)

        context.update({"otp_section": True, "contact": contact})
        messages.success(request, "OTP sent")
        return render(request, "registration/forgot_password.html", context)

    # VERIFY OTP
    if request.method == "POST" and "verify" in request.POST:
        contact = request.POST.get("contact")
        entered_otp = request.POST.get("otp")

        data = otp_storage.get(contact)

        if not data:
            context["errors"]["otp"] = "No OTP generated"
        elif time.time() - data["timestamp"] > 300:
            context["errors"]["otp"] = "OTP expired"
            context["resend_disabled"] = False
        elif entered_otp == data["otp"]:
            request.session["reset_user"] = contact
            return redirect("base:forgot_password_reset")
        else:
            context["errors"]["otp"] = "Invalid OTP"

        context.update({"otp_section": True, "contact": contact})
        return render(request, "registration/forgot_password.html", context)

    return render(request, "registration/forgot_password.html", context)

# ================= RESET PASSWORD =================

def forgot_password_reset(request):
    user_key = request.session.get("reset_user")

    if not user_key:
        return redirect("base:forgot_password")

    context = {
        **base_context(),
        "errors": {}
    }

    if request.method == "POST":
        new_password = request.POST.get("new_password")       # match template name
        confirm_password = request.POST.get("confirm_password")

        if not new_password or not confirm_password:
            context["errors"]["password"] = ""

        elif new_password != confirm_password:
            context["errors"]["confirm_password"] = "Passwords do not match"

        elif not is_valid_password(new_password):
            context["errors"]["password"] = "Password must be 8+ chars, 1 uppercase, 1 lowercase, 1 number & 1 special char"

        if context["errors"]:
            return render(request, "registration/forgot_password_reset.html", context)

        # Update user password
        user = User.objects.filter(email=user_key).first() if "@" in user_key else User.objects.filter(username=user_key).first()
        if user:
            user.set_password(new_password)
            user.save()

        otp_storage.pop(user_key, None)
        request.session.pop("reset_user", None)

        messages.success(request, "Password reset successful")
        return redirect("base:login")

    return render(request, "registration/forgot_password_reset.html", context)
# ================= LOGIN OPTIONS =================

def login_options(request):
    return render(request, "login_options.html")