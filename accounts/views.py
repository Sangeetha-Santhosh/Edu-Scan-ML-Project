from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render

from .forms import StudentLoginForm


def home(request):
    return render(request, 'accounts/home.html')


def teacher_login(request):
    if request.user.is_authenticated and request.user.role == 'TEACHER':
        return redirect('assignments:teacher_dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.role != 'TEACHER':
                messages.error(request, 'This account is not registered as a teacher.')
            else:
                login(request, user)
                return redirect('assignments:teacher_dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/teacher_login.html', {'form': form})


def student_login(request):
    if request.user.is_authenticated and request.user.role == 'STUDENT':
        return redirect('assignments:student_dashboard')

    if request.method == 'POST':
        form = StudentLoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                reg_number=form.cleaned_data['reg_number'],
                dob=form.cleaned_data['dob'],
            )
            if user is not None:
                login(request, user)
                return redirect('assignments:student_dashboard')
            messages.error(request, 'No student found with that register number and date of birth.')
    else:
        form = StudentLoginForm()
    return render(request, 'accounts/student_login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('accounts:home')
