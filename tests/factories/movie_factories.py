from movies.models import Movie
from .user_factories import create_user_with_token
from django.contrib.auth.models import User as UserType
from datetime import timedelta


def create_multiple_movies(quantity: int, user: UserType) -> list[Movie]:
    movies_data = [
        {
            "title": f"Movie {index}",
            "duration": timedelta(hours=2, minutes=40, seconds=30),
            "premiere": "2014-11-05",
            "budget": "165000000.00",
            "user": user,
        }
        for index in range(1, quantity + 1)
    ]

    movies_objects = [Movie(**movie_data) for movie_data in movies_data]
    movies = Movie.objects.bulk_create(movies_objects)

    return movies
