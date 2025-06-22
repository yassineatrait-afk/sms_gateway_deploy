from functools import wraps
from flask import session, redirect, url_for


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not (current_user.is_authenticated and current_user.is_admin):
            return abort(403)
        return f(*args, **kwargs)
    return decorated

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function
