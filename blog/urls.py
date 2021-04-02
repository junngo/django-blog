from django.urls import path
from . import views

urlpatterns = [
    # /blog/1/
    path("<int:pk>/", views.PostDetail.as_view()),

    # /blog/
    path("", views.PostList.as_view()),
]