from django import forms


class StudentLoginForm(forms.Form):
    reg_number = forms.CharField(label='Register Number', max_length=50)
    dob = forms.DateField(
        label='Date of Birth',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
