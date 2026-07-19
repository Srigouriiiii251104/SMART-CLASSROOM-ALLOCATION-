from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView
from django.views.decorators.http import require_POST

from .forms import RoleAwareLoginForm, SignupForm
from .models import User


class RoleAwareLoginView(LoginView):
    template_name = "registration/login.html"
    authentication_form = RoleAwareLoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return self.get_redirect_url() or reverse("dashboard:home")

    def get_initial(self):
        initial = super().get_initial()
        requested_role = self.request.GET.get("role")
        initial["role"] = requested_role if requested_role in {choice[0] for choice in User.ROLE_CHOICES} else User.ROLE_STUDENT
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context.get("form")
        context["selected_role"] = (form["role"].value() if form else None) or self.get_initial()["role"]
        return context


class SignupView(FormView):
    template_name = "accounts/signup.html"
    form_class = SignupForm
    success_url = reverse_lazy("dashboard:home")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("dashboard:home")
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        requested_role = self.request.GET.get("role")
        initial["role"] = requested_role if requested_role in {choice[0] for choice in User.ROLE_CHOICES} else User.ROLE_STUDENT
        return initial

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, f"Welcome, {user.display_name}. Your account has been created.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context.get("form")
        context["selected_role"] = (form["role"].value() if form else None) or self.get_initial()["role"]
        return context


def role_based_redirect(request):
    if not request.user.is_authenticated:
        return redirect("login")
    return redirect("dashboard:home")


@login_required
def profile_view(request):
    return render(request, "accounts/profile.html", {"profile_user": request.user})


@login_required
@require_POST
def toggle_theme(request):
    current_theme = request.session.get("theme", "light")
    request.session["theme"] = "dark" if current_theme == "light" else "light"
    messages.success(request, f"Theme switched to {request.session['theme']} mode.")
    return redirect(request.POST.get("next") or reverse("dashboard:home"))
