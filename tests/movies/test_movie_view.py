from unittest.mock import MagicMock, patch
import ipdb
from rest_framework.test import APITestCase
from rest_framework.views import status
from movies.models import Movie

from tests.factories import (
    create_user_with_token,
    create_multiple_movies,
    create_genre_by_name,
)


class MovieListCreateViewTest(APITestCase):
    """
    Classe para testar criação e listagem de filmes (critico, não critico)
    """

    @classmethod
    def setUpTestData(cls) -> None:
        cls.BASE_URL = "/api/movies/"
        cls.admin, cls.admin_token = create_user_with_token(is_admin=True)
        _, cls.non_admin_token = create_user_with_token()

        # UnitTest Longer Logs
        cls.maxDiff = None

    def test_movies_listing_pagination(self):
        create_multiple_movies(quantity=4, user=self.admin)
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

    def test_movie_creation_without_token(self):
        response = self.client.post(self.BASE_URL, data={}, format="json")

        # STATUS CODE
        expected_status_code = status.HTTP_401_UNAUTHORIZED
        resulted_status_code = response.status_code

        msg = (
            "\nVerifique se o status code retornado do POST sem token "
            + f"em `{self.BASE_URL}` é {expected_status_code}"
        )
        self.assertEqual(expected_status_code, resulted_status_code, msg)

    def test_movies_creation_with_non_admin_token(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.non_admin_token)
        response = self.client.post(self.BASE_URL, data={}, format="json")

        # STATUS CODE
        expected_status_code = status.HTTP_403_FORBIDDEN
        result_status_code = response.status_code
        msg = (
            "\nVerifique se o status code retornado do POST "
            + f"em `{self.BASE_URL}` com token de não admin é {expected_status_code}"
        )
        self.assertEqual(expected_status_code, result_status_code, msg)

    def test_movie_creation_without_required_fields(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.admin_token)
        response = self.client.post(self.BASE_URL, data={}, format="json")

        # RETORNO JSON
        resulted_data: dict = response.json()
        expected_data = {
            "title": ["This field is required."],
            "duration": ["This field is required."],
            "premiere": ["This field is required."],
            "budget": ["This field is required."],
            "genres": ["This field is required."],
        }
        msg = "\nVerifique as chaves obrigatórias ao tentar criar um filme."
        self.assertDictEqual(expected_data, resulted_data, msg)

        # STATUS CODE
        expected_status_code = status.HTTP_400_BAD_REQUEST
        resulted_status_code = response.status_code
        msg = (
            "Verifique se o status code retornado do POST sem todos os campos obrigatórios "
            + f"em `{self.BASE_URL}` é {expected_status_code}."
        )
        self.assertEqual(expected_status_code, resulted_status_code, msg)

    def test_movie_creation_with_admin_token(self):
        genre_1_name = "Crime"
        genre_2_name = "Drama"

        genre_1 = create_genre_by_name(genre_1_name)
        genre_2 = create_genre_by_name(genre_2_name)

        movie_data = {
            "title": "O Poderoso Chefão 2",
            # HH:MM:SS
            "duration": "01:50:00",
            "premiere": "1972-09-10",
            "budget": "13000000.00",
            "genres": [{"name": genre_1_name}, {"name": genre_2_name}],
        }
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.admin_token)
        response = self.client.post(self.BASE_URL, data=movie_data, format="json")

        added_movie = Movie.objects.last()
        added_genre_1_pk = str(added_movie.genres.get(name=genre_1_name).pk)
        added_genre_2_pk = str(added_movie.genres.get(name=genre_2_name).pk)
        # RETORNO JSON
        expected_data = {
            "id": str(added_movie.pk),
            "title": "O Poderoso Chefão 2",
            "duration": "01:50:00",
            "premiere": "1972-09-10",
            "budget": "13000000.00",
            "overview": None,
            "genres": [
                {
                    "id": added_genre_1_pk,
                    "name": genre_1_name,
                },
                {
                    "id": added_genre_2_pk,
                    "name": genre_2_name,
                },
            ],
        }

        resulted_data = response.json()
        msg = (
            "\nVerifique se as informações do filme retornadas no POST "
            + f"em `{self.BASE_URL}` com dados válidos estão corretas."
        )
        self.assertDictEqual(expected_data, resulted_data, msg)

        msg = "\nVerifique se o gênero é pego do banco se já existir"
        self.assertEqual(added_genre_1_pk, str(genre_1.pk), msg)
        self.assertEqual(added_genre_2_pk, str(genre_2.pk), msg)

        # STATUS CODE
        expected_status_code = status.HTTP_201_CREATED
        result_status_code = response.status_code
        msg = (
            "\nVerifique se o status code retornado do POST "
            + f"em `{self.BASE_URL}` com dados validos é {expected_status_code}"
        )
        self.assertEqual(expected_status_code, result_status_code, msg)
