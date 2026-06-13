import contextvars

# Create the context variable with a default value of None.
current_user = contextvars.ContextVar('current_user', default=None)

def get_current_user():
    """
    Utility function to grab the logged-in user from anywhere in the codebase 
    (models, services, signals) without passing the request object.
    """
    return current_user.get()