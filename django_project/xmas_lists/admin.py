from django.contrib import admin

from .models import Event, List, ListItem, ListItemPurchased

admin.site.register(Event)
admin.site.register(List)
admin.site.register(ListItem)
admin.site.register(ListItemPurchased)