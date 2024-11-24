from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "rows": 2,
                    "style": "width: 100%;", 
                    "placeholder": "Write your review here...",
                }
                        ),
        }

class SearchForm(forms.Form):
    query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Search for books...", "class": "form-control"}),
    )

