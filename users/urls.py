from django.urls import path
from users.views import UserIndexView

urlpatterns = [
    path("", UserIndexView.as_view(), name="index"),
]
