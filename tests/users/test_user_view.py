from unittest.mock import MagicMock, patch

import ipdb
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User as UserType
from rest_framework.test import APITestCase
from rest_framework.views import status

from tests.factories import create_multiple_critic_users, create_user_with_token

# User: Type[UserType] = get_user_model()
User: UserType = get_user_model()


class UserListCreateViewTest(APITestCase):
    """
    Classe para testar criação e listagem de usuários (critico, não critico)
    """

    @classmethod
    def setUpTestData(cls) -> None:
        cls.BASE_URL = "/api/users/"

        # UnitTest Longer Logs
        cls.maxDiff = None

    def test_users_listing_pagination_with_admin_token(self):
        _, admin_token = create_user_with_token(is_admin=True)
        create_multiple_critic_users(quantity=4)

        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + admin_token)
        response = self.client.get(self.BASE_URL)

        resulted_data = response.json()

        # STATUS CODE
        expected_status_code = status.HTTP_200_OK
        result_status_code = response.status_code
        msg = (
            "\nVerifique se o status code retornado do GET "
            + f"em `{self.BASE_URL}` com token de admin é {expected_status_code}"
        )
        self.assertEqual(expected_status_code, result_status_code, msg)

        # RETORNO JSON
        expected_pagination_keys = {"count", "next", "previous", "results"}
        msg = "\nVerifique se a paginação está sendo feita corretamente"
        with self.subTest():
            for expected_key in expected_pagination_keys:
                self.assertIn(expected_key, resulted_data.keys(), msg)

        results_len = len(resulted_data["results"])
        expected_len = 4

        msg = (
            "\nVerifique se a paginação está retornando apenas quatro items de cada vez"
        )
        self.assertEqual(expected_len, results_len)

    def test_users_listing_pagination_without_token(self):
        response = self.client.get(self.BASE_URL)

        # STATUS CODE
        expected_status_code = status.HTTP_401_UNAUTHORIZED
        resulted_status_code = response.status_code

        msg = (
            "\nVerifique se o status code retornado do GET sem token "
            + f"em `{self.BASE_URL}` é {expected_status_code}"
        )
        self.assertEqual(expected_status_code, resulted_status_code, msg)

    def test_users_listing_pagination_with_non_admin_token(self):
        _, non_admin_token = create_user_with_token()

        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + non_admin_token)
        response = self.client.get(self.BASE_URL)

        # STATUS CODE
        expected_status_code = status.HTTP_403_FORBIDDEN
        result_status_code = response.status_code
        msg = (
            "\nVerifique se o status code retornado do GET "
            + f"em `{self.BASE_URL}` com token de não admin é {expected_status_code}"
        )
        self.assertEqual(expected_status_code, result_status_code, msg)

    def test_user_creation_without_required_fields(self):
        response = self.client.post(self.BASE_URL, data={}, format="json")

        # RETORNO JSON
        resulted_data: dict = response.json()
        expected_data = {
            "username": ["This field is required."],
            "email": ["This field is required."],
            "password": ["This field is required."],
            "first_name": ["This field is required."],
            "last_name": ["This field is required."],
        }
        msg = "\nVerifique as chaves obrigatórias ao tentar criar um usuário."
        self.assertDictEqual(expected_data, resulted_data, msg)

        # STATUS CODE
        expected_status_code = status.HTTP_400_BAD_REQUEST
        resulted_status_code = response.status_code
        msg = (
            "Verifique se o status code retornado do POST sem todos os campos obrigatórios "
            + f"em `{self.BASE_URL}` é {expected_status_code}."
        )
        self.assertEqual(expected_status_code, resulted_status_code, msg)

    @patch("django.utils.timezone.now", return_value="2022-11-27T17:55:22.819371Z")
    def test_critic_creation(self, mock_now: MagicMock):
        user_data = {
            "username": "lucira",
            "email": "lucira@mail.com",
            "first_name": "Lucira",
            "last_name": "Critica",
            "password": "1234",
            "is_critic": True,
        }

        response = self.client.post(self.BASE_URL, data=user_data, format="json")

        added_user = User.objects.last()

        # RETORNO JSON
        expected_data = {
            "id": str(added_user.pk),
            "username": "lucira",
            "email": "lucira@mail.com",
            "first_name": "Lucira",
            "last_name": "Critica",
            "bio": None,
            "is_critic": True,
            "is_superuser": False,
            "updated_at": mock_now.return_value,
        }
        resulted_data = response.json()
        msg = (
            "\nVerifique se as informações do usuário retornadas no POST "
            + f"em `{self.BASE_URL}` com dados válidos estão corretas."
        )
        self.assertDictEqual(expected_data, resulted_data, msg)

        # PASSWORD HASHEADO
        msg = "\nVerifique se o password está sendo hasheado corretamente."
        self.assertTrue(added_user.check_password(user_data["password"]), msg)

        # STATUS CODE
        expected_status_code = status.HTTP_201_CREATED
        result_status_code = response.status_code
        msg = (
            "\nVerifique se o status code retornado do POST "
            + f"em `{self.BASE_URL}` com dados validos é {expected_status_code}"
        )
        self.assertEqual(expected_status_code, result_status_code, msg)

    @patch("django.utils.timezone.now", return_value="2022-11-27T17:55:22.819371Z")
    def test_critic_creation_with_bio(self, mock_now: MagicMock):
        user_data = {
            "username": "raphael",
            "email": "raphael@mail.com",
            "first_name": "Raphael",
            "last_name": "Critico",
            "bio": "Uma Bio",
            "password": "1234",
            "is_critic": True,
        }

        response = self.client.post(self.BASE_URL, data=user_data, format="json")

        added_user = User.objects.last()

        # RETORNO JSON
        expected_data = {
            "id": str(added_user.pk),
            "username": "raphael",
            "email": "raphael@mail.com",
            "first_name": "Raphael",
            "last_name": "Critico",
            "bio": "Uma Bio",
            "is_critic": True,
            "is_superuser": False,
            "updated_at": mock_now.return_value,
        }
        resulted_data = response.json()
        msg = (
            "\nVerifique se as informações do usuário retornadas no POST "
            + f"em `{self.BASE_URL}` com dados validos estão corretas."
        )
        self.assertDictEqual(expected_data, resulted_data, msg)

        # PASSWORD HASHEADO
        msg = "\nVerifique se o password está sendo hasheado corretamente."
        self.assertTrue(added_user.check_password(user_data["password"]), msg)

        # STATUS CODE
        expected_status_code = status.HTTP_201_CREATED
        result_status_code = response.status_code
        msg = (
            "\nVerifique se o status code retornado do POST "
            + f"em `{self.BASE_URL}` com dados validos é {expected_status_code}."
        )
        self.assertEqual(expected_status_code, result_status_code, msg)

    @patch("django.utils.timezone.now", return_value="2022-11-27T17:55:22.819371Z")
    def test_non_critic_creation(self, mock_now: MagicMock):
        user_data = {
            "username": "alexandre",
            "email": "ale@mail.com",
            "first_name": "Ale",
            "last_name": "Nao Critico",
            "password": "1234",
        }

        response = self.client.post(self.BASE_URL, data=user_data, format="json")

        added_user = User.objects.last()

        # RETORNO JSON
        expected_data = {
            "id": str(added_user.pk),
            "username": "alexandre",
            "email": "ale@mail.com",
            "first_name": "Ale",
            "last_name": "Nao Critico",
            "bio": None,
            "is_critic": False,
            "is_superuser": False,
            "updated_at": mock_now.return_value,
        }
        resulted_data = response.json()
        msg = (
            "\nVerifique se as informações do usuário retornadas no POST "
            + f"em `{self.BASE_URL}` com dados validos estão corretas."
        )
        self.assertDictEqual(expected_data, resulted_data, msg)

        # PASSWORD HASHEADO
        msg = "\nVerifique se o password está sendo hasheado corretamente."
        self.assertTrue(added_user.check_password(user_data["password"]), msg)

        # STATUS CODE
        expected_status_code = status.HTTP_201_CREATED
        result_status_code = response.status_code
        msg = (
            "\nVerifique se o status code retornado do POST "
            + f"em `{self.BASE_URL}` com dados validos é {expected_status_code}."
        )
        self.assertEqual(expected_status_code, result_status_code, msg)

    def test_uniqueness_of_email_and_username_in_user_creation(self):
        user_data = {
            "username": "lucira",
            "email": "lucira@mail.com",
            "first_name": "Lucira",
            "last_name": "Buster",
            "password": "1234",
        }
        # Populando o banco pré testagem
        create_user_with_token(user_data)
        response = self.client.post(self.BASE_URL, data=user_data, format="json")

        # RETORNO JSON
        resulted_data = response.json()
        expected_fields = {"username", "email"}
        resulted_fields = set(resulted_data.keys())
        msg = (
            f"\nVerifique se no POST em `{self.BASE_URL}` "
            + f"um usuário pode ser criado com email e username duplicados."
        )
        self.assertSetEqual(expected_fields, resulted_fields, msg)

        # STATUS CODE
        expected_status_code = status.HTTP_400_BAD_REQUEST
        result_status_code = response.status_code
        msg = (
            "Verifique se o status code retornado do POST "
            + f"em `{self.BASE_URL}` é {expected_status_code}"
        )
        self.assertEqual(expected_status_code, result_status_code, msg)
