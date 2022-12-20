from genres.models import Genre


def create_genre_by_name(genre_name: dict = None) -> Genre:
    """
    Cria um usuário comum e retorna-o juntamente com seu token de acesso JWT.
    Se passado is_admin, cria um usuário admin
    """
    default_genre_name = "Genre X"
    genre_data = {"name": genre_name or default_genre_name}

    genre = Genre.objects.create(**genre_data)

    return genre
