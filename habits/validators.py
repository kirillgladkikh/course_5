from datetime import timedelta
from django.core.exceptions import ValidationError


def validate_no_reward_and_related_habit(reward, related_habit):
    """
    Проверяет, что не заполнены одновременно вознаграждение и связанная привычка.
    """
    if reward and related_habit:
        raise ValidationError(
            "Одновременный выбор вознаграждения и связанной привычки не допускается."
        )

def validate_time_to_action_max_120_seconds(time_to_action):
    """
    Проверяет, что время выполнения не превышает 120 секунд.
    """
    if time_to_action and time_to_action > timedelta(seconds=120):
        raise ValidationError(
            "Время выполнения не может превышать 120 секунд (2 минуты)."
        )

def validate_related_habit_is_pleasant(related_habit):
    """
    Проверяет, что связанная привычка имеет признак приятной привычки.
    """
    if related_habit and not related_habit.is_pleasant:
        raise ValidationError(
            "Связанные привычки могут быть только с признаком приятной привычки."
        )

def validate_pleasant_habit_no_reward_or_related(is_pleasant, reward, related_habit):
    """
    Проверяет, что у приятной привычки нет вознаграждения или связанной привычки.
    """
    if is_pleasant and (reward or related_habit):
        raise ValidationError(
            "У приятной привычки не может быть вознаграждения или связанной привычки."
        )

def validate_period_between_1_and_7_days(period):
    """
    Проверяет, что период выполнения находится в диапазоне от 1 до 7 дней.
    """
    if not (1 <= period <= 7):
        raise ValidationError(
            "Период выполнения должен быть от 1 до 7 дней включительно."
        )
