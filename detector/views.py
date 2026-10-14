from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import teacher_required
from assignments.models import Submission

from .models import AnalysisResult
from .utils import extract_text, predict


@teacher_required
def check_submission(request, submission_id):
    submission = get_object_or_404(
        Submission, pk=submission_id, assignment__created_by=request.user
    )
    try:
        text = extract_text(submission.file)
        if not text.strip():
            raise ValueError('No readable text was found in this file.')
        result = predict(text)
    except Exception as exc:
        messages.error(request, f'Could not analyze this file: {exc}')
        return redirect('assignments:assignment_detail_teacher', pk=submission.assignment_id)

    analysis, _ = AnalysisResult.objects.update_or_create(
        submission=submission,
        defaults={
            'predicted_label': result['label'],
            'ai_probability': result['ai_probability'],
            'human_probability': result['human_probability'],
            'top_ai_terms': result['top_ai_terms'],
            'top_human_terms': result['top_human_terms'],
        },
    )
    submission.status = Submission.STATUS_CHECKED
    submission.seen_by_teacher = True
    submission.save(update_fields=['status', 'seen_by_teacher'])

    ai_terms = analysis.top_ai_terms or []
    human_terms = analysis.top_human_terms or []
    max_ai = max([abs(score) for _, score in ai_terms], default=1) or 1
    max_human = max([abs(score) for _, score in human_terms], default=1) or 1
    ai_terms_display = [
        {'word': w, 'score': s, 'width': round(abs(s) / max_ai * 100, 1)} for w, s in ai_terms
    ]
    human_terms_display = [
        {'word': w, 'score': s, 'width': round(abs(s) / max_human * 100, 1)} for w, s in human_terms
    ]

    return render(request, 'detector/result.html', {
        'submission': submission,
        'analysis': analysis,
        'ai_terms_display': ai_terms_display,
        'human_terms_display': human_terms_display,
    })
