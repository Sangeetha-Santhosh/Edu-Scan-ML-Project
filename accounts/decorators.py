from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


def teacher_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'TEACHER':
            messages.error(request, 'Please log in as a teacher to continue.')
            return redirect('accounts:teacher_login')
        return view_func(request, *args, **kwargs)
    return wrapper


def student_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'STUDENT':
            messages.error(request, 'Please log in as a student to continue.')
            return redirect('accounts:student_login')
        return view_func(request, *args, **kwargs)
    return wrapper
