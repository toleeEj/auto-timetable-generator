from django import forms
from .models import Class, ConflictReport

class ConflictReportForm(forms.ModelForm):
    class Meta:
        model = ConflictReport
        fields = ['classes', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['classes'].queryset = Class.objects.filter(
            course__in=user.enrollment_set.values('course'),
            section__in=user.enrollment_set.values('section')
        ).distinct() if user.role == 'student' else Class.objects.filter(faculty=user)
        # Pre-select classes from user's PotentialConflict
        if user:
            potential_conflict = user.potentialconflict_set.first()
            if potential_conflict:
                self.fields['classes'].initial = potential_conflict.classes.all()