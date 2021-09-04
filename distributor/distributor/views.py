from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from financial_accounting.views import count_importation_request
from local_business.views import count_notifications
from user.forms import UserLoginForm, UserRegistrationForm


def user_registration_view(request):
    user_full_name = ''
    password_match = True

    username = request.POST['username']
    password1 = request.POST['password1']
    password2 = request.POST['password2']
    email = request.POST['email']
    first_name = request.POST['first_name']
    last_name = request.POST['last_name']

    if password1 != password2:
        password_match = False
        return password_match, user_full_name

    User.objects.create_user(
        username=username,
        password=password1,
        email=email,
        first_name=first_name,
        last_name=last_name
    )
    user_full_name = f'{first_name} {last_name}'
    user = authenticate(username=username, password=password1)
    login(request, user)
    return password_match, user_full_name


def user_login_view(request):
    user_full_name = ''

    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)

    if user is None:
        is_logged_in = False
    else:
        login(request, user)
        is_logged_in = True
        user_full_name = f'{request.user.first_name} {request.user.last_name}'
    return is_logged_in, user_full_name


def homepage(request):
    context = {
        'username': '',
        'num_of_total_undone_form': count_notifications(),
        'number_of_importation_request': count_importation_request(),
        'user_id': request.user.id,
        'login_form': UserLoginForm(),
        'registration_form': UserRegistrationForm()
    }

    if request.user.is_authenticated:
        context['username'] = f'{request.user.first_name} {request.user.last_name}'
        return render(request, 'home/base.html', context)

    if request.method == 'POST':
        if 'log_in' in request.POST:
            is_logged_in, context['username'] = user_login_view(request)
            if is_logged_in:
                messages.success(request, 'Đăng nhập thành công')
            else:
                messages.error(request, 'Chưa đăng ký tài khoản')
            return redirect('homepage')

        elif 'register' in request.POST:
            password_match, context['username'] = user_registration_view(request)
            if password_match:
                messages.success(request, 'Đăng ký thành công')
            else:
                messages.error(request, 'Mật khẩu phải giống nhau')
                context['registration_form'] = UserRegistrationForm(request.POST)
                context['successfully_submit'] = True
            return redirect('homepage')

    return render(request, 'home/base.html', context)
