from django import forms
from .models import Kefir


class KefirForm(forms.ModelForm):
    class Meta:
        model = Kefir
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
