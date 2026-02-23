from django.urls import path
from .views import CreateProjectAPI

urlpatterns = [
    path("projects/create/", CreateProjectAPI.as_view()),
]