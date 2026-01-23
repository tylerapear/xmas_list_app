from django.urls import path

from . import views

app_name = "xmas_lists"
urlpatterns = [
    path("", views.index, name="index"),
    path("list/<int:list_id>/", views.list, name="list"),
    path("list/<int:list_id>/create", views.create, name="create")
]