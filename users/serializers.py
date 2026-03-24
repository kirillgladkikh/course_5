from rest_framework import serializers

from users.models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={"input_type": "password"}, label="Пароль")
    confirm_password = serializers.CharField(
        write_only=True, style={"input_type": "password"}, label="Подтверждение пароля"
    )

    class Meta:
        model = User
        fields = ["email", "password", "confirm_password", "phone", "country", "tg_id"]

    def validate(self, data):
        password = data.get("password")
        confirm_password = data.get("confirm_password")

        if password != confirm_password:
            raise serializers.ValidationError({"confirm_password": "Пароли не совпадают."})

        # Удаляем confirm_password из данных перед сохранением
        data.pop("confirm_password", None)
        return data

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = super().create(validated_data)  # Создаём пользователя без пароля
        user.set_password(password)  # Устанавливаем и хэшируем пароль
        user.save()
        return user
