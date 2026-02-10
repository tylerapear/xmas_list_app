from django import forms
from django.contrib.auth.models import User
from .models import Event, EventInvite

class EventCreateForm(forms.ModelForm):
    
    invited_users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'select2-users form-control'}),
        required=True,
        help_text="Select users attending this event"
    )
    
    event_admins = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'select2-users form-control'}),
        required=False,
        help_text="Select admins for this event",
    )
    
    class Meta:
        model = Event
        fields = ['event_title', 'event_date', 'invited_users', 'event_admins']
        
class EventInviteResponseForm(forms.ModelForm):
    
    RESPONSE_CHOICES = [
        ('accept', 'Accept'),
        ('decline', 'Decline'),
    ]
    
    response = forms.ChoiceField(
        choices=RESPONSE_CHOICES,
        widget=forms.Select,
        required=True,
        help_text="Accept or decline this invitation"
    )
    
    class Meta:
        model = EventInvite
        fields = ['response']