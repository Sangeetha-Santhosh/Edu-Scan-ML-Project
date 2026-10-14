from django.contrib import admin

from .models import Assignment, StudentProfile, Submission

admin.site.register(StudentProfile)
admin.site.register(Assignment)
admin.site.register(Submission)
