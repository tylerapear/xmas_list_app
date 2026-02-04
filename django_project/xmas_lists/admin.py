from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from .models import Event, List, ListItem, ListItemPurchased

class ListAdmin(GuardedModelAdmin):
    pass

admin.site.register(Event)
admin.site.register(List, ListAdmin)
admin.site.register(ListItem)
admin.site.register(ListItemPurchased)