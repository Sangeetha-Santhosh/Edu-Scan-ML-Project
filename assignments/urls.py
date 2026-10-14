from django.urls import path

from . import views

app_name = 'assignments'
urlpatterns = [
    path('teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/add-student/', views.add_student, name='add_student'),
    path('teacher/create/', views.create_assignment, name='create_assignment'),
    path('teacher/assignment/<int:pk>/', views.assignment_detail_teacher, name='assignment_detail_teacher'),
    path('teacher/submission/<int:submission_id>/download/', views.download_submission, name='download_submission'),
    path('teacher/submission/<int:submission_id>/reallot/', views.reallot_submission, name='reallot_submission'),
    path('student/', views.student_dashboard, name='student_dashboard'),
    path('student/assignment/<int:pk>/', views.assignment_detail_student, name='assignment_detail_student'),
]
