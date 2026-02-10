from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from .models import *

class EventObjectAdmin(GuardedModelAdmin):
    pass


class ListObjectAdmin(GuardedModelAdmin):
    pass

admin.site.register(Event, EventObjectAdmin)
admin.site.register(EventAdmin)
admin.site.register(EventInvite)
admin.site.register(List, ListObjectAdmin)
admin.site.register(ListItem)
admin.site.register(ListItemPurchased)