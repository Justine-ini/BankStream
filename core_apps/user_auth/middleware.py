class CustomHeaderMiddleware:
    """
    Middleware that adds a custom HTTP header 'X-Django-User' to responses for authenticated users.
    If the user is authenticated, the middleware sets the 'X-Django-User' header to the user's email address.
    This can be useful for debugging, logging, or passing user information to frontend applications.
    Args:
        get_response (callable): The next middleware or view in the Django request/response cycle.
    Methods:
        __call__(request): Processes the incoming request and adds the custom header to the response if the user is authenticated.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_authenticated:
            response["X-Django-User"] = request.user.username
        return response
