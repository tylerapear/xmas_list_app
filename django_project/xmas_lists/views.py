from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db import IntegrityError

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
    
class ListItemCreate(LoginRequiredMixin, generic.CreateView):
    model = ListItem
    fields = ["title", "url", "price", "priority"]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        list_obj = get_object_or_404(List, pk=self.kwargs['pk'])
        context['list'] = list_obj
        return context
    
    def form_valid(self, form):
        form.instance.list = get_object_or_404(List, pk=self.kwargs['pk'])
        try:
            return super().form_valid(form)
        except IntegrityError:
            form.add_error(None, "An item with this title already exists on this list")
            return self.form_invalid(form)
    
    def get_success_url(self):
        return reverse('xmas_lists:list-detail', kwargs={'pk': self.kwargs['pk']})
    
    
    
