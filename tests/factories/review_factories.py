from movies.models import Movie
from .user_factories import create_user_with_token
from django.contrib.auth.models import User as UserType
from datetime import timedelta
from reviews.models import Review
from .faker_factory import fake


def create_multiple_reviews(
    quantity: int, movie: Movie, critic: UserType
) -> list[Review]:
    reviews_data = [
        {
            "stars": fake.pyint(min_value=1, max_value=5),
            "review": fake.sentence(),
            "spoilers": fake.pybool(),
            "movie": movie,
            "critic": critic,
        }
        for _ in range(1, quantity + 1)
    ]

    reviews_objects = [Review(**review_data) for review_data in reviews_data]
    reviews = Review.objects.bulk_create(reviews_objects)

    return reviews
