from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend

User = get_user_model()


class StudentDOBBackend(BaseBackend):
    """
    Authenticates students using register number + date of birth
    instead of a password. Used only for accounts with role=STUDENT.
    """

    def authenticate(self, request, reg_number=None, dob=None, **kwargs):
        if not reg_number or not dob:
            return None
        from assignments.models import StudentProfile
        try:
            profile = StudentProfile.objects.select_related('user').get(
                reg_number=reg_number, dob=dob
            )
            return profile.user
        except StudentProfile.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
