from django.urls import path

from . import views

app_name = 'detector'
urlpatterns = [
    path('check/<int:submission_id>/', views.check_submission, name='check_submission'),
]
