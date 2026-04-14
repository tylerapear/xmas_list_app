from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailBackend(ModelBackend):
    """Authenticate using email instead of username."""
    
    def authenticate(self, request, email=None, password=None, **kwargs):
        # 'username' parameter receives the email from the login form
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return None
        
        if user.check_password(password):
            return user
        return None