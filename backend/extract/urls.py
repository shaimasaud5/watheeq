from django.urls import path
from .views import ExtractAPIView

urlpatterns = [
   path("extract/",ExtractAPIView.as_view(),name="extract"),
]