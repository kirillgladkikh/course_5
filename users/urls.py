from django.urls import path
from views import UserIndexView

urlpatterns = [
    path("", UserIndexView.as_view(), name="index"),
]
