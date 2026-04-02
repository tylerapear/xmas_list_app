from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Prefetch
from django.db import IntegrityError
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from datetime import timedelta
from guardian.shortcuts import assign_perm, remove_perm
from guardian.mixins import PermissionRequiredMixin as GuardianPermissionRequiredMixin
from django.core.mail import send_mail

from .forms import EventCreateForm, EventInviteResponseForm
from .models import *
    
@login_required
def index(request):
    
    user = request.user
    
    list_obj = ( 
        List.objects
        .filter(event__event_date__gt=timezone.now(), user=user)
        .order_by('event__event_date')
        .first()
    )
    context = {'list': list_obj}
    
    return render(request, 'xmas_lists/index.html', context)
    
class EventListView(LoginRequiredMixin, generic.ListView):
    model = Event
    
    def get_queryset(self):
        user = self.request.user
        
        # Collect all events where the current user is an owner, admin, or attendee
        return Event.objects.filter(
            Q(event_owner=user) |
            Q(list__user=user) |
            Q(eventadmin__user=user)
        ).prefetch_related(
            Prefetch(
                'list_set',
                queryset=List.objects.filter(user=user),
                to_attr='my_lists'
            )
        ).distinct()
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        events = self.get_queryset()
        
        context['attending_events'] = [e for e in events if e.my_lists]
        context['attending_events_future'] = [e for e in events if e.my_lists and e.event_date >= timezone.now().date()]
        context['attending_events_past'] = [e for e in events if e.my_lists and e.event_date < timezone.now().date()]
        context['own_events'] = [e for e in events if e.event_owner == user]
        context['own_events_future'] = [e for e in events if e.event_owner == user and e.event_date >= timezone.now().date()]
        context['own_events_past'] = [e for e in events if e.event_owner == user and e.event_date < timezone.now().date()]
        admin_event_ids = EventAdmin.objects.filter(user=user)
        context['admin_events'] = [e for e in events if e.id in admin_event_ids]
        context['admin_events_future'] = [e for e in events if e.id in admin_event_ids and e.event_date >= timezone.now().date()]
        context['admin_events_past'] = [e for e in events if e.id in admin_event_ids and e.event_date < timezone.now().date()]
        
        return context
    
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
        
        # Set Event Owner
        form.instance.event_owner = self.request.user
        
        response = super().form_valid(form)
        event = self.object
        
        # Create EventInvites
        invited_users = form.cleaned_data['invited_users']
        for user in invited_users:
            event_invite, created = EventInvite.objects.get_or_create(event=event, user=user)
            assign_perm('change_eventinvite', user, event_invite) 
        
        # Set owner as admin
        assign_perm('change_event', self.request.user, event)
            
        # Add EventAdmin records for each event admin and assign OLPs
        event_admins = form.cleaned_data['event_admins']
        for user in event_admins:
            new_admin, created = EventAdmin.objects.get_or_create(event=event, user=user)
            assign_perm('change_event', user, event)
            
        
        return response
    
class EventUpdateView(GuardianPermissionRequiredMixin, generic.UpdateView):
    model = Event
    form_class = EventCreateForm
    permission_required = 'xmas_lists.change_event'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = self.get_object()
        return context
    
    def get_initial(self):
        initial = super().get_initial()
        event = self.get_object()
        
        # Get Current Users
        current_users = List.objects.filter(event=event).values_list('user', flat=True)
        initial['users'] = current_users
    
        # Get Current Admins
        current_admins = EventAdmin.objects.filter(event=event).values_list('user', flat=True)
        initial['event_admins'] = current_admins
        return initial
    
    def form_valid(self, form):
        response = super().form_valid(form)
        event = self.get_object()
        
        initial_users = User.objects.filter(list__event=event)
        updated_users = form.cleaned_data['invited_users']
        initial_admins = User.objects.filter(eventadmin__event=event)
        updated_admins = form.cleaned_data['event_admins']
        
        # Delete any removed users
        for user in initial_users:
            if user not in updated_users:
                List.objects.filter(user=user, event=event).delete()
                EventInvite.objects.filter(user=user, event=event).delete()
                
        # Delete any removed admins
        for user in initial_admins:
            if user not in updated_admins:
                EventAdmin.objects.filter(user=user, event=event).delete()
                remove_perm('change_event', user, event)
            
        # Create EventInvites
        for user in updated_users:
            event_invite, created = EventInvite.objects.get_or_create(event=event, user=user)
            assign_perm('change_eventinvite', user, event_invite) 
    
        # Add EventAdmin records for each event admin and assign OLPs
        event_admins = form.cleaned_data['event_admins']
        for user in event_admins:
            new_admin, created = EventAdmin.objects.get_or_create(event=event, user=user)
            assign_perm('change_event', user, event)
            
        return response
    
class EventInviteListView(LoginRequiredMixin, generic.ListView):
    model = EventInvite
    
    def get_queryset(self):
        return (
            EventInvite.objects
            .filter(user=self.request.user)
            .order_by('created_at')
        )
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pending_invites'] = context['eventinvite_list'].filter(accepted_at__isnull=True).filter(rejected_at__isnull=True)
        context['accepted_invites'] = context['eventinvite_list'].filter(accepted_at__isnull=False).filter(rejected_at__isnull=True)
        context['declined_invites'] = context['eventinvite_list'].filter(accepted_at__isnull=True).filter(rejected_at__isnull=False)
        return context

class EventInviteUpdateView(GuardianPermissionRequiredMixin, generic.UpdateView):
    model = EventInvite
    form_class = EventInviteResponseForm
    permission_required = 'change_eventinvite'
    
    def dispatch(self, request, *args, **kwargs):
        if self.get_object().accepted_at or self.get_object().rejected_at:
            raise PermissionDenied("You have already responded to this invitation")
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        response = form.cleaned_data['response']
        invite = self.get_object()
        print(response)
        if response == "accept":
            form.instance.accepted_at = timezone.now()

            # Create lists for user and assign OLPs
            new_list, created = List.objects.get_or_create(event=invite.event, user=invite.user)
            assign_perm('change_list', invite.user, new_list)
            
            return super().form_valid(form)
        elif response == "decline":
            form.instance.rejected_at = timezone.now()
            return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('xmas_lists:eventinvite-list')

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
