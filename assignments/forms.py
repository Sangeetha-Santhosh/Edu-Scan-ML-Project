from django import forms

from .models import Assignment, StudentProfile, Submission


class AddStudentForm(forms.Form):
    name = forms.CharField(max_length=150)
    reg_number = forms.CharField(max_length=50)
    dob = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    department = forms.CharField(max_length=100, required=False)

    def clean_reg_number(self):
        reg_number = self.cleaned_data['reg_number']
        if StudentProfile.objects.filter(reg_number=reg_number).exists():
            raise forms.ValidationError('A student with this register number already exists.')
        return reg_number


class AssignmentForm(forms.ModelForm):
    students = forms.ModelMultipleChoiceField(
        queryset=StudentProfile.objects.all().order_by('name'),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        help_text='All students are selected by default — untick anyone who should not receive this assignment.',
    )

    class Meta:
        model = Assignment
        fields = ['title', 'description', 'due_date', 'attachment', 'students']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['file']
        help_texts = {'file': 'Accepted formats: .txt, .docx, .pdf'}
