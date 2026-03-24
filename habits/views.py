from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
# from django.db.models import Q

from habits.models import Habit
from habits.paginators import HabitPagination
from habits.serializers import HabitSerializer
from habits.permissions import IsOwnerOrReadOnly


# CRUD для модели Habits с использованием ViewSet
class HabitViewSet(ModelViewSet):
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    pagination_class = HabitPagination
    permission_classes = [IsOwnerOrReadOnly,]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            # Для CRUD-операций оставить доступ только к своим привычкам
            return Habit.objects.filter(owner=user).order_by('habit_name')
        else:
            # Для неаутентифицированных — пустой набор (публичные привычки — через отдельный эндпоинт)
            return Habit.objects.none()

        # user = self.request.user
        # # Основной запрос: свои привычки + публичные привычки других пользователей
        # queryset = Habit.objects.filter(
        #     Q(owner=user) | Q(is_published=True)
        # ).distinct()
        #
        # # Дополнительная фильтрация: если привычка не публичная, показываем только свои
        # if user.is_authenticated:
        #     queryset = queryset.filter(
        #         Q(owner=user) |
        #         Q(is_published=True)
        #     )
        # else:
        #     # Для неаутентифицированных пользователей — только публичные привычки
        #     queryset = queryset.filter(is_published=True)
        #
        # return queryset.order_by('habit_name')  # Сортировка по дате создания

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=['get'], permission_classes=[])
    def public_habits(self, request):
        """
        Отдельный эндпоинт для получения только публичных привычек.
        Доступен без аутентификации.
        """
        queryset = Habit.objects.filter(is_published=True).order_by('habit_name')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
