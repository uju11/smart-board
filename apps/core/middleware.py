from .context import current_user

class CurrentUserMiddleware:
    """
    Automatically extracts the user from the request and stores it in ContextVars.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Extract the user (if they are logged in)
        user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
        
        # Inject the user into the ContextVar and save the reference token
        token = current_user.set(user)
        
        try:
            # Let Django process the API view
            response = self.get_response(request)
        finally:
            # Clean up memory after the response is generated
            current_user.reset(token)
            
        return response