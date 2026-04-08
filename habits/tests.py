from unittest.mock import Mock

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.serializers import ValidationError
from rest_framework.test import APIClient

from habits.models import Habit
from habits.validators import (
    validate_no_reward_and_related_habit,
    validate_period_between_1_and_7_days,
    validate_pleasant_habit_no_reward_or_related,
    validate_related_habit_is_pleasant,
    validate_time_to_action_max_120_seconds,
)

User = get_user_model()  # Получаем кастомную модель пользователя


class HabitCRUDTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Создаём пользователя
        self.user = User.objects.create(email="test@example.com")
        self.user.set_password("testpass123")
        self.user.save()

        # Авторизуемся
        self.client.force_authenticate(user=self.user)

    def test_available_endpoints(self):
        self.client.get("/habits/habits/")

    def test_create_habit_success(self):
        """Тест успешного создания привычки"""
        data = {
            "habit_name": "Утренняя зарядка",
            "place": "Дома",
            "time": "08:00:00",
            "action": "Пробежать 1 км",
            "is_pleasant": False,
            "period": 1,
            "reward": "Чашка кофе",
            "time_to_action": 120,  # Передаем как число секунд (120 с = 2 мин)
            "is_published": True,
        }

        # print("\n" + "=" * 50)
        # print("ОТЛАДКА ТЕСТА: Создание привычки")
        # print("=" * 50)
        # print(f"URL: /habits/habits/")
        # print(f"Метод: POST")
        # print(f"Данные запроса: {data}")
        # print(f"Аутентифицированный пользователь: {self.user.email if self.user else 'None'}")
        # print(f"Количество привычек до запроса: {Habit.objects.count()}")

        response = self.client.post("/habits/habits/", data, format="json")

        # print(f"\nСтатус ответа: {response.status_code}")
        # print(f"Тело ответа (response.data): {response.data}")
        # print(f"Заголовки ответа: {dict(response.items())}")
        # print(f"Количество привычек после запроса: {Habit.objects.count()}")
        # print("=" * 50 + "\n")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.count(), 1)
        habit = Habit.objects.first()
        self.assertEqual(habit.habit_name, "Утренняя зарядка")
        self.assertEqual(habit.owner, self.user)

    def test_retrieve_habit_success(self):
        """Тест получения привычки"""
        habit = Habit.objects.create(
            habit_name="Утренняя зарядка",
            place="Дома",
            time="08:00:00",
            action="Пробежать 1 км",
            is_pleasant=False,
            period=1,
            reward="Чашка кофе",
            time_to_action="00:02:00",
            is_published=True,
            owner=self.user,
        )

        response = self.client.get(f"/habits/habits/{habit.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["habit_name"], "Утренняя зарядка")

    def test_update_habit_success(self):
        """Тест обновления привычки"""
        habit = Habit.objects.create(
            habit_name="Утренняя зарядка",
            place="Дома",
            time="08:00:00",
            action="Пробежать 1 км",
            is_pleasant=False,
            period=1,
            reward="Чашка кофе",
            time_to_action="00:02:00",
            is_published=True,
            owner=self.user,
        )

        update_data = {"habit_name": "Вечерняя пробежка", "place": "Парк", "time": "19:00:00"}

        response = self.client.patch(f"/habits/habits/{habit.id}/", update_data, format="json")

        # print(f"Статус ответа: {response.status_code}")
        # print(f"Тело ошибки: {response.data}")  # Покажет проблемное поле

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        habit.refresh_from_db()
        self.assertEqual(habit.habit_name, "Вечерняя пробежка")
        self.assertEqual(habit.place, "Парк")

    def test_partial_update_habit_success(self):
        """Тест частичного обновления привычки"""
        habit = Habit.objects.create(
            habit_name="Утренняя зарядка",
            place="Дома",
            time="08:00:00",
            action="Пробежать 1 км",
            is_pleasant=False,
            period=1,
            reward="Чашка кофе",
            time_to_action="00:02:00",
            is_published=True,
            owner=self.user,
        )

        # Данные для обновления — должны содержать ВСЕ обязательные поля модели
        update_data = {
            "habit_name": "Вечерняя пробежка",
            "action": "Пробежать 2 км",  # Обязательно!
        }

        response = self.client.patch(f"/habits/habits/{habit.id}/", update_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["habit_name"], "Вечерняя пробежка")

        self.assertEqual(response.data["action"], "Пробежать 2 км")  # Проверка обновления

    def test_delete_habit_success(self):
        """Тест удаления привычки"""
        habit = Habit.objects.create(
            habit_name="Утренняя зарядка",
            place="Дома",
            time="08:00:00",
            action="Пробежать 1 км",
            is_pleasant=False,
            period=1,
            reward="Чашка кофе",
            time_to_action="00:02:00",
            is_published=True,
            owner=self.user,
        )

        response = self.client.delete(f"/habits/habits/{habit.id}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Habit.objects.filter(id=habit.id).exists())

    def test_list_habits_success(self):
        """Тест списка привычек пользователя"""
        Habit.objects.create(
            habit_name="Утренняя зарядка",
            place="Дома",
            time="08:00:00",
            action="Пробежать 1 км",
            is_pleasant=False,
            period=1,
            reward="Чашка кофе",
            time_to_action="00:02:00",
            is_published=True,
            owner=self.user,
        )
        Habit.objects.create(
            habit_name="Чтение перед сном",
            place="Дом",
            time="22:00:00",
            action="Прочитать 10 страниц",
            is_pleasant=True,
            period=1,
            time_to_action="00:01:30",
            is_published=False,
            owner=self.user,
        )

        response = self.client.get("/habits/habits/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_public_habits_endpoint(self):
        """Тест эндпоинта публичных привычек"""
        # Создаём публичную привычку
        Habit.objects.create(
            habit_name="Публичная привычка",
            place="Общественное место",
            time="10:00:00",
            action="Сделать разминку",
            is_pleasant=True,
            period=2,
            time_to_action="00:01:00",
            is_published=True,
            owner=self.user,
        )
        # Создаём приватную привычку
        Habit.objects.create(
            habit_name="Приватная привычка",
            place="Дом",
            time="18:00:00",
            action="Помедитировать",
            is_pleasant=True,
            period=3,
            time_to_action="00:01:30",
            is_published=False,
            owner=self.user,
        )

        # Снимаем аутентификацию для теста публичного эндпоинта
        self.client.force_authenticate(user=None)

        response = self.client.get("/habits/habits/public_habits/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["habit_name"], "Публичная привычка")

    def test_unauthorized_access_to_private_habits(self):
        """Тест доступа неавторизованного пользователя к приватным привычкам"""
        self.client.force_authenticate(user=None)
        response = self.client.get("/habits/habits/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)  # Пустой список


# Тесты для валидаторов (habits/validators.py)
class HabitValidatorsTests(TestCase):
    def setUp(self):
        # Создаём моковый объект привычки для тестов валидаторов, зависящих от связанных привычек
        self.pleasant_habit = Mock(is_pleasant=True, pk=1)
        self.unpleasant_habit = Mock(is_pleasant=False, pk=2)

    def test_validate_no_reward_and_related_habit_success(self):
        """Тест валидатора: не заполнены одновременно вознаграждение и связанная привычка (успех)"""
        # Только вознаграждение
        data = {"reward": "Чашка кофе", "related_habit": None}
        result = validate_no_reward_and_related_habit(data)
        self.assertEqual(result, data)

        # Только связанная привычка
        data = {"reward": None, "related_habit": self.pleasant_habit}
        result = validate_no_reward_and_related_habit(data)
        self.assertEqual(result, data)

        # Ни того, ни другого
        data = {"reward": None, "related_habit": None}
        result = validate_no_reward_and_related_habit(data)
        self.assertEqual(result, data)

    def test_validate_no_reward_and_related_habit_failure(self):
        """Тест валидатора: ошибка при одновременном заполнении вознаграждения и связанной привычки"""
        data = {"reward": "Чашка кофе", "related_habit": 1}

        with self.assertRaises(ValidationError):
            validate_no_reward_and_related_habit(data)

    def test_validate_time_to_action_max_120_seconds_success(self):
        """Тест валидатора: время выполнения не превышает 120 секунд (успех)"""
        from datetime import timedelta

        # Ровно 120 секунд
        data = {"time_to_action": timedelta(seconds=120)}
        result = validate_time_to_action_max_120_seconds(data)
        self.assertEqual(result, data)

        # Меньше 120 секунд
        data = {"time_to_action": timedelta(seconds=60)}
        result = validate_time_to_action_max_120_seconds(data)
        self.assertEqual(result, data)

        # Нет времени выполнения
        data = {"time_to_action": None}
        result = validate_time_to_action_max_120_seconds(data)
        self.assertEqual(result, data)

    def test_validate_time_to_action_max_120_seconds_failure(self):
        """Тест валидатора: ошибка, если время выполнения превышает 120 секунд"""
        from datetime import timedelta

        # Некорректные данные — должно быть исключение
        data = {"time_to_action": timedelta(seconds=121)}
        with self.assertRaises(ValidationError):
            validate_time_to_action_max_120_seconds(data)

    def test_validate_related_habit_is_pleasant_success(self):
        """Тест валидатора: связанная привычка — приятная (успех)"""
        data = {"related_habit": self.pleasant_habit}
        result = validate_related_habit_is_pleasant(data)
        self.assertEqual(result, data)

        # Нет связанной привычки
        data = {"related_habit": None}
        result = validate_related_habit_is_pleasant(data)
        self.assertEqual(result, data)

    def test_validate_related_habit_is_pleasant_failure(self):
        """Тест валидатора: ошибка, если связанная привычка не приятная"""
        unpleasant_habit = Mock(is_pleasant=False, pk=2)
        data = {"related_habit": unpleasant_habit}

        with self.assertRaises(ValidationError):
            validate_related_habit_is_pleasant(data)

    def test_validate_pleasant_habit_no_reward_or_related_success(self):
        """Тест валидатора: у приятной привычки нет вознаграждения или связанной привычки (успех)"""
        # Приятная привычка без дополнительных полей
        data = {"is_pleasant": True, "reward": None, "related_habit": None}
        result = validate_pleasant_habit_no_reward_or_related(data)
        self.assertEqual(result, data)

        # Полезная привычка с вознаграждением
        data = {"is_pleasant": False, "reward": "Чашка кофе", "related_habit": None}
        result = validate_pleasant_habit_no_reward_or_related(data)
        self.assertEqual(result, data)

    def test_validate_pleasant_habit_no_reward_or_related_failure(self):
        """Тест валидатора: ошибка для приятной привычки с вознаграждением"""
        data = {"is_pleasant": True, "reward": "Подарок", "related_habit": None}

        with self.assertRaises(ValidationError):
            validate_pleasant_habit_no_reward_or_related(data)

    def test_validate_period_between_1_and_7_days_success(self):
        """Тест валидатора: период выполнения в диапазоне 1–7 дней (успех)"""
        for period in range(1, 8):  # 1, 2, 3, 4, 5, 6, 7
            data = {"period": period}
            result = validate_period_between_1_and_7_days(data)
            self.assertEqual(result, data)

    def test_validate_period_between_1_and_7_days_failure(self):
        """Тест валидатора: ошибка, если период вне диапазона 1–7 дней"""
        data = {"period": 8}

        with self.assertRaises(ValidationError):
            validate_period_between_1_and_7_days(data)
