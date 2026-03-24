from django.utils import timezone
from datetime import timedelta

def calculate_reminder_time(habit, base_time=None):
    """
    Рассчитывает время напоминания для привычки на основе её времени и периодичности.
    Напоминание отправляется за 15 минут до времени выполнения привычки.

    Args:
        habit: экземпляр модели Habit
        base_time: базовая временная точка для расчёта (по умолчанию — сейчас)

    Returns:
        datetime: время отправки напоминания
    """
    if base_time is None:
        base_time = timezone.now()

    # Создаём datetime для напоминания сегодня (время привычки минус 15 минут)
    reminder_datetime = timezone.make_aware(
        timezone.datetime.combine(
            base_time.date(),
            habit.time
        )
    ) - timedelta(minutes=15)

    # Если напоминание в прошлом относительно base_time, планируем на следующий период
    while reminder_datetime <= base_time:
        reminder_datetime += timedelta(days=habit.period)

    return reminder_datetime

def get_upcoming_reminders(hours_ahead=24):
    """
    Получает все привычки и рассчитывает время их напоминаний на заданный период вперёд.

    Args:
        hours_ahead: количество часов вперёд для планирования напоминаний

    Yields:
        tuple: (habit, reminder_time)
    """
    from .models import Habit
    cutoff_time = timezone.now() + timedelta(hours=hours_ahead)

    for habit in Habit.objects.filter(owner__isnull=False):
        reminder_time = calculate_reminder_time(habit)
        if reminder_time <= cutoff_time:
            yield habit, reminder_time
