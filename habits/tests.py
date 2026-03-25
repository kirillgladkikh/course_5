from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from habits.models import Habit
from rest_framework.serializers import ValidationError
from habits.validators import (
    validate_no_reward_and_related_habit,
    validate_time_to_action_max_120_seconds,
    validate_related_habit_is_pleasant,
    validate_pleasant_habit_no_reward_or_related,
    validate_period_between_1_and_7_days,
)
from unittest.mock import Mock


User = get_user_model()  # Получаем кастомную модель пользователя


class HabitCRUDTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Создаём пользователя
        self.user = User.objects.create(
            email='test@example.com'
        )
        self.user.set_password('testpass123')
        self.user.save()

        # Авторизуемся
        self.client.force_authenticate(user=self.user)


    def test_available_endpoints(self):
        response = self.client.get('/habits/habits/')
        print("Доступные методы:", response.data)


    def test_create_habit_success(self):
        """Тест успешного создания привычки"""
        data = {
            'habit_name': 'Утренняя зарядка',
            'place': 'Дома',
            'time': '08:00:00',
            'action': 'Пробежать 1 км',
            'is_pleasant': False,
            'period': 1,
            'reward': 'Чашка кофе',
            'time_to_action': 120,  # Передаем как число секунд (120 с = 2 мин)
            'is_published': True,
        }

        print("\n" + "=" * 50)
        print("ОТЛАДКА ТЕСТА: Создание привычки")
        print("=" * 50)
        print(f"URL: /habits/habits/")
        print(f"Метод: POST")
        print(f"Данные запроса: {data}")
        print(f"Аутентифицированный пользователь: {self.user.email if self.user else 'None'}")
        print(f"Количество привычек до запроса: {Habit.objects.count()}")

        response = self.client.post('/habits/habits/', data, format='json')

        print(f"\nСтатус ответа: {response.status_code}")
        print(f"Тело ответа (response.data): {response.data}")
        print(f"Заголовки ответа: {dict(response.items())}")
        print(f"Количество привычек после запроса: {Habit.objects.count()}")
        print("=" * 50 + "\n")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.count(), 1)
        habit = Habit.objects.first()
        self.assertEqual(habit.habit_name, 'Утренняя зарядка')
        self.assertEqual(habit.owner, self.user)

    # def test_create_habit_success(self):
    #     """Тест успешного создания привычки"""
    #     data = {
    #         'habit_name': 'Утренняя зарядка',
    #         'place': 'Дома',
    #         'time': '08:00:00',
    #         'action': 'Пробежать 1 км',
    #         'is_pleasant': False,
    #         'period': 1,
    #         'reward': 'Чашка кофе',
    #         'time_to_action': 120,  # Передаем как число секунд
    #         'is_published': True,
    #     }
    #
    #     print("Отправляем POST-запрос с данными:", data)
    #     response = self.client.post('/habits/habits/', data, format='json')
    #
    #     print("Статус ответа:", response.status_code)
    #     print("Тело ответа:", response.data)
    #
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.assertEqual(Habit.objects.count(), 1)
    #     habit = Habit.objects.first()
    #     self.assertEqual(habit.habit_name, 'Утренняя зарядка')
    #     self.assertEqual(habit.owner, self.user)

        # """Тест успешного создания привычки"""
        # data = {
        #     'habit_name': 'Утренняя зарядка',
        #     'place': 'Дома',
        #     'time': '08:00:00',
        #     'action': 'Пробежать 1 км',
        #     'is_pleasant': False,
        #     'period': 1,
        #     'reward': 'Чашка кофе',
        #     'time_to_action': '00:02:00',  # 2 минуты
        #     'is_published': True,
        # }
        #
        # response = self.client.post('/habits/habits/', data, format='json')
        #
        # self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # self.assertEqual(Habit.objects.count(), 1)
        # habit = Habit.objects.first()
        # self.assertEqual(habit.habit_name, 'Утренняя зарядка')
        # self.assertEqual(habit.owner, self.user)

    def test_retrieve_habit_success(self):
        """Тест получения привычки"""
        habit = Habit.objects.create(
            habit_name='Утренняя зарядка',
            place='Дома',
            time='08:00:00',
            action='Пробежать 1 км',
            is_pleasant=False,
            period=1,
            reward='Чашка кофе',
            time_to_action='00:02:00',
            is_published=True,
            owner=self.user
        )

        response = self.client.get(f'/habits/habits/{habit.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['habit_name'], 'Утренняя зарядка')

    def test_update_habit_success(self):
        """Тест обновления привычки"""
        habit = Habit.objects.create(
            habit_name='Утренняя зарядка',
            place='Дома',
            time='08:00:00',
            action='Пробежать 1 км',
            is_pleasant=False,
            period=1,
            reward='Чашка кофе',
            time_to_action='00:02:00',
            is_published=True,
            owner=self.user
        )

        update_data = {
            'habit_name': 'Вечерняя пробежка',
            'place': 'Парк',
            'time': '19:00:00'
        }

        response = self.client.put(f'/habits/habits/{habit.id}/', update_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        habit.refresh_from_db()
        self.assertEqual(habit.habit_name, 'Вечерняя пробежка')
        self.assertEqual(habit.place, 'Парк')

    def test_partial_update_habit_success(self):
        """Тест частичного обновления привычки"""
        habit = Habit.objects.create(
            habit_name='Утренняя зарядка',
            place='Дома',
            time='08:00:00',
            action='Пробежать 1 км',
            is_pleasant=False,
            period=1,
            reward='Чашка кофе',
            time_to_action='00:02:00',
            is_published=True,
            owner=self.user
        )

        patch_data = {'habit_name': 'Йога по утрам'}

        response = self.client.patch(f'/habits/habits/{habit.id}/', patch_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        habit.refresh_from_db()
        self.assertEqual(habit.habit_name, 'Йога по утрам')

    def test_delete_habit_success(self):
        """Тест удаления привычки"""
        habit = Habit.objects.create(
            habit_name='Утренняя зарядка',
            place='Дома',
            time='08:00:00',
            action='Пробежать 1 км',
            is_pleasant=False,
            period=1,
            reward='Чашка кофе',
            time_to_action='00:02:00',
            is_published=True,
            owner=self.user
        )

        response = self.client.delete(f'/habits/habits/{habit.id}/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Habit.objects.filter(id=habit.id).exists())

    def test_list_habits_success(self):
        """Тест списка привычек пользователя"""
        Habit.objects.create(
            habit_name='Утренняя зарядка',
            place='Дома',
            time='08:00:00',
            action='Пробежать 1 км',
            is_pleasant=False,
            period=1,
            reward='Чашка кофе',
            time_to_action='00:02:00',
            is_published=True,
            owner=self.user
        )
        Habit.objects.create(
            habit_name='Чтение перед сном',
            place='Дом',
            time='22:00:00',
            action='Прочитать 10 страниц',
            is_pleasant=True,
            period=1,
            time_to_action='00:01:30',
            is_published=False,
            owner=self.user
        )

        response = self.client.get('/habits/habits/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_public_habits_endpoint(self):
        """Тест эндпоинта публичных привычек"""
        # Создаём публичную привычку
        public_habit = Habit.objects.create(
            habit_name='Публичная привычка',
            place='Общественное место',
            time='10:00:00',
            action='Сделать разминку',
            is_pleasant=True,
            period=2,
            time_to_action='00:01:00',
            is_published=True,
            owner=self.user
        )
        # Создаём приватную привычку
        Habit.objects.create(
            habit_name='Приватная привычка',
            place='Дом',
            time='18:00:00',
            action='Помедитировать',
            is_pleasant=True,
            period=3,
            time_to_action='00:01:30',
            is_published=False,
            owner=self.user
        )

        # Снимаем аутентификацию для теста публичного эндпоинта
        self.client.force_authenticate(user=None)

        response = self.client.get('/habits/habits/public_habits/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['habit_name'], 'Публичная привычка')


    def test_unauthorized_access_to_private_habits(self):
        """Тест доступа неавторизованного пользователя к приватным привычкам"""
        self.client.force_authenticate(user=None)

        response = self.client.get('/habits/habits/')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn(
            'detail',
            response.data,
            'Ответ должен содержать поле "detail" с описанием ошибки'
        )
        self.assertEqual(
            response.data['detail'],
            'Authentication credentials were not provided.',
            'Сообщение об ошибке должно быть стандартным для DRF при отсутствии аутентификации'
        )


# Тесты для валидаторов (habits/validators.py)
class HabitValidatorsTests(TestCase):
    def setUp(self):
        # Создаём моковый объект привычки для тестов валидаторов, зависящих от связанных привычек
        self.pleasant_habit = Mock(
            is_pleasant=True,
            pk=1
        )
        self.unpleasant_habit = Mock(
            is_pleasant=False,
            pk=2
        )

    def test_validate_no_reward_and_related_habit_success(self):
        """Тест валидатора: не заполнены одновременно вознаграждение и связанная привычка (успех)"""
        # Только вознаграждение
        data = {'reward': 'Чашка кофе', 'related_habit': None}
        result = validate_no_reward_and_related_habit(data)
        self.assertEqual(result, data)

        # Только связанная привычка
        data = {'reward': None, 'related_habit': self.pleasant_habit}
        result = validate_no_reward_and_related_habit(data)
        self.assertEqual(result, data)

        # Ни того, ни другого
        data = {'reward': None, 'related_habit': None}
        result = validate_no_reward_and_related_habit(data)
        self.assertEqual(result, data)

# РАБОТАЕТ!! СДЕЛАТЬ ТАКЖЕ ДЛЯ ВСЕХ ВАЛИДАТОРОВ !!!
    def test_validate_no_reward_and_related_habit_failure(self):
        """Тест валидатора: ошибка при одновременном заполнении вознаграждения и связанной привычки"""
        with self.assertRaises(ValidationError) as context:
            validate_no_reward_and_related_habit({
                'reward': 'Чашка кофе',
                'related_habit': 1
            })

        detail = context.exception.detail
        error_message = ''

        if isinstance(detail, dict) and 'reward' in detail:
            error_detail = detail['reward']
            if hasattr(error_detail, 'string'):  # DRF ErrorDetail объект
                error_message = error_detail.string
            elif isinstance(error_detail, (list, tuple)) and error_detail:
                first_item = error_detail[0]
                if hasattr(first_item, 'string'):
                    error_message = first_item.string
                else:
                    error_message = str(first_item)
            else:
                error_message = str(error_detail)
        else:
            error_message = str(detail)

        self.assertEqual(
            error_message,
            'Одновременный выбор вознаграждения и связанной привычки не допускается.'
        )



    # def test_validate_no_reward_and_related_habit_failure(self):
    #     """Тест валидатора: ошибка при одновременном заполнении вознаграждения и связанной привычки"""
        # data = {
        #     'reward': 'Чашка кофе',
        #     'related_habit': self.pleasant_habit
        # }
        #
        # with self.assertRaises(ValidationError) as context:
        #     validate_no_reward_and_related_habit(data)
        #
        # self.assertIn('reward', context.exception.detail)
        # self.assertEqual(
        #     context.exception.detail['reward'][0],
        #     'Одновременный выбор вознаграждения и связанной привычки не допускается.'
        # )

    def test_validate_time_to_action_max_120_seconds_success(self):
        """Тест валидатора: время выполнения не превышает 120 секунд (успех)"""
        from datetime import timedelta

        # Ровно 120 секунд
        data = {'time_to_action': timedelta(seconds=120)}
        result = validate_time_to_action_max_120_seconds(data)
        self.assertEqual(result, data)

        # Меньше 120 секунд
        data = {'time_to_action': timedelta(seconds=60)}
        result = validate_time_to_action_max_120_seconds(data)
        self.assertEqual(result, data)

        # Нет времени выполнения
        data = {'time_to_action': None}
        result = validate_time_to_action_max_120_seconds(data)
        self.assertEqual(result, data)

    def test_validate_time_to_action_max_120_seconds_failure(self):
        """Тест валидатора: ошибка, если время выполнения превышает 120 секунд"""
        from datetime import timedelta

        data = {'time_to_action': timedelta(seconds=121)}

        with self.assertRaises(ValidationError) as context:
            validate_time_to_action_max_120_seconds(data)

        self.assertIn('time_to_action', context.exception.detail)
        self.assertEqual(
            context.exception.detail['time_to_action'][0],
            'Время выполнения не может превышать 120 секунд (2 минуты).'
        )

    def test_validate_related_habit_is_pleasant_success(self):
        """Тест валидатора: связанная привычка — приятная (успех)"""
        data = {'related_habit': self.pleasant_habit}
        result = validate_related_habit_is_pleasant(data)
        self.assertEqual(result, data)

        # Нет связанной привычки
        data = {'related_habit': None}
        result = validate_related_habit_is_pleasant(data)
        self.assertEqual(result, data)

    def test_validate_related_habit_is_pleasant_failure(self):
        """Тест валидатора: ошибка, если связанная привычка не является приятной"""
        data = {'related_habit': self.unpleasant_habit}

        with self.assertRaises(ValidationError) as context:
            validate_related_habit_is_pleasant(data)

        self.assertIn('related_habit', context.exception.detail)
        self.assertEqual(
            context.exception.detail['related_habit'][0],
            'Связанные привычки могут быть только с признаком приятной привычки.'
        )

    def test_validate_pleasant_habit_no_reward_or_related_success(self):
        """Тест валидатора: у приятной привычки нет вознаграждения или связанной привычки (успех)"""
        # Приятная привычка без дополнительных полей
        data = {'is_pleasant': True, 'reward': None, 'related_habit': None}
        result = validate_pleasant_habit_no_reward_or_related(data)
        self.assertEqual(result, data)

        # Неприятная привычка с вознаграждением
        data = {'is_pleasant': False, 'reward': 'Чашка кофе', 'related_habit': None}
        result = validate_pleasant_habit_no_reward_or_related(data)
        self.assertEqual(result, data)

    def test_validate_pleasant_habit_no_reward_or_related_failure(self):
        """Тест валидатора: ошибка, если у приятной привычки есть вознаграждение или связанная привычка"""
        # С вознаграждением
        data = {'is_pleasant': True, 'reward': 'Чашка кофе', 'related_habit': None}

        with self.assertRaises(ValidationError) as context:
            validate_pleasant_habit_no_reward_or_related(data)

        self.assertIn('is_pleasant', context.exception.detail)
        self.assertEqual(
            context.exception.detail['is_pleasant'][0],
            'У приятной привычки не может быть вознаграждения или связанной привычки.'
        )

        # Со связанной привычкой
        data = {'is_pleasant': True, 'reward': None, 'related_habit': self.pleasant_habit}

        with self.assertRaises(ValidationError):
            validate_pleasant_habit_no_reward_or_related(data)

    def test_validate_period_between_1_and_7_days_success(self):
        """Тест валидатора: период выполнения в диапазоне 1–7 дней (успех)"""
        for period in range(1, 8):  # 1, 2, 3, 4, 5, 6, 7
            data = {'period': period}
            result = validate_period_between_1_and_7_days(data)
            self.assertEqual(result, data)


    def test_validate_period_between_1_and_7_days_failure(self):
        """Тест валидатора: ошибка, если период выполнения вне диапазона 1–7 дней"""
        # Меньше 1
        data = {'period': 0}
        with self.assertRaises(ValidationError) as context:
            validate_period_between_1_and_7_days(data)
        self.assertIn('period', context.exception.detail)
        self.assertEqual(
            context.exception.detail['period'][0],
            'Период выполнения должен быть от 1 до 7 дней включительно.'
        )

        # Больше 7
        data = {'period': 8}
        with self.assertRaises(ValidationError) as context:
            validate_period_between_1_and_7_days(data)
        self.assertIn('period', context.exception.detail)
        self.assertEqual(
            context.exception.detail['period'][0],
            'Период выполнения должен быть от 1 до 7 дней включительно.'
        )

        # Отрицательное значение
        data = {'period': -1}
        with self.assertRaises(ValidationError) as context:
            validate_period_between_1_and_7_days(data)
        self.assertIn('period', context.exception.detail)
        self.assertEqual(
            context.exception.detail['period'][0],
            'Период выполнения должен быть от 1 до 7 дней включительно.'
        )

        # Крайние недопустимые значения (проверка граничных условий)
        data = {'period': 100}
        with self.assertRaises(ValidationError) as context:
            validate_period_between_1_and_7_days(data)
        self.assertIn('period', context.exception.detail)
        self.assertEqual(
            context.exception.detail['period'][0],
            'Период выполнения должен быть от 1 до 7 дней включительно.'
        )
