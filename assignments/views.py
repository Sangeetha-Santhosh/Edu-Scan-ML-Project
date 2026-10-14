from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import student_required, teacher_required
from accounts.models import User

from .forms import AddStudentForm, AssignmentForm, SubmissionForm
from .models import Assignment, ReallotHistory, StudentProfile, Submission


@teacher_required
def teacher_dashboard(request):
    assignments = Assignment.objects.filter(created_by=request.user)
    students = StudentProfile.objects.all().order_by('name')
    return render(request, 'assignments/teacher_dashboard.html', {
        'assignments': assignments,
        'students': students,
    })


@teacher_required
def add_student(request):
    if request.method == 'POST':
        form = AddStudentForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = User(
                username=data['reg_number'],
                first_name=data['name'],
                role=User.ROLE_STUDENT,
                password=make_password(None),
            )
            user.set_unusable_password()
            user.save()
            StudentProfile.objects.create(
                user=user,
                name=data['name'],
                reg_number=data['reg_number'],
                dob=data['dob'],
                department=data.get('department', ''),
            )
            messages.success(request, f"Student \"{data['name']}\" added successfully.")
            return redirect('assignments:teacher_dashboard')
    else:
        form = AddStudentForm()
    return render(request, 'assignments/add_student.html', {'form': form})


@teacher_required
def create_assignment(request):
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.created_by = request.user
            assignment.save()
            form.save_m2m()
            messages.success(request, 'Assignment created and sent to the selected students.')
            return redirect('assignments:teacher_dashboard')
    else:
        # Default: allot to every current student. Teacher can untick anyone.
        form = AssignmentForm(initial={
            'students': StudentProfile.objects.all().values_list('id', flat=True)
        })
    return render(request, 'assignments/create_assignment.html', {'form': form})


@teacher_required
def assignment_detail_teacher(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk, created_by=request.user)
    submissions = assignment.submissions.select_related('student', 'analysis').all()

    # Viewing this page counts as reviewing any new submissions on it.
    submissions.filter(seen_by_teacher=False).update(seen_by_teacher=True)

    submitted_student_ids = set(submissions.values_list('student_id', flat=True))
    pending_students = assignment.students.exclude(id__in=submitted_student_ids)
    return render(request, 'assignments/assignment_detail_teacher.html', {
        'assignment': assignment,
        'submissions': submissions,
        'pending_students': pending_students,
    })


@teacher_required
def download_submission(request, submission_id):
    submission = get_object_or_404(
        Submission, pk=submission_id, assignment__created_by=request.user
    )
    if not submission.file:
        raise Http404('No file attached to this submission.')
    filename = submission.file.name.split('/')[-1]
    return FileResponse(submission.file.open('rb'), as_attachment=True, filename=filename)


@teacher_required
def reallot_submission(request, submission_id):
    """Sends the assignment back to the student because the AI-detection
    score came back too high. Logs the previous score and clears the
    submission so the student can upload a fresh attempt."""
    submission = get_object_or_404(
        Submission, pk=submission_id, assignment__created_by=request.user
    )
    analysis = getattr(submission, 'analysis', None)
    if request.method != 'POST' or not analysis or analysis.ai_probability <= 50:
        messages.error(request, 'This submission is not eligible for reallotment.')
        return redirect('assignments:assignment_detail_teacher', pk=submission.assignment_id)

    ReallotHistory.objects.create(
        assignment=submission.assignment,
        student=submission.student,
        previous_ai_probability=analysis.ai_probability,
    )
    student_name = submission.student.name
    submission.delete()  # cascades to delete the AnalysisResult too

    messages.success(request, f'Assignment reallotted to {student_name} for resubmission.')
    return redirect('assignments:assignment_detail_teacher', pk=submission.assignment_id)


@student_required
def student_dashboard(request):
    profile = request.user.student_profile
    assignments = profile.assignments.all()
    submitted_ids = set(profile.submissions.values_list('assignment_id', flat=True))
    recent_reallotments = profile.reallotments.filter(seen_by_student=False)
    return render(request, 'assignments/student_dashboard.html', {
        'assignments': assignments,
        'submitted_ids': submitted_ids,
        'recent_reallotments': recent_reallotments,
    })


@student_required
def assignment_detail_student(request, pk):
    profile = request.user.student_profile
    assignment = get_object_or_404(profile.assignments, pk=pk)

    # Mark this assignment as opened, and clear any reallotment notice for it.
    assignment.seen_by_students.add(profile)
    assignment.reallotments.filter(student=profile, seen_by_student=False).update(seen_by_student=True)

    existing = Submission.objects.filter(assignment=assignment, student=profile).first()
    was_reallotted = assignment.reallotments.filter(student=profile).exists()

    if request.method == 'POST' and not existing:
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.assignment = assignment
            submission.student = profile
            submission.save()
            messages.success(request, 'Assignment submitted successfully.')
            return redirect('assignments:student_dashboard')
    else:
        form = SubmissionForm()

    return render(request, 'assignments/assignment_detail_student.html', {
        'assignment': assignment,
        'form': form,
        'existing': existing,
        'was_reallotted': was_reallotted,
    })
