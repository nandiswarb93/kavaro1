from django.core.management.base import BaseCommand
from emailapp.utils import send_scheduled_announcements

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        send_scheduled_announcements()
