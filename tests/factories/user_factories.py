from django.contrib.auth import get_user_model
from django.contrib.auth.models import User as UserType
from rest_framework_simplejwt.tokens import RefreshToken
from .faker_factory import fake

User: UserType = get_user_model()


def create_user_with_token(
    user_data: dict = None,
    is_admin: bool = False,
    is_critic=False,
) -> tuple[UserType, str]:
    """
    Cria um usuário comum e retorna-o juntamente com seu token de acesso JWT.
    Se passado is_admin, cria um usuário admin
    """
    default_user_data = {
        "username": fake.unique.user_name(),
        "email": fake.unique.email(),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "password": fake.password(),
        "is_critic": is_critic,
    }

    user_data = user_data or default_user_data

    if is_admin:
        user = User.objects.create_superuser(**user_data)
    else:
        user = User.objects.create_user(**user_data)

    token: RefreshToken = RefreshToken.for_user(user)

    return user, str(token.access_token)


def create_multiple_critic_users(quantity: int) -> list[User]:
    users_data = [
        {
            "username": f"lucira_{index}",
            "email": f"lucira_{index}@mail.com",
            "first_name": "Lucira {index}",
            "last_name": "Buster",
            "password": "1234",
            "is_critic": True,
        }
        for index in range(1, quantity + 1)
    ]

    users = [User.objects.create_user(**user_data) for user_data in users_data]

    return users
