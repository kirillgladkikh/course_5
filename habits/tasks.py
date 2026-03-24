import logging
from celery import shared_task
import requests
from django.conf import settings
from .services import get_upcoming_reminders
from .models import Habit

logger = logging.getLogger(__name__)

@shared_task
def send_habit_reminder(habit_id):
    """
    Отправляет напоминание о привычке через Telegram.
    Выполняется в назначенное время (eta).
    """
    try:
        habit = Habit.objects.get(id=habit_id)
        user = habit.owner

        if not user or not user.tg_id:
            logger.warning(f"У пользователя {user.email} нет Telegram ID")
            return "Пользователь не имеет Telegram ID"

        message = (
            f"⏰ Напоминание о привычке!\n\n"
            f"Привычка: {habit.habit_name}\n"
            f"Действие: {habit.action}\n"
            f"Время: {habit.time}\n"
            f"Место: {habit.place}\n"
        )

        if send_telegram_message(user.tg_id, message):
            logger.info(f"Напоминание отправлено для {habit.habit_name}")
            return "Напоминание успешно отправлено"
        else:
            return "Ошибка отправки через Telegram"

    except Habit.DoesNotExist:
        logger.error(f"Привычка с ID {habit_id} не найдена")
        return "Ошибка: привычка не найдена"
    except Exception as e:
        logger.error(f"Ошибка при отправке напоминания для привычки {habit_id}: {str(e)}")
        return f"Ошибка: {str(e)}"

@shared_task
def schedule_habit_reminders():
    """
    Ежедневно планирует напоминания на следующие 24 часа.
    Запускается через Celery Beat (в 01:00).
    """
    sent_count = 0

    # Получаем все предстоящие напоминания на 24 часа вперёд
    for habit, reminder_time in get_upcoming_reminders(hours_ahead=24):
        # Планируем отправку напоминания в точное время
        send_habit_reminder.apply_async(
            args=[habit.id],
            eta=reminder_time
        )
        sent_count += 1
        logger.info(f"Запланировано напоминание для {habit.habit_name} на {reminder_time}")

    logger.info(f"Всего запланировано напоминаний: {sent_count}")
    return f"Запланировано {sent_count} напоминаний"

def send_telegram_message(chat_id, text):
    """
    Отправка сообщения через Telegram_Bot_API.
    """
    url = f"{settings.TELEGRAM_URL}{settings.TELEGRAM_TOKEN}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        logger.error(f"Ошибка отправки в Telegram: {e}")
        return False
