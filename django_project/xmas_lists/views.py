from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db import IntegrityError
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from datetime import timedelta
from guardian.shortcuts import assign_perm

from .forms import EventCreateForm
from .models import Event, List, ListItem, ListItemPurchased, User
    
@login_required
def index(request):
    
    list_obj = ( 
        List.objects
        .filter(event__event_date__gt=timezone.now(), user=request.user)
        .order_by('event__event_date')
        .first()
    )
    context = {'list': list_obj}
    return render(request, 'xmas_lists/index.html', context)
    
    
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
    
class EventCreateView(LoginRequiredMixin, generic.CreateView):
    model = Event
    form_class = EventCreateForm
    
    def form_valid(self, form):
        response = super().form_valid(form)
        users = form.cleaned_data['users']
        event = self.object
        for user in users:
            new_list, created = List.objects.get_or_create(event=event, user=user)
            assign_perm('change_list', user, new_list)
        return response
    
class EventUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Event
    form_class = EventCreateForm
    
    def get_initial(self):
        initial = super().get_initial()
        event = self.get_object()
        users_in_event = List.objects.filter(event=event).values_list('user', flat=True)
        initial['users'] = users_in_event
        return initial
    
    def form_valid(self, form):
        response = super().form_valid(form)
        event = self.get_object()
        
        initial_users = User.objects.filter(list__event=event)
        updated_users = form.cleaned_data['users']
        
        # Delete any removed users
        for user in initial_users:
            if user not in updated_users:
                List.objects.filter(user=user, event=event).delete()
        
        for user in updated_users:
            new_list, created = List.objects.get_or_create(event=event, user=user)
            assign_perm('change_list', user, new_list)
        return response

class ListListView(LoginRequiredMixin, generic.ListView):
    model = List
    
    def get_queryset(self):
        return (
            List.objects
            .filter(user=self.request.user)
            .order_by('event__event_date')
        )
    
class ListDetailView(LoginRequiredMixin, generic.DetailView):
    model = List
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        list_obj = self.object
        is_owner = (list_obj.user == self.request.user)
        context['is_owner'] = is_owner
        
        has_new_items = False
        annotated_items = []
        for item in list_obj.listitem_set.all():
            
            purchased = ListItemPurchased.objects.filter(list_item = item).first()
            
            ten_minutes_after_created = item.created_at + timedelta(minutes=10)
            modifiable_window = timezone.now() < ten_minutes_after_created
            has_new_items = True if modifiable_window or has_new_items else False
            
            if not modifiable_window or is_owner:
                annotated_items.append({
                    'item': item,
                    'purchased_id': purchased.id if purchased else None,
                    'purchased_by': purchased.purchased_by if purchased else None,
                    'purchase_comments': purchased.purchase_comments if purchased else None,
                    'modifiable_window': modifiable_window,
                })
        context['annotated_items'] = annotated_items
        context['has_new_items'] = has_new_items
        
        return context
    
class ListItemCreateView(generic.CreateView):
    model = ListItem
    fields = ['title', 'url', 'price', 'priority']
    
    def dispatch(self, request, *args, **kwargs):
        list_obj = get_object_or_404(List, pk=self.kwargs['pk'])
        if not request.user.has_perm('xmas_lists.change_list', list_obj):
            raise PermissionDenied("You do not have permission to edit this list.")
        return super().dispatch(request, *args, **kwargs)
    
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
            print("errorrrrr")
            form.add_error(None, "An item with this title already exists on this list")
            return self.form_invalid(form)
    
    def get_success_url(self):
        return reverse('xmas_lists:list-detail', kwargs={'pk': self.kwargs['pk']})
    
class ListItemUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = ListItem
    fields = ['title', 'url', 'price', 'priority']
    template_name = 'xmas_lists/listitem_update_form.html'
    
    def get_success_url(self):
        return reverse('xmas_lists:list-detail', kwargs={'pk': 
            get_object_or_404(ListItem, pk=self.kwargs['pk']).list.id
        })
    
class ListItemDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = ListItem
    
    def get_success_url(self):
        return reverse('xmas_lists:list-detail', kwargs={'pk': 
            get_object_or_404(ListItem, pk=self.kwargs['pk']).list.id
        })
    
class ListItemPurchasedCreateView(LoginRequiredMixin, generic.CreateView):
    model = ListItemPurchased
    fields = ['purchase_comments']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        list_obj = get_object_or_404(ListItem, pk=self.kwargs['pk'])
        context['list-item'] = list_obj
        return context
    
    def form_valid(self, form):
        form.instance.list_item = get_object_or_404(ListItem, pk=self.kwargs['pk'])
        form.instance.purchased_by = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('xmas_lists:list-detail', kwargs={'pk': 
            get_object_or_404(ListItem, pk=self.kwargs['pk']).list.id
        })
        
class ListItemPurchasedDeleteView(LoginRequiredMixin, generic.DeleteView):    
    model = ListItemPurchased
    def get_success_url(self):
        return reverse('xmas_lists:list-detail', kwargs={'pk': 
            get_object_or_404(ListItemPurchased, pk=self.kwargs['pk']).list_item.list.id
        })
