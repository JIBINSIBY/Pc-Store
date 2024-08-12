from django.shortcuts import redirect
from django.urls import reverse

class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            if 'user_id' in request.session:
                del request.session['user_id']
                del request.session['user_email']
                del request.session['user_role']
                del request.session['username']

        response = self.get_response(request)
        return response