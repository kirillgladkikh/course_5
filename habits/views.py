from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from habits.models import Habit
from habits.paginators import HabitPagination
from habits.permissions import IsOwnerOrReadOnly
from habits.serializers import HabitSerializer


# CRUD для модели Habits с использованием ViewSet
class HabitViewSet(ModelViewSet):
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    pagination_class = HabitPagination


    permission_classes = [IsOwnerOrReadOnly]


    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']


    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            if self.action == 'create':
                # При создании не фильтруем — владелец будет назначен в perform_create
                return Habit.objects.all()
            else:
                return Habit.objects.filter(owner=user).order_by("habit_name")
        else:
            return Habit.objects.none()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


    def create(self, request, *args, **kwargs):

        return super().create(request, *args, **kwargs)











    @action(detail=False, methods=["get"], permission_classes=[])
    def public_habits(self, request):
        """
        Отдельный эндпоинт для получения только публичных привычек.
        Доступен без аутентификации.
        """
        queryset = Habit.objects.filter(is_published=True).order_by("habit_name")
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
