from django import forms
from django.forms import formset_factory
from .models import Student, Subject, Result, CLASS_YEARS

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['student_id', 'name', 'class_year', 'combination'] 

class AssignSubjectsForm(forms.Form):
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.none(),
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, **kwargs):
        level = kwargs.pop('level', None)
        super().__init__(*args, **kwargs)
        if level:
            self.fields['subjects'].queryset = Subject.objects.filter(level=level)

class ResultForm(forms.ModelForm):
    class Meta:
        model = Result
        fields = ['subject', 'score']
        widgets = {
            'subject': forms.HiddenInput(),
            'score': forms.NumberInput(attrs={'min': 0, 'max': 100, 'class': 'form-control'}),
        }

    def clean_score(self):
        score = self.cleaned_data['score']
        if not (0 <= score <= 100):
            raise forms.ValidationError("Score must be between 0 and 100.")
        return score

ResultFormSet = formset_factory(ResultForm, extra=0)

class BulkResultForm(forms.ModelForm):
    class Meta:
        model = Result
        fields = ['student', 'subject', 'score']
        widgets = {
            'student': forms.HiddenInput(),
            'subject': forms.HiddenInput(),
            'score': forms.NumberInput(attrs={'min': 0, 'max': 100, 'class': 'form-control'}),
        }

    def clean_score(self):
        score = self.cleaned_data['score']
        if not (0 <= score <= 100):
            raise forms.ValidationError("Score must be between 0 and 100.")
        return score

BulkResultFormSet = formset_factory(BulkResultForm, extra=0)

class BulkSelectForm(forms.Form):
    class_year = forms.ChoiceField(choices=CLASS_YEARS)
    combination = forms.CharField(max_length=50, required=False)  # Updated
    subject = forms.ModelChoiceField(queryset=Subject.objects.all())

    def clean(self):
        cleaned_data = super().clean()
        class_year = cleaned_data.get('class_year')
        subject = cleaned_data.get('subject')
        if class_year and subject:
            level = 'O' if class_year in ['S1', 'S2', 'S3', 'S4'] else 'A'
            if subject.level != level:
                raise forms.ValidationError("Subject does not match the level for this class year.")
        return cleaned_data