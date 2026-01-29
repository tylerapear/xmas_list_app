from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Count

from .models import Event, List, ListItem, ListItemPurchased
    
class EventDetailView(LoginRequiredMixin, generic.DetailView):
    model = Event
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.object
        context['lists'] = (
            List.objects.filter(event=event)
            .annotate(item_count=Count('listitem'))
        )
        return context

class ListListView(LoginRequiredMixin, generic.ListView):
    model = List
    
    def get_queryset(self):
        return (
            List.objects.filter(user=self.request.user)
        )
    
class ListDetailView(LoginRequiredMixin, generic.DetailView):
    model = List
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        list_obj = self.object
        context['is_owner'] = (list_obj.user == self.request.user)
        return context
    
    
    
    
