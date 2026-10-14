from django.conf import settings
from django.db import models


class StudentProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile'
    )
    name = models.CharField(max_length=150)
    reg_number = models.CharField(max_length=50, unique=True)
    dob = models.DateField()
    department = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f'{self.name} ({self.reg_number})'


class Assignment(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assignments_created'
    )
    students = models.ManyToManyField(StudentProfile, related_name='assignments')
    seen_by_students = models.ManyToManyField(
        StudentProfile, related_name='seen_assignments', blank=True
    )
    attachment = models.FileField(upload_to='assignment_files/', blank=True, null=True)
    due_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Submission(models.Model):
    STATUS_SUBMITTED = 'SUBMITTED'
    STATUS_CHECKED = 'CHECKED'
    STATUS_CHOICES = (
        (STATUS_SUBMITTED, 'Submitted'),
        (STATUS_CHECKED, 'Checked'),
    )

    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='submissions')
    file = models.FileField(upload_to='submissions/')
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_SUBMITTED)
    seen_by_teacher = models.BooleanField(default=False)

    class Meta:
        unique_together = ('assignment', 'student')
        ordering = ['-submitted_at']

    def __str__(self):
        return f'{self.student.name} -> {self.assignment.title}'


class ReallotHistory(models.Model):
    """Keeps a short audit trail whenever a teacher sends an assignment
    back to a student because the AI-detection score was too high."""
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='reallotments')
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='reallotments')
    previous_ai_probability = models.FloatField()
    reallotted_at = models.DateTimeField(auto_now_add=True)
    seen_by_student = models.BooleanField(default=False)

    class Meta:
        ordering = ['-reallotted_at']

    def __str__(self):
        return f'{self.student.name} reallotted for {self.assignment.title}'
