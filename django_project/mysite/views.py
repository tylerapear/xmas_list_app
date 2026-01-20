from django.shortcuts import render
from django.http import HttpResponse

from xmas_lists.models import User

def index(request):
    user = User.objects.get(pk=1)
    context = {"user": user}
    return render(request, "mysite/index.html", context)