from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

def signup_view(request):
    if request.method == 'POST':
        email = request.POST.get('email'); password = request.POST.get('password'); name = request.POST.get('name') or ''
        if not email or not password:
            return render(request, 'users/signup.html', {'error':'Email và mật khẩu bắt buộc'})
        if User.objects.filter(username=email).exists():
            return render(request, 'users/signup.html', {'error':'Tài khoản đã tồn tại'})
        u = User.objects.create_user(username=email, email=email, password=password, first_name=name)
        login(request, u)
        return redirect('/')
    return render(request, 'users/signup.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email'); password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            return redirect('/')
        return render(request, 'users/login.html', {'error':'Sai thông tin đăng nhập'})
    return render(request, 'users/login.html')

def logout_view(request):
    logout(request)
    return redirect('/')
