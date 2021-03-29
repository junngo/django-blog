from django.urls import path
from . import views

urlpatterns = [
    # /blog/
    path("", views.index),

    # /blog/1/
    path("<int:pk>/", views.detail),
]