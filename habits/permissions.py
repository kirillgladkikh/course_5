from rest_framework.permissions import SAFE_METHODS, BasePermission


# habits/permissions.py — отладочная версия IsOwnerOrReadOnly
class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        print(f"[PERMISSION] Проверка has_object_permission. Объект: {obj}, Метод: {request.method}")
        if request.method in SAFE_METHODS:
            print("[PERMISSION] Безопасный метод — разрешаем.")
            return True
        if obj is None:
            print("[PERMISSION] Объект None (создание) — разрешаем.")
            return True
        result = obj.owner == request.user
        print(f"[PERMISSION] Сравнение владельца: {obj.owner} == {request.user} → {result}")
        return result

    def has_permission(self, request, view):
        print(f"[PERMISSION] Проверка has_permission. Действие: {view.action}, Пользователь: {request.user}, Аутентифицирован: {request.user.is_authenticated}")
        if view.action == 'create':
            result = request.user and request.user.is_authenticated
            print(f"[PERMISSION] Результат для create: {result}")
            return result
        return True


# class IsOwnerOrReadOnly(BasePermission):
#     """
#     Разрешает доступ только владельцу привычки для операций записи.
#     Для остальных пользователей — только чтение (если привычка публичная).
#     """
#
#     def has_object_permission(self, request, view, obj):
#         if request.method in SAFE_METHODS:
#             return True
#         # При создании объекта obj = None
#         if obj is None:
#             # Разрешение уже проверено в has_permission для create
#             return True
#         return obj.owner == request.user
#         # # Разрешаем безопасные методы (GET, HEAD, OPTIONS) для всех
#         # if request.method in SAFE_METHODS:
#         #     return True
#         #     # return obj.is_published or obj.owner == request.user
#         #
#         # # Для операций записи (POST, PUT, PATCH, DELETE) проверяем, что пользователь — владелец
#         # return obj.owner == request.user
#
#     def has_permission(self, request, view):
#         # Разрешаем POST для аутентифицированных пользователей
#         if view.action == 'create':
#             return request.user and request.user.is_authenticated
#         return True
