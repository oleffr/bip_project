from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User

def home(request):
    """Главная страница"""
    return render(request, 'home.html')

def user_login(request):
    """Вход пользователя"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('profile')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')
    
    return render(request, 'login.html')

def user_logout(request):
    """Выход пользователя"""
    logout(request)
    return redirect('home')

def register(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        
        if password == password2:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Имя пользователя уже занято')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'Email уже используется')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                messages.success(request, 'Регистрация прошла успешно! Теперь вы можете войти.')
                return redirect('login')
        else:
            messages.error(request, 'Пароли не совпадают')
    
    return render(request, 'register.html')

@login_required
def profile(request):
    """Личный кабинет пользователя"""
    return render(request, 'profile.html', {'user': request.user})