import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create demo accounts. Hosted deployments require an explicit demo password."

    def handle(self, *args, **kwargs):
        configured_password = os.environ.get("DEVHANDOVER_DEMO_PASSWORD")
        if not settings.DEBUG and (not configured_password or len(configured_password) < 8 or configured_password == "DemoPass123!"):
            raise CommandError("Set a private demo password of at least 8 characters.")
        password = configured_password or "DemoPass123!"

        User = get_user_model()
        group, _ = Group.objects.get_or_create(name="handover_managers")
        for username in ("manager", "outgoing", "incoming"):
            user, created = User.objects.get_or_create(username=username)
            if created or (configured_password and not user.check_password(password)):
                user.set_password(password)
                user.save(update_fields=["password"])
            if username == "manager":
                user.groups.add(group)
            self.stdout.write(f"{username}: {'created' if created else 'already exists'}")
