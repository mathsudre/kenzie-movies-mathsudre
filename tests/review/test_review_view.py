from unittest.mock import MagicMock, patch
import ipdb
from rest_framework.test import APITestCase
from rest_framework.views import status
from movies.models import Movie
from reviews.models import Review

from tests.factories import (
    create_user_with_token,
    create_multiple_movies,
    create_genre_by_name,
    create_multiple_reviews,
)


class ReviewCreateViewTest(APITestCase):
    """
    Classe para testar criação e listagem de filmes (critico, não critico)
    """

    @classmethod
    def setUpTestData(cls) -> None:
        cls.BASE_URL = "/api/movies/%s/reviews/"
        cls.admin, cls.admin_token = create_user_with_token(is_admin=True)
        cls.critic, cls.critic_token = create_user_with_token(is_critic=True)
        _, cls.non_critic_token = create_user_with_token()

        cls.movie_1, cls.movie_2 = create_multiple_movies(quantity=2, user=cls.admin)
        cls.BASE_URL_MOVIE_1 = cls.BASE_URL % cls.movie_1.pk
        cls.BASE_URL_MOVIE_2 = cls.BASE_URL % cls.movie_2.pk
        cls.NO_MOVIE_UUID = "5b7c7f80-820c-4594-9251-4b14fa3102c4"
        cls.BASE_URL_NO_MOVIE = cls.BASE_URL % cls.NO_MOVIE_UUID

        # UnitTest Longer Logs
        cls.maxDiff = None

    def test_review_creation_without_token(self):
        response = self.client.post(self.BASE_URL_MOVIE_1, data={}, format="json")

        # STATUS CODE
        expected_status_code = status.HTTP_401_UNAUTHORIZED
        resulted_status_code = response.status_code

        msg = (
            "\nVerifique se o status code retornado do POST sem token "
            + f"em `{self.BASE_URL_MOVIE_1}` é {expected_status_code}"
        )
        self.assertEqual(expected_status_code, resulted_status_code, msg)

    def test_review_creation_with_non_critic_token(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.non_critic_token)
        response = self.client.post(self.BASE_URL_MOVIE_1, data={}, format="json")

        # STATUS CODE
        expected_status_code = status.HTTP_403_FORBIDDEN
        result_status_code = response.status_code
        msg = (
            "\nVerifique se o status code retornado do POST "
            + f"em `{self.BASE_URL_MOVIE_1}` com token de não crítico é {expected_status_code}"
        )
        self.assertEqual(expected_status_code, result_status_code, msg)

    def test_review_creation_with_not_found_movie_uuid(self):
        review_data = {
            "stars": 4,
            "review": "O Poderoso Chefão 2 podia ter dado muito errado...",
            "spoilers": False,
        }
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.critic_token)
        response = self.client.post(
            self.BASE_URL_NO_MOVIE, data=review_data, format="json"
        )

        # RETORNO JSON
        resulted_data = response.json()
        expected_data = {"detail": "Not found."}

        msg = (
            "Verifique se a mensagem com movie_id não cadastrado no POST em "
            + f"`{self.BASE_URL_NO_MOVIE}` está correta."
        )
        self.assertDictEqual(expected_data, resulted_data)

        # STATUS CODE
        expected_status_code = status.HTTP_404_NOT_FOUND
        resulted_status_code = response.status_code
        msg = (
            "\nVerifique se o status code retornado do POST "
            + f"em `{self.BASE_URL_NO_MOVIE}` com movie_id não cadastrado {expected_status_code}."
        )
        self.assertEqual(expected_status_code, resulted_status_code, msg)

    def test_review_creation_without_required_fields(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.critic_token)
        response = self.client.post(self.BASE_URL_MOVIE_1, data={}, format="json")

        # RETORNO JSON
        resulted_data: dict = response.json()
        expected_data = {
            "stars": ["This field is required."],
            "review": ["This field is required."],
        }
        msg = "\nVerifique as chaves obrigatórias ao tentar criar uma review."
        self.assertDictEqual(expected_data, resulted_data, msg)

        # STATUS CODE
        expected_status_code = status.HTTP_400_BAD_REQUEST
        resulted_status_code = response.status_code
        msg = (
            "Verifique se o status code retornado do POST sem todos os campos obrigatórios "
            + f"em `{self.BASE_URL_MOVIE_1}` é {expected_status_code}."
        )
        self.assertEqual(expected_status_code, resulted_status_code, msg)

    # PARAMOS AQUI
    def test_review_creation_with_critic_token(self):
        review_data = {
            "stars": 4,
            "review": "O Poderoso Chefão 2 podia ter dado muito errado...",
            "spoilers": False,
        }
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.critic_token)
        response = self.client.post(
            self.BASE_URL_MOVIE_1,
            data=review_data,
            format="json",
        )

        added_review = Review.objects.last()

        # RETORNO JSON
        expected_data = {
            "id": str(added_review.pk),
            **review_data,
            "movie_id": str(self.movie_1.pk),
            "critic": {
                "id": str(self.critic.pk),
                "first_name": self.critic.first_name,
                "last_name": self.critic.last_name,
            },
        }

        resulted_data = response.json()
        msg = (
            "\nVerifique se as informações da review retornadas no POST "
            + f"em `{self.BASE_URL_MOVIE_1}` com dados válidos estão corretas."
        )
        self.assertDictEqual(expected_data, resulted_data, msg)

        # STATUS CODE
        expected_status_code = status.HTTP_201_CREATED
        result_status_code = response.status_code
        msg = (
            "\nVerifique se o status code retornado do POST "
            + f"em `{self.BASE_URL_MOVIE_1}` com dados validos é {expected_status_code}"
        )
        self.assertEqual(expected_status_code, result_status_code, msg)

    def test_review_creation_with_admin_token(self):
        review_data = {
            "stars": 4,
            "review": "O Poderoso Chefão 2 podia ter dado muito errado...",
            "spoilers": False,
        }
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.admin_token)
        response = self.client.post(
            self.BASE_URL_MOVIE_1,
            data=review_data,
            format="json",
        )

        added_review = Review.objects.last()

        # RETORNO JSON
        expected_data = {
            "id": str(added_review.pk),
            **review_data,
            "movie_id": str(self.movie_1.pk),
            "critic": {
                "id": str(self.admin.pk),
                "first_name": self.admin.first_name,
                "last_name": self.admin.last_name,
            },
        }

        resulted_data = response.json()
        msg = (
            "\nVerifique se as informações da review retornadas no POST "
            + f"em `{self.BASE_URL_MOVIE_1}` com dados válidos estão corretas."
        )
        self.assertDictEqual(expected_data, resulted_data, msg)

        # STATUS CODE
        expected_status_code = status.HTTP_201_CREATED
        result_status_code = response.status_code
        msg = (
            "\nVerifique se o status code retornado do POST "
            + f"em `{self.BASE_URL_MOVIE_1}` com dados validos é {expected_status_code}"
        )
        self.assertEqual(expected_status_code, result_status_code, msg)

    def test_review_creation_with_invalid_stars(self):
        review_data = {
            "stars": 100,
            "review": "O Poderoso Chefão 2 podia ter dado muito errado...",
            "spoilers": False,
        }
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.critic_token)
        response = self.client.post(
            self.BASE_URL_MOVIE_1,
            data=review_data,
            format="json",
        )

        # RETORNO JSON
        expected_data = {"stars": ["Ensure this value is less than or equal to 5."]}

        resulted_data = response.json()
        msg = (
            "\nVerifique se é possível fazer uma review com `stars` maior que 5 "
            + f"em `{self.BASE_URL_MOVIE_1}`"
        )
        self.assertDictEqual(expected_data, resulted_data, msg)

        review_data = {
            "stars": 0,
            "review": "O Poderoso Chefão 2 podia ter dado muito errado...",
            "spoilers": False,
        }
        response = self.client.post(
            self.BASE_URL_MOVIE_1,
            data=review_data,
            format="json",
        )

        expected_data = {"stars": ["Ensure this value is greater than or equal to 1."]}
        resulted_data = response.json()
        msg = (
            "\nVerifique se é possível fazer uma review com `stars` menor que 1 "
            + f"em `{self.BASE_URL_MOVIE_1}`"
        )
        self.assertDictEqual(expected_data, resulted_data, msg)

        # STATUS CODE
        expected_status_code = status.HTTP_400_BAD_REQUEST
        result_status_code = response.status_code
        msg = (
            "\nVerifique se o status code retornado do POST "
            + f"em `{self.BASE_URL_MOVIE_1}` com dados inválidos é {expected_status_code}"
        )
        self.assertEqual(expected_status_code, result_status_code, msg)

    def test_reviews_listing_pagination(self):
        create_multiple_reviews(
            quantity=4,
            movie=self.movie_1,
            critic=self.critic,
        )

        create_multiple_reviews(
            quantity=4,
            movie=self.movie_2,
            critic=self.admin,
        )
        response = self.client.get(self.BASE_URL_MOVIE_1)

        resulted_data = response.json()

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

        # STATUS CODE
        expected_status_code = status.HTTP_200_OK
        result_status_code = response.status_code
        msg = (
            "\nVerifique se o status code retornado do GET "
            + f"em `{self.BASE_URL}` com token de admin é {expected_status_code}"
        )
        self.assertEqual(expected_status_code, result_status_code, msg)
