import os

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from google.oauth2 import id_token
from google.auth.transport import requests
from django.utils.decorators import method_decorator
from mysite.utils import generate_unique_username

from xmas_lists.models import User


def index(request):
    
    return render(request, "mysite/index.html", {})
        
@csrf_exempt
def auth_receiver(request):
    """
    Google calls this URL after the user has signed in with their Google account.
    """
    print('Inside')
    token = request.POST['credential']
 
    try:
        user_data = id_token.verify_oauth2_token(
            token, requests.Request(), os.environ['GOOGLE_OAUTH_CLIENT_ID']
        )
    except ValueError:
        return HttpResponse(status=403)
    
    print(user_data)
    
    email = user_data.get('email')
    first_name = user_data.get('given_name', '')
    last_name = user_data.get('family_name', '')
    
    user, created = User.objects.get_or_create(
        email = email,
        defaults={
            "username": generate_unique_username(),
            "first_name": first_name,
            "last_name": last_name
        }
    )
    
    user.backend = 'django.contrib.auth.backends.ModelBackend'
    login(request, user)
 
    # In a real app, I'd also save any new user here to the database.
    # You could also authenticate the user here using the details from Google (https://docs.djangoproject.com/en/4.2/topics/auth/default/#how-to-log-a-user-in)
    request.session['user_data'] = user_data
 
    return redirect('xmas_lists:index')
        
def signup(request):
    
    first_name = request.POST["first-name"]
    username = generate_unique_username() 
    password = request.POST["password"]
    email = request.POST["email"]
    
    try:
        user = User.objects.create_user(first_name=first_name, username=username, email=email, password=password)
    except IntegrityError:
        messages.error(request, "A user with this email already exists")
        return HttpResponseRedirect(reverse("login"))
    
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    messages.success(request, "Account created successfully!")
    
    return HttpResponseRedirect(reverse("xmas_lists:index"))