from django import forms

from company.models import Company


class CompanyCreateForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = [
            "name",
            "email",
            "address",
            "phone",
            "description",
            "website",
            "established_date",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "address": forms.Textarea(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.TextInput(attrs={"class": "form-control"}),
            "website": forms.TextInput(attrs={"class": "form-control"}),
            "established_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
        }
