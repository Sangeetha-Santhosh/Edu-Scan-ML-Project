from assignments.models import ReallotHistory, Submission


def notification_counts(request):
    """
    Powers the notification bells in the navbar.

    Student: bell 1 = assignments allotted but not yet opened.
             bell 2 = reallotment notices (work sent back) not yet seen.
    Teacher: bell   = student submissions not yet reviewed.
    """
    data = {
        'unseen_assignments': 0,
        'unseen_reports': 0,
        'unseen_assignment_list': [],
        'unseen_report_list': [],
    }
    user = getattr(request, 'user', None)

    if not user or not user.is_authenticated:
        return data

    if getattr(user, 'role', None) == 'STUDENT' and hasattr(user, 'student_profile'):
        profile = user.student_profile
        unseen_assignments = profile.assignments.exclude(
            id__in=profile.seen_assignments.values_list('id', flat=True)
        ).order_by('-created_at')
        unseen_reports = ReallotHistory.objects.filter(
            student=profile, seen_by_student=False
        ).select_related('assignment')

        data['unseen_assignments'] = unseen_assignments.count()
        data['unseen_reports'] = unseen_reports.count()
        data['unseen_assignment_list'] = list(unseen_assignments[:6])
        data['unseen_report_list'] = list(unseen_reports[:6])

    elif getattr(user, 'role', None) == 'TEACHER':
        unseen_reports = Submission.objects.filter(
            assignment__created_by=user, seen_by_teacher=False
        ).select_related('assignment', 'student')

        data['unseen_reports'] = unseen_reports.count()
        data['unseen_report_list'] = list(unseen_reports[:6])

    return data
