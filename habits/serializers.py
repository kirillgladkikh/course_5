from rest_framework import serializers
from habits.models import Habit


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = '__all__'

    # Базовые ограничения целостности данных прописали в методе clean в habits/models.py
    # Кросс‑полевую валидацию прописали в сериализаторе
    def validate(self, data):
        is_pleasant = data.get('is_pleasant', False)
        reward = data.get('reward')
        related_habit = data.get('related_habit')

        errors = {}  # Будем собирать все ошибки и только потом выводить их

        # 1. Приятная привычка не может иметь вознаграждения или связанной привычки
        if is_pleasant and (reward or related_habit):
            errors['is_pleasant'] = (
                "У приятной привычки не может быть вознаграждения или связанной привычки."
            )

        # 2. Нельзя одновременно указать вознаграждение и связанную привычку
        if reward and related_habit:
            errors['reward'] = (
                "Нельзя одновременно указать вознаграждение и связанную привычку."
            )

        # 3. Связанная привычка должна быть приятной
        if related_habit and not related_habit.is_pleasant:
            errors['related_habit'] = (
                "Связанная привычка должна иметь признак приятной привычки."
            )

        # Если есть ошибки, выбрасываем исключение с полным списком
        if errors:
            raise serializers.ValidationError(errors)

        return data
