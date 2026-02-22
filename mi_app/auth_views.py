from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET", "POST"])
def login_view(request):
    """Vista de login"""
    if request.method == 'GET':
        return render(request, 'login.html')
    
    # POST
    username = request.POST.get('username')
    password = request.POST.get('password')
    
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        messages.success(request, f"Bienvenido {user.first_name or user.username}")
        return redirect('inicio')
    else:
        messages.error(request, "Usuario o contraseña incorrectos")
        return render(request, 'login.html', {
            'username': username,
            'error': 'Credenciales inválidas'
        })

@login_required(login_url='login')
def logout_view(request):
    """Vista de logout"""
    logout(request)
    messages.success(request, "Sesión cerrada correctamente")
    return redirect('login')

def register_view(request):
    """Vista de registro (opcional)"""
    if request.method == 'GET':
        return render(request, 'register.html')
    
    # POST
    username = request.POST.get('username')
    email = request.POST.get('email')
    password = request.POST.get('password')
    password_confirm = request.POST.get('password_confirm')
    
    if password != password_confirm:
        messages.error(request, "Contraseñas no coinciden")
        return render(request, 'register.html')
    
    if User.objects.filter(username=username).exists():
        messages.error(request, "Usuario ya existe")
        return render(request, 'register.html')
    
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )
    messages.success(request, "Usuario creado. Inicia sesión")
    return redirect('login')
