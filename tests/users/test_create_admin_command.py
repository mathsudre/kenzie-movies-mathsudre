from io import StringIO

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User as UserType
from django.core.management import base, call_command
from django.test import TestCase


User: UserType = get_user_model()


class CreateAdminCommandTest(TestCase):
    def test_create_admin_command_output_message_on_success(self):
        out = StringIO()
        call_command("create_admin", stdout=out)
        self.assertIn("Admin `admin` successfully created!", out.getvalue())

    def test_create_admin_duplicated_username(self):
        User.objects.create_superuser(
            username="admin", email="admin@example.com", password="admin"
        )

        with self.assertRaises(base.CommandError) as err:
            call_command("create_admin")

        returned_error_message = err.exception.args[0]
        expected_error_message = "Username `admin` already taken."
        msg = "Verifique se a mensagem ao tentar criar um admin com username já existente está correta"

        self.assertEqual(expected_error_message, returned_error_message, msg)

    def test_create_admin_duplicated_email(self):
        User.objects.create_superuser(
            username="admin2", email="admin@example.com", password="admin"
        )

        with self.assertRaises(base.CommandError) as err:
            call_command("create_admin")

        returned_error_message = err.exception.args[0]
        expected_error_message = "Email `admin@example.com` already taken."
        msg = "Verifique se a mensagem ao tentar criar um admin com username já existente está correta"

        self.assertEqual(expected_error_message, returned_error_message, msg)

    def test_create_admin_with_all_optional_args(self):
        opt_args = {"username": "gohan", "password": "1234", "email": "gohan@son.com"}
        call_command("create_admin", **opt_args)

        added_admin = User.objects.last()

        msg = "Verifique se o username do admin via comando foi criado corretamente"
        self.assertEqual(added_admin.username, opt_args["username"], msg)

        msg = "Verifique se o email do admin via comando foi criado corretamente"
        self.assertEqual(added_admin.email, opt_args["email"], msg)

        msg = "Verifique se a senha do admin via comando foi hasheada corretamente"
        self.assertTrue(added_admin.check_password(opt_args["password"]))

        msg = "Verifique se o usuario criado via comando é um admin"
        self.assertTrue(added_admin.is_superuser)

    def test_create_admin_without_args(self):
        default_values = {
            "username": "admin",
            "password": "admin1234",
            "email": "admin@example.com",
        }
        call_command("create_admin")

        added_admin = User.objects.last()

        msg = "Verifique se o username do admin via comando foi criado corretamente"
        self.assertEqual(added_admin.username, default_values["username"], msg)

        msg = "Verifique se o email do admin via comando foi criado corretamente"
        self.assertEqual(added_admin.email, default_values["email"], msg)

        msg = "Verifique se a senha do admin via comando foi hasheada corretamente"
        self.assertTrue(added_admin.check_password(default_values["password"]))

        msg = "Verifique se o usuario criado via comando é um admin"
        self.assertTrue(added_admin.is_superuser)
