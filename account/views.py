from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import reverse_lazy
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse
from django.views.generic.edit import CreateView, FormView

from account.forms import RegisterForm


def login_user(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("core:dashboard"))
    next = request.GET.get("next", "")
    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            if next:
                return HttpResponseRedirect(next)
            return HttpResponseRedirect(reverse("core:dashboard"))
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, "account/login.html")


def logout_user(request):
    logout(request)
    return HttpResponseRedirect(reverse("account:login"))


class RegisterUserView(FormView):
    template_name = "account/register.html"
    form_class = RegisterForm
    success_url = reverse_lazy("account:login")

    def form_valid(self, form):
        if form.is_valid():
            response = form.save()
            info = response.get("info")
            if response.get("status") == "success":
                messages.success(self.request, info)
                return super().form_valid(form)
            else:
                messages.error(self.request, info)
                return super().form_invalid(form)
        else:
            messages.error(self.request, "Invalid form")
            return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Registration Page"
        return context
