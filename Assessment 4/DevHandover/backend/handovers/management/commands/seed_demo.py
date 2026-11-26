import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create demo accounts. Hosted deployments require an explicit demo password."

    def handle(self, *args, **kwargs):
        password = os.environ.get("DEVHANDOVER_DEMO_PASSWORD")
        if not settings.DEBUG and (not password or len(password) < 20 or password == "DemoPass123!"):
            raise CommandError("Set a demo password of at least 20 characters.")
        password = password or "DemoPass123!"

        User = get_user_model()
        group, _ = Group.objects.get_or_create(name="handover_managers")
        for username in ("manager", "outgoing", "incoming"):
            user, created = User.objects.get_or_create(username=username)
            if created:
                user.set_password(password)
                user.save(update_fields=["password"])
            if username == "manager":
                user.groups.add(group)
            self.stdout.write(f"{username}: {'created' if created else 'already exists'}")
