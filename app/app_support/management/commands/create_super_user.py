from django.contrib.auth import get_user_model
from django.contrib.auth.management.commands import createsuperuser
from django.core.management import CommandError

User = get_user_model()


class Command(createsuperuser.Command):
    """
        Using this command, you can set a password when creating a superuser in one line
    """

    help = 'Create a superuser, and allow password to be provided.'

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            '--password', dest='password', default=None,
            help='Specifies the password for the superuser.',
        )

    def handle(self, *args, **kwargs):
        """
            Kwargs processing. Takes the necessary data from the input.
        """

        password = kwargs.get('password')
        username = kwargs.get('username')
        email = kwargs.get('email')
        database = kwargs.get('database')
        required_fields = [User.USERNAME_FIELD].extend(User.REQUIRED_FIELDS)
        errors = []

        if not username and 'username' in required_fields:
            errors.append('username')
        if not email and 'email' in required_fields:
            errors.append('email')

        if errors:
            raise CommandError(f"required fields: {errors}")

        super(Command, self).handle(*args, **kwargs)

        if password:
            user = self.UserModel._default_manager.db_manager(database).get(username=username)
            user.set_password(password)
            user.save()
