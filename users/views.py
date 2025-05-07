from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib import messages
from django.http import HttpResponseForbidden
from .forms import CustomUserCreationForm, CustomUserUpdateForm
from timetable.models import ConflictReport

def landing_page(request):
    return render(request, 'landing.html')

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('landing_page')

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.role == 'admin':
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("You must be an Admin to access this page.")
    return wrapper

@admin_required
@login_required
def admin_dashboard(request):
    unresolved_conflicts = ConflictReport.objects.filter(is_resolved=False).order_by('-created_at')
    context = {
        'unresolved_conflicts': unresolved_conflicts,
        'unresolved_count': unresolved_conflicts.count(),
    }
    return render(request, 'admin_dashboard.html', context)

@login_required
def profile_view(request):
    if request.method == 'POST':
        # Handle account deletion
        if 'delete_account' in request.POST:
            request.user.delete()
            messages.success(request, 'Your account has been deleted.')
            return redirect('landing_page')

        # Handle profile update
        if 'update_profile' in request.POST:
            form = CustomUserUpdateForm(request.POST, request.FILES, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your profile has been updated.')
                return redirect('profile')

        # Handle password change
        if 'change_password' in request.POST:
            password_form = PasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, password_form.user)  # Keep user logged in
                messages.success(request, 'Your password has been updated.')
                return redirect('profile')
            else:
                messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserUpdateForm(instance=request.user)
        password_form = PasswordChangeForm(user=request.user)

    return render(request, 'profile.html', {'form': form, 'password_form': password_form})