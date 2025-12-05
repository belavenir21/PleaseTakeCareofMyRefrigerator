"""
Custom SessionAuthentication that doesn't enforce CSRF for specific endpoints
"""
from rest_framework.authentication import SessionAuthentication


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    SessionAuthentication that doesn't enforce CSRF
    Use this for file upload endpoints
    """
    def enforce_csrf(self, request):
        return  # Skip CSRF check
