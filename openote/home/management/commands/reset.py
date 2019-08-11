from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from .createuser import PasswordPromptAction


class Command(BaseCommand):
    help = "Reset password."

    def add_arguments(self, parser):
        parser.add_argument('-u', dest='username', type=str, required=True)
        parser.add_argument('-p', dest='password', action=PasswordPromptAction, type=str, required=True)

    def handle(self, *args, **options):
        try:
            username = options['username']
            password = options['password']
        except Exception:
            raise CommandError("Create User: python3 manage.py reset -u <username> -p ")

        try:
            user = User.objects.get(username=username)
        except Exception:
            raise CommandError("No user named [{}]".format(username))

        user.set_password(password)
        user.save()
        self.stdout.write("[+] Password changed")
