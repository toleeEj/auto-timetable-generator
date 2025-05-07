from django import forms
from .models import Feedback
from timetable.models import Class

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['message', 'related_class']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4}),
        }