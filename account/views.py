from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.generic.edit import CreateView


def login_user(request):
    next = request.GET.get("next", "")
    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            if next:
                return HttpResponseRedirect(next)
            return HttpResponseRedirect("/")
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, "account/login.html")


def logout_user(request):
    logout(request)
    return HttpResponseRedirect("/")


class RegisterUserView(CreateView):
    template_name = "account/register.html"

    def form_valid(self, form):
        response = form.save()
        if response.get("status") == "success":
            return super().form_valid(form)
        return super().form_invalid(form)
