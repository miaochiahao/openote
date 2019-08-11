import argparse
import getpass

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError


class PasswordPromptAction(argparse.Action):
    def __init__(self,
                 option_strings,
                 dest=None,
                 nargs=0,
                 default=None,
                 required=False,
                 type=None,
                 metavar=None,
                 help=None):
        super(PasswordPromptAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=nargs,
            default=default,
            required=required,
            metavar=metavar,
            type=type,
            help=help)

    def __call__(self, parser, args, values, option_string=None):
        password = getpass.getpass()
        setattr(args, self.dest, password)


class Command(BaseCommand):
    help = "Create common user."

    def add_arguments(self, parser):
        parser.add_argument('-u', dest='username', type=str, required=True)
        parser.add_argument('-p', dest='password', action=PasswordPromptAction, type=str, required=True)

    def handle(self, *args, **options):
        try:
            username = options['username']
            password = options['password']
        except Exception:
            raise CommandError("Create User: python3 manage.py createuser -u <username> -p ")

        user = User.objects.create_user(username, None, password)
        user.save()
        self.stdout.write("[+] Create user [{}] successfully.".format(username))
