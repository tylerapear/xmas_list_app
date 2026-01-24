from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate
from django.contrib import messages
from django.urls import reverse
from django.db import IntegrityError

from xmas_lists.models import User

def index(request):
    
    return render(request, "mysite/login.html", {})

def login_user(request):
    
    username, password = request.POST["email"], request.POST["password"]
    user = authenticate(username=username, password=password)
    
    if user is not None:
        return render(request, "mysite/index.html", {"user": user})
    else:
        return render(
            request,
            "mysite/login.html",
            {
                "message": "Username or password is incorrect",
            },
        )
        
def signup(request):
    
    first_name, username, password = request.POST["first-name"], request.POST["email"], request.POST["password"]
    
    try:
        user = User.objects.create_user(first_name=first_name, username=username, password=password)
    except IntegrityError:
        print("HA!")
        messages.error(request, "A user with this email already exists")
        return render(request, "mysite/login.html")
    
    messages.success(request, "Account created successfully!")
    
    return HttpResponseRedirect(reverse("index"))