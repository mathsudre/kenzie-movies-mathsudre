from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import User


class UserSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    username = serializers.CharField(
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="A user with that username already exists.",
            )
        ]
    )
    email = serializers.EmailField(
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="user with this email already exists.",
            )
        ],
    )
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    bio = serializers.CharField(default=None)
    is_critic = serializers.BooleanField(default=False)
    is_superuser = serializers.BooleanField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data: dict) -> User:
        return User.objects.create_user(**validated_data)
