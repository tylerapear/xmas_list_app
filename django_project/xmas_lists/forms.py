from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from xmas_lists.models import ListItem

class AddListItemForm(ModelForm):
    
    class Meta:
        model = ListItem
        fields = ["title", "url", "price", "priority"]
        