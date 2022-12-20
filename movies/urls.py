from django.urls import path

from . import views
from reviews import views as review_views

urlpatterns = [
    path("movies/", views.MovieView.as_view()),
    path("movies/<uuid:movie_id>/reviews/", review_views.ReviewView.as_view()),
]
