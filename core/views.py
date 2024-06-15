from django.shortcuts import render
from braces.views import LoginRequiredMixin as BracesLoginRequiredMixin
from django.views.generic import TemplateView

# Create your views here.


class DashboardView(BracesLoginRequiredMixin, TemplateView):
    template_name = "core/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Dashboard"
        return context
