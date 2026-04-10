# from django.db import models
# from django.contrib.auth.models import AbstractUser
# import uuid
# from datetime import datetime, timedelta

# class TempOTP(models.Model):
#     email = models.EmailField(unique=True)
#     mobile = models.CharField(max_length=15, unique=True)
#     email_otp = models.CharField(max_length=6)
#     mobile_otp = models.CharField(max_length=6)
#     created_at = models.DateTimeField(auto_now_add=True)
#     verified = models.BooleanField(default=False)

#     def is_expired(self):
#         return datetime.now() > self.created_at + timedelta(minutes=10)




from django.db import models
from django.utils import timezone
from datetime import timedelta


class TempOTP(models.Model):
    contact = models.CharField(max_length=100, unique=True)  # email OR mobile
    email_otp = models.CharField(max_length=6, null=True, blank=True)
    mobile_otp = models.CharField(max_length=6, null=True, blank=True)

    is_email = models.BooleanField(default=False)
    is_mobile = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=5)

    def __str__(self):
        return self.contact