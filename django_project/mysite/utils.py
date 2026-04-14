from coolname import generate_slug
from django.contrib.auth.models import User

def generate_unique_username():
    ### Generates a 2-word username using coolname, and makes sure it's unique
    
    while True:
        username = generate_slug(3)
        
        users = User.objects.all()
        for user in users:
            if not User.objects.filter(username=username).exists():
                return username