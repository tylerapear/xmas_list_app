from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from django.db import IntegrityError

from xmas_lists.models import User


def index(request):
    
    return render(request, "mysite/index.html", {})
        
def signup(request):
    
    first_name, username, password = request.POST["first-name"], request.POST["email"], request.POST["password"]
    
    try:
        user = User.objects.create_user(first_name=first_name, username=username, password=password)
    except IntegrityError:
        messages.error(request, "A user with this email already exists")
        return HttpResponseRedirect(reverse("login"))
    
    login(request, user)
    messages.success(request, "Account created successfully!")
    
    return HttpResponseRedirect(reverse("index"))