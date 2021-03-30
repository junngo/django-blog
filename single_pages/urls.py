from django.urls import path
from . import views

urlpatterns = [
    # /abou_me/
    path("about_me/", views.about_me),

    # /
    path("", views.landing),
]
