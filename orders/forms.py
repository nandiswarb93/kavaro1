from django import forms
from .models import ReturnRequest
from django.utils import timezone

class ReturnPickupForm(forms.ModelForm):
    class Meta:
        model = ReturnRequest
        fields = []  # No fields needed; we'll set pickup_scheduled_at automatically

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.pickup_scheduled_at = timezone.now()
        instance.status = 'pickup_scheduled'
        if commit:
            instance.save()
        return instance
