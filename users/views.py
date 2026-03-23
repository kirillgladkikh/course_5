from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class UserIndexView(APIView):
    def get(self, request):
        return Response({"message": "Добро пожаловать в API привычек!"}, status=status.HTTP_200_OK)
