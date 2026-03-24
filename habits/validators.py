from datetime import timedelta

from rest_framework.serializers import ValidationError


def validate_no_reward_and_related_habit(value):
    """
    Проверяет, что не заполнены одновременно вознаграждение и связанная привычка.
    """
    reward = value.get("reward")
    related_habit = value.get("related_habit")
    if reward and related_habit:
        raise ValidationError({"reward": "Одновременный выбор вознаграждения и связанной привычки не допускается."})
    return value


def validate_time_to_action_max_120_seconds(value):
    """
    Проверяет, что время выполнения не превышает 120 секунд.
    """
    time_to_action = value.get("time_to_action")
    if time_to_action and time_to_action > timedelta(seconds=120):
        raise ValidationError({"time_to_action": "Время выполнения не может превышать 120 секунд (2 минуты)."})
    return value


def validate_related_habit_is_pleasant(value):
    """
    Проверяет, что связанная привычка имеет признак приятной привычки.
    """
    related_habit = value.get("related_habit")
    if related_habit and not related_habit.is_pleasant:
        raise ValidationError({"related_habit": "Связанные привычки могут быть только с признаком приятной привычки."})
    return value


def validate_pleasant_habit_no_reward_or_related(value):
    """
    Проверяет, что у приятной привычки нет вознаграждения или связанной привычки.
    """
    is_pleasant = value.get("is_pleasant", False)
    reward = value.get("reward")
    related_habit = value.get("related_habit")
    if is_pleasant and (reward or related_habit):
        raise ValidationError(
            {"is_pleasant": "У приятной привычки не может быть вознаграждения или связанной привычки."}
        )
    return value


def validate_period_between_1_and_7_days(value):
    """
    Проверяет, что период выполнения находится в диапазоне от 1 до 7 дней.
    """
    period = value.get("period")
    if period is not None and not (1 <= period <= 7):
        raise ValidationError({"period": "Период выполнения должен быть от 1 до 7 дней включительно."})
    return value
