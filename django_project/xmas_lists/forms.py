from django import forms
from django.contrib.auth.models import User
from .models import Event

class EventCreateForm(forms.ModelForm):
    
    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'select2-users form-control'}),
        required=True,
        help_text="Select users attending this event"
    )
    
    class Meta:
        model = Event
        fields = ['event_title', 'event_date', 'users']