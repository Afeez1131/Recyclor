from django import forms

from customer.models import Customer, ServiceHistory


class CreateCustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            "name",
            "email",
            "address",
            "phone",
            "schedule",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "address": forms.Textarea(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "schedule": forms.TextInput(attrs={"class": "form-control"}),
        }


class CreateServiceHistory(forms.ModelForm):
    class Meta:
        model = ServiceHistory
        fields = ["cost"]
        labels = {
            "cost": "Cost of Service",
        }
        widgets = {
            "cost": forms.NumberInput(attrs={"class": "form-control"}),
        }
        
    def clean(self):
        cleaned_data = super().clean()
        cost = cleaned_data.get("cost", 0)
        if cost <= 0:
            self.add_error("cost", "Cost cannot be negative")
        return cleaned_data