from rest_framework import serializers

from habits.models import Habit
from habits.validators import (
    validate_no_reward_and_related_habit,
    validate_period_between_1_and_7_days,
    validate_pleasant_habit_no_reward_or_related,
    validate_related_habit_is_pleasant,
    validate_time_to_action_max_120_seconds,
)


class HabitSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.email')

    class Meta:
        model = Habit
        fields = "__all__"

    # Фильтрация полей для публичных привычек
    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")

        # Если привычка не публичная и пользователь не владелец, скрываем чувствительные данные
        if not instance.is_published and instance.owner != request.user:
            # Скрываем поля, которые могут раскрыть личную информацию
            sensitive_fields = ["reward", "related_habit", "owner"]
            for field in sensitive_fields:
                if field in data:
                    data[field] = None
        return data

    # Применяем все валидаторы последовательно
    def validate(self, data):
        data = validate_no_reward_and_related_habit(data)
        data = validate_time_to_action_max_120_seconds(data)
        data = validate_related_habit_is_pleasant(data)
        data = validate_pleasant_habit_no_reward_or_related(data)
        data = validate_period_between_1_and_7_days(data)
        return data
