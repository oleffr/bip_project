from flask import session, redirect

def login_required(role=None):
    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if 'role' not in session:
                return redirect('/login')
            if role and session['role'] != role:
                return redirect('/login') 
            else:
                print(session["role"], role)
            return f(*args, **kwargs)
        wrapped_function.__name__ = f.__name__
        return wrapped_function
    return decorator