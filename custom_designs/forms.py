from django import forms
import json
from .models import CustomDesign
class CustomDesignForm(forms.ModelForm):
    class Meta:
        model = CustomDesign
        fields = '__all__'
    
    def clean_selected_color(self):
        color_data = self.cleaned_data.get('selected_color')
        if not color_data:
            raise forms.ValidationError("Color selection is required")
    
        try:
            color_json = json.loads(color_data)
            if not color_json.get('hex') or not color_json.get('name'):
                raise forms.ValidationError("Invalid color format")
            return color_json
        except json.JSONDecodeError:
            raise forms.ValidationError("Invalid color data format")
