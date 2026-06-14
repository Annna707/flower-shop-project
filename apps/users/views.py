from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm
from django.shortcuts import redirect, render

from .forms import ProfileEditForm
from .models import Profile


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('catalog:product_list')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request):
    Profile.objects.get_or_create(user=request.user)
    return render(request, 'users/profile.html')


@login_required
def profile_edit(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileEditForm(request.user, request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлён.')
            return redirect('users:profile')
    else:
        form = ProfileEditForm(request.user, instance=profile)
    return render(request, 'users/profile_edit.html', {'form': form})