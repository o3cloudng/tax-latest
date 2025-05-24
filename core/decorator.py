from django.core.exceptions import PermissionDenied
from django.contrib.auth import logout

# Permission that allows more roles = 
def role_required(allowed_roles=[]):
    def decorator(view_func):
        def wrap(request, *args, **kwargs):
            if request.role == allowed_roles:
                return view_func(request, *args, **kwargs)
            else: # Logout
                logout(request)
                # raise PermissionDenied
        return wrap
    return decorator

# Admin Only
def admin_only(view_func):
    def wrap(request, *args, **kwargs):
        # print(f"IS ADMIN: {request.user.is_tax_admin}")
        if request.user.is_tax_admin:
            return view_func(request, *args, **kwargs)
        else: # Logout
            # logout(request)
            raise PermissionDenied
    return wrap

# Tax Payers Only
def tax_payer_only(view_func):
    def wrap(request, *args, **kwargs):
        if not request.user.is_tax_admin:
            return view_func(request, *args, **kwargs)
        else: # Logout
            # logout(request)
            raise PermissionDenied
    return wrap