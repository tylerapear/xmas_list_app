from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

from .models import User, List, ListItem

def index(request):
    user = User.objects.get(pk=1)
    context = {"user": user}
    return render(request, "xmas_lists/index.html", context)

def list(request, list_id):
    user_list = List.objects.get(pk=list_id)
    context = {"list": user_list}
    return render(request, "xmas_lists/list.html", context)

def create(request, list_id):
    
    user_list = get_object_or_404(List, pk=list_id)
    item_title = request.POST["title"]
    item_url = request.POST["url"]
    
    ListItem.objects.create(
        list=user_list,
        title=item_title,
        url=item_url,
    )
    
    return HttpResponseRedirect(reverse("xmas_lists:index"))
