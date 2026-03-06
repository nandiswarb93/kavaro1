# from django.db import models
# import uuid

# class Subscription(models.Model):
#     email = models.EmailField(unique=True)
#     is_active = models.BooleanField(default=True)
#     token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
#     subscribed_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.email


# class Announcement(models.Model):
#     title = models.CharField(max_length=200)
#     message = models.TextField()

#     # OPTION 1: Upload image
#     image = models.ImageField(upload_to="announcements/", blank=True, null=True)

#     # OPTION 2: External image URL
#     image_url = models.URLField(blank=True, null=True)

#     send_at = models.DateTimeField(auto_now_add=True)
#     is_sent = models.BooleanField(default=False)

#     def __str__(self):
#         return self.title
# models.py

from django.db import models
import uuid

class Subscription(models.Model):
    name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    

    is_active = models.BooleanField(default=True)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return self.email


class Announcement(models.Model):
    title = models.CharField(max_length=200)
    message = models.TextField()
    image = models.ImageField(upload_to="announcements/", blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)  # optional URL
    send_at = models.DateTimeField(null=True, blank=True)  # ✅ allow empty for existing rows
    is_sent = models.BooleanField(default=False)
    is_important = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
