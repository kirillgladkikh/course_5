from datetime import timedelta

from rest_framework.serializers import ValidationError


def validate_no_reward_and_related_habit(value):
    """
    Проверяет, что не заполнены одновременно вознаграждение и связанная привычка.
    Валидирует только если оба поля присутствуют в данных.
    """
    reward = value.get("reward")
    related_habit = value.get("related_habit")

    # Проверяем только если оба поля переданы в запросе
    if "reward" in value and "related_habit" in value:
        if reward is not None and related_habit is not None:
            raise ValidationError(
                {"reward": "Одновременный выбор вознаграждения и связанной привычки не допускается."}
            )
    return value


def validate_time_to_action_max_120_seconds(value):
    """
    Проверяет, что время выполнения не превышает 120 секунд.
    Валидирует только если поле time_to_action присутствует в данных.
    """
    time_to_action = value.get("time_to_action")

    # Проверяем только если поле передано в запросе
    if "time_to_action" in value and time_to_action is not None:
        if time_to_action > timedelta(seconds=120):
            raise ValidationError({"time_to_action": "Время выполнения не может превышать 120 секунд (2 минуты)."})
    return value


def validate_related_habit_is_pleasant(value):
    """
    Проверяет, что связанная привычка имеет признак приятной привычки.
    Валидирует только если поле related_habit присутствует в данных.
    """
    related_habit = value.get("related_habit")

    # Проверяем только если поле передано в запросе и оно не None
    if "related_habit" in value and related_habit is not None:
        if not related_habit.is_pleasant:
            raise ValidationError(
                {"related_habit": "Связанные привычки могут быть только с признаком приятной привычки."}
            )
    return value


def validate_pleasant_habit_no_reward_or_related(value):
    """
    Проверяет, что у приятной привычки нет вознаграждения или связанной привычки.
    Валидирует только если is_pleasant присутствует в данных и установлен в True.
    """
    is_pleasant = value.get("is_pleasant", False)

    # Проверяем только если is_pleasant передан в запросе и равен True
    if "is_pleasant" in value and is_pleasant:
        reward = value.get("reward")
        related_habit = value.get("related_habit")

        # Если reward или related_habit переданы в запросе и не None — ошибка
        has_reward = "reward" in value and reward is not None
        has_related = "related_habit" in value and related_habit is not None

        if has_reward or has_related:
            raise ValidationError(
                {"is_pleasant": "У приятной привычки не может быть вознаграждения или связанной привычки."}
            )
    return value


def validate_period_between_1_and_7_days(value):
    """
    Проверяет, что период выполнения находится в диапазоне от 1 до 7 дней.
    Валидирует только если поле period присутствует в данных.
    """
    period = value.get("period")

    # Проверяем только если поле передано в запросе и не None
    if "period" in value and period is not None:
        if not (1 <= period <= 7):
            raise ValidationError({"period": "Период выполнения должен быть от 1 до 7 дней включительно."})
    return value
