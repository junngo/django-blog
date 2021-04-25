from django.urls import path
from . import views

urlpatterns = [
    # /blog/tag/django/
    path("tag/<str:slug>", views.tag_page),

    # /blog/category/programming/
    path("category/<str:slug>", views.category_page),

    # /blog/1/
    path("<int:pk>/", views.PostDetail.as_view()),

    # /blog/
    path("", views.PostList.as_view()),
]
