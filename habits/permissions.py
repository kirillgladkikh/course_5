from rest_framework.permissions import SAFE_METHODS, BasePermission



class IsOwnerOrReadOnly(BasePermission):
    """
    Разрешает доступ только владельцу привычки для операций записи.
    Для остальных пользователей — только чтение (если привычка публичная).
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return obj.is_published or obj.owner == request.user
        # Для операций записи (POST, PUT, PATCH, DELETE) проверяем, что пользователь — владелец
        return obj.owner == request.user


    def has_permission(self, request, view):
        # Разрешаем POST для аутентифицированных пользователей
        if view.action == 'create':
            return request.user and request.user.is_authenticated
        return True




