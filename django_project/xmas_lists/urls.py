from django.urls import path

from . import views

app_name = "xmas_lists"
urlpatterns = [
    path("", views.index, name='index'),
    path("event/<int:pk>/", views.EventDetailView.as_view(), name="event-detail"),
    path("event/create", views.EventCreateView.as_view(), name="event-create"),
    path("event/<int:pk>/update", views.EventUpdateView.as_view(), name="event-update"),
    path("list/", views.ListListView.as_view(), name="list-list"),
    path("list/<int:pk>/", views.ListDetailView.as_view(), name="list-detail"),
    path("list/<int:pk>/create", views.ListItemCreateView.as_view(), name="list-item-create"),
    path("list-item/<int:pk>/update", views.ListItemUpdateView.as_view(), name="list-item-update"),
    path("list-item/<int:pk>/delete", views.ListItemDeleteView.as_view(), name="list-item-delete"),
    path("list-item/<int:pk>/purchase", views.ListItemPurchasedCreateView.as_view(), name="list-item-purchase"),
    path("list-item/<int:pk>/unpurchase", views.ListItemPurchasedDeleteView.as_view(), name="list-item-unpurchase"),
]