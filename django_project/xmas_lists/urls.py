from django.urls import path

from . import views

app_name = "xmas_lists"
urlpatterns = [
    path("", views.index, name='index'),
    path("event/", views.EventListView.as_view(), name="event-list"),
    path("event/<int:pk>/", views.EventDetailView.as_view(), name="event-detail"),
    path("event/create", views.EventCreateView.as_view(), name="event-create"),
    path("event/<int:pk>/update", views.EventUpdateView.as_view(), name="event-update"),
    path("eventinvite/", views.EventInviteListView.as_view(), name="eventinvite-list"),
    path("eventinvite/<int:pk>/update", views.EventInviteUpdateView.as_view(), name="eventinvite-update"),
    path("list/", views.ListListView.as_view(), name="list-list"),
    path("list/<int:pk>/", views.ListDetailView.as_view(), name="list-detail"),
    path("list/<int:pk>/create", views.ListItemCreateView.as_view(), name="list-item-create"),
    path("list-item/<int:pk>/update", views.ListItemUpdateView.as_view(), name="list-item-update"),
    path("list-item/<int:pk>/delete", views.ListItemDeleteView.as_view(), name="list-item-delete"),
    path("list-item/<int:pk>/purchase", views.ListItemPurchasedCreateView.as_view(), name="list-item-purchase"),
    path("list-item/<int:pk>/unpurchase", views.ListItemPurchasedDeleteView.as_view(), name="list-item-unpurchase"),
    path("friend-request/", views.FriendRequestListView.as_view(), name="friend-request-list"),
    path("friend-request/create", views.FriendRequestCreateView.as_view(), name="friend-request-create"),
    path("friend-request/<int:pk>/update", views.FriendRequestUpdateView.as_view(), name="friend-request-update")
]