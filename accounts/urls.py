from django.urls import path

from . import views

app_name = 'accounts'
urlpatterns = [
    path('', views.home, name='home'),
    path('teacher-login/', views.teacher_login, name='teacher_login'),
    path('student-login/', views.student_login, name='student_login'),
    path('logout/', views.logout_view, name='logout'),
]
