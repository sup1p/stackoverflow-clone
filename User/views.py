from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserChangeForm
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages

from Post.models import Question, Answer
from .forms import CustomUserCreationForm, CustomUserLoginForm, ProfileEditForm
from .models import CustomUser

# Регистрация
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, 'signup.html')

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email is already taken.")
            return render(request, 'signup.html')

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken.")
            return render(request, 'signup.html')

        user = CustomUser.objects.create_user(username=username, email=email, password=password1)
        login(request, user)
        messages.success(request, "You have successfully registered!")
        return redirect('index')

    return render(request, 'signup.html')

# Логин
def login_view(request):
    if request.method == 'POST':
        form = CustomUserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome, {user.username}!')
                return redirect('index')
            else:
                messages.error(request, 'Invalid email or password.')
    else:
        form = CustomUserLoginForm()
    return render(request, 'login.html', {'form': form})

# Логаут
def logout_view(request):
    logout(request)
    messages.info(request, 'You have successfully logged out.')
    return redirect('index')


@login_required
def profile_view(request):
    user = request.user
    questions = Question.objects.filter(author=user)
    answers = Answer.objects.filter(author=user)

    context = {
        'user': user,
        'questions': questions,
        'answers': answers
    }
    return render(request, 'profile.html', context)

@login_required
def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileEditForm(request.POST,request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('profile')
        else:
            messages.error(request, 'Something went wrong')
    else:
        form = ProfileEditForm(instance=user)
        return render(request, 'edit_profile.html', {'form': form})
