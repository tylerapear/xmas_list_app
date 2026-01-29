from django.urls import path

from . import views

app_name = "xmas_lists"
urlpatterns = [
    path("list/", views.ListListView.as_view(), name="list-list"),
    path("list/<int:pk>/", views.ListDetailView.as_view(), name="list-detail"),
]