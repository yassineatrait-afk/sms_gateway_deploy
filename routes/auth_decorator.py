from functools import wraps
from flask import g, redirect, url_for, abort

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = getattr(g, 'current_user', None)
        if not user:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def roles_required(*allowed_roles):
    """
    Restrict access to users whose role.name is in allowed_roles.
    Usage:
      @roles_required('admin', 'manager')
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            user = getattr(g, 'current_user', None)
            if not user:
                return redirect(url_for('auth.login'))
            if user.role.name not in allowed_roles:
                return abort(403)
            return f(*args, **kwargs)
        return wrapped
    return decorator

# Convenience shortcuts
admin_required   = roles_required('admin')
manager_required = roles_required('admin', 'manager')
viewer_required  = roles_required('admin', 'manager', 'viewer')
