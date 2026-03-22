from flask import session, redirect

def login_required(role=None):
    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if 'username' not in session:
                return redirect('/login')
            if role and session['username'] != role:
                return redirect('/login') 
            else:
                print(session["username"], role)
            return f(*args, **kwargs)
        wrapped_function.__name__ = f.__name__
        return wrapped_function
    return decorator