from django.db import models

from assignments.models import Submission


class AnalysisResult(models.Model):
    submission = models.OneToOneField(Submission, on_delete=models.CASCADE, related_name='analysis')
    predicted_label = models.CharField(max_length=30)
    ai_probability = models.FloatField(help_text='Estimated % likelihood the text is AI-generated')
    human_probability = models.FloatField(help_text='Estimated % likelihood the text is human-written')
    top_ai_terms = models.JSONField(default=list, blank=True)
    top_human_terms = models.JSONField(default=list, blank=True)
    analyzed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.submission} -> {self.predicted_label} ({self.ai_probability}% AI)'
