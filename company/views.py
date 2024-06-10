from django.shortcuts import render
from braces.views import LoginRequiredMixin as BracesLoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView, CreateView
from django.contrib import messages

from company.forms import CompanyCreateForm
from company.models import Company
# Create your views here.

class CreateCompanyView(BracesLoginRequiredMixin, CreateView):
    model = Company
    form_class = CompanyCreateForm
    template_name = "company/create_company.html"
    success_url = reverse_lazy("core:dashboard")
    
    def get_success_url(self):
        obj = self.object
        messages.success(self.request, f"{obj.name} has been created successfully")
        return self.success_url
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Create Company"
        return context
        
        
class UpdateCompanyView(BracesLoginRequiredMixin, UpdateView):
    model = Company
    form_class = CompanyCreateForm
    template_name = "company/update_company.html"
    success_url = reverse_lazy("core:dashboard")
    
    def get_success_url(self):
        obj = self.get_object()
        messages.success(self.request, f"{obj.name} has been updated successfully")
        return self.success_url
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Update {self.get_object().name}"
        return context 
