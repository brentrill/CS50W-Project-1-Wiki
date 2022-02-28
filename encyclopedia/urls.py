from django.urls import path

from . import views

app_name = 'encyclopedia'
urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:title>", views.entry, name="title"),
    path("search/", views.search, name="search"),
    path("new/", views.new_page, name="new"),
    path("edit/", views.edit_page, name="edit"),
    path("changes/", views.change_page, name="change"),
    path("random/", views.random_page, name="random")
]
