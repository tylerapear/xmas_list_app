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

from .models import Event, List, ListItem, ListItemPurchased
    
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
        
        annotated_items = []
        for item in list_obj.listitem_set.all():
            purchased = ListItemPurchased.objects.filter(list_item = item).first()
            annotated_items.append({
                'item': item,
                'purchased_id': purchased.id if purchased else None,
                'purchased_by': purchased.purchased_by if purchased else None,
                'purchase_comments': purchased.purchase_comments if purchased else None,
            })
        context['annotated_items'] = annotated_items
        
        return context
    
class ListItemCreate(generic.CreateView):
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
            form.add_error(None, "An item with this title already exists on this list")
            return self.form_invalid(form)
    
    def get_success_url(self):
        return reverse('xmas_lists:list-detail', kwargs={'pk': self.kwargs['pk']})
    
class ListItemUpdate(LoginRequiredMixin, generic.UpdateView):
    model = ListItem
    fields = ['title', 'url', 'price', 'priority']
    template_name = 'xmas_lists/listitem_update_form.html'
    
    def get_success_url(self):
        return reverse('xmas_lists:list-detail', kwargs={'pk': 
            get_object_or_404(ListItem, pk=self.kwargs['pk']).list.id
        })
    
class ListItemDelete(LoginRequiredMixin, generic.DeleteView):
    model = ListItem
    
    def get_success_url(self):
        return reverse('xmas_lists:list-detail', kwargs={'pk': 
            get_object_or_404(ListItem, pk=self.kwargs['pk']).list.id
        })
    
class ListItemPurchasedCreate(LoginRequiredMixin, generic.CreateView):
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
        
class ListItemPurchasedDelete(LoginRequiredMixin, generic.DeleteView):    
    model = ListItemPurchased
    def get_success_url(self):
        return reverse('xmas_lists:list-detail', kwargs={'pk': 
            get_object_or_404(ListItemPurchased, pk=self.kwargs['pk']).list_item.list.id
        })
