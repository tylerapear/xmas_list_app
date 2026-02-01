from django.urls import path

from . import views

app_name = "xmas_lists"
urlpatterns = [
    path("event/<int:pk>/", views.EventDetailView.as_view(), name="event-detail"),
    path("list/", views.ListListView.as_view(), name="list-list"),
    path("list/<int:pk>/", views.ListDetailView.as_view(), name="list-detail"),
    path("list/<int:pk>/create", views.ListItemCreate.as_view(), name="list-item-create"),
    path("list-item/<int:pk>/purchase", views.ListItemPurchasedCreate.as_view(), name="list-item-purchase"),
]