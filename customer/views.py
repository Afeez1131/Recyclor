from braces.views import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from customer.forms import CreateCustomerForm
from customer.models import Customer

class CreateCustomerView(LoginRequiredMixin, CreateView):
    template_name = "customer/create.html"
    model = Customer
    form_class = CreateCustomerForm
    success_url = reverse_lazy("core:dashboard")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Register as a Customer"
        return context
        
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
        
        
class UpdateCustomerView(LoginRequiredMixin, UpdateView):
    model = Customer
    template_name = "customer/update.html"
    form_class = CreateCustomerForm
    success_url = reverse_lazy("core:dashboard")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Update Customer Information"
        return context