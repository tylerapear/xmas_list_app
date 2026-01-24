from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate
from django.urls import reverse

from xmas_lists.models import User

def index(request):
    
    return render(request, "mysite/login.html", {})

def login_user(request):
    
    username, password = request.POST["username"], request.POST["password"]
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
    
    username, password = request.POST["username"], request.POST["password"]
    user = User.objects.create_user(username, "test@example.com", password)
    
    return HttpResponseRedirect(reverse("index"))