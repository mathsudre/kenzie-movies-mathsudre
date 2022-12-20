from django.contrib.auth import get_user_model
from django.contrib.auth.models import User as UserType
from rest_framework.test import APITestCase
from rest_framework.views import status

from tests.factories.user_factories import create_user_with_token

User: UserType = get_user_model()


class UserLoginViewTest(APITestCase):
    """
    Classe para testar login de usuários
    """

    @classmethod
    def setUpTestData(cls) -> None:
        cls.BASE_URL = "/api/login/"

        # UnitTest Longer Logs
        cls.maxDiff = None

    def test_user_login_without_required_fields(self):
        response = self.client.post(self.BASE_URL, data={}, format="json")

        # RETORNO JSON
        resulted_data: dict = response.json()
        expected_data = {
            "username": ["This field is required."],
            "password": ["This field is required."],
        }

        msg = "\nVerifique as chaves obrigatórias ao tentar logar um usuário."
        self.assertDictEqual(expected_data, resulted_data, msg)

        # STATUS CODE
        expected_status_code = status.HTTP_400_BAD_REQUEST
        returned_status_code = response.status_code
        msg = (
            "\nVerifique se o status code retornado do POST sem todos os campos obrigatórios "
            + f"em `{self.BASE_URL}` é {expected_status_code}."
        )
        self.assertEqual(expected_status_code, returned_status_code, msg)

    def test_login_success(self):
        register_data = {
            "username": "lucira_buster",
            "email": "lucira_buster@kenziebuster.com",
            "first_name": "Lucira",
            "last_name": "Buster",
            "password": "1313",
        }
        # Criando usuário para logar
        create_user_with_token(register_data)

        login_data = {
            "username": "lucira_buster",
            "password": "1313",
        }
        response = self.client.post(self.BASE_URL, data=login_data, format="json")

        # RETORNO JSON
        expected_keys = {"access", "refresh"}
        returned_keys = set(response.json().keys())
        msg = (
            "Verifique se tanto o access token quanto o refresh token estão "
            + f"sendo retornados corretamente do login em `{self.BASE_URL}`"
        )
        self.assertSetEqual(expected_keys, returned_keys, msg)

        # STATUS CODE
        expected_status_code = status.HTTP_200_OK
        returned_status_code = response.status_code
        msg = (
            "Verifique se o status code retornado do POST "
            + f"em `{self.BASE_URL}` é {expected_status_code}"
        )
        self.assertEqual(expected_status_code, returned_status_code, msg)

    def test_login_with_wrong_credentials(self):
        login_data = {
            "username": "lucira_buster_non_existent",
            "password": "11111111111111111",
        }
        response = self.client.post(self.BASE_URL, data=login_data, format="json")

        # STATUS CODE
        expected_status_code = status.HTTP_401_UNAUTHORIZED
        returned_status_code = response.status_code
        msg = (
            "Verifique se o status code retornado do POST com credenciais inválidas"
            + f"em `{self.BASE_URL}` é {expected_status_code}"
        )
        self.assertEqual(expected_status_code, returned_status_code, msg)

        # RETORNO JSON
        returned_data: dict = response.json()
        expected_data = {"detail": "No active account found with the given credentials"}
        msg = "Verifique se a mensagem ao logar com credenciais inválidas está correta"
        self.assertDictEqual(expected_data, returned_data, msg)
