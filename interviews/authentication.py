from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings


class APIKeyAuthentication(BaseAuthentication):
    """
    Simple API key authentication.
    Clients should authenticate by passing the API key in the "X-API-Key" header.
    """
    
    def authenticate(self, request):
        api_key = request.META.get('HTTP_X_API_KEY')
        
        if not api_key:
            return None
            
        if api_key != settings.API_KEY:
            raise AuthenticationFailed('Invalid API key')
            
        # Return a dummy user and auth token
        return (None, api_key)
    
    def authenticate_header(self, request):
        return 'X-API-Key'
