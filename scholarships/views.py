from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import PasswordChangeDoneView, PasswordChangeView
from django.shortcuts import redirect, render

from .forms import (
    CustomLoginForm,
    RegistrationForm,
    ScholarshipFilterForm,
    ScholarshipRequestForm,
)
from .models import Scholarship, ScholarshipRequest, User


def home(request):
    return render(request, "scholarships/home.html")


def scholarship_list(request):
    scholarships = Scholarship.objects.all()
    filter_form = ScholarshipFilterForm(request.GET or None)

    if filter_form.is_valid():
        data = filter_form.cleaned_data
        if data["education_level"]:
            scholarships = scholarships.filter(education_level=data["education_level"])
        if data["discipline"]:
            scholarships = scholarships.filter(discipline=data["discipline"])
        if data["prefecture"]:
            scholarships = scholarships.filter(prefecture=data["prefecture"])

    return render(
        request,
        "scholarships/scholarship_list.html",
        {"scholarships": scholarships, "filter_form": filter_form},
    )


def scholarship_detail(request, pk):
    scholarship = Scholarship.objects.get(pk=pk)
    return render(
        request,
        "scholarships/scholarship_detail.html",
        {"scholarship": scholarship},
    )


@login_required
def request_form(request):
    if request.method == "POST":
        form = ScholarshipRequestForm(request.POST)
        if form.is_valid():
            request_obj = form.save(commit=False)
            request_obj.user = request.user
            request_obj.save()
            messages.success(request, "Your scholarship request has been submitted!")
            return redirect("profile")
    else:
        form = ScholarshipRequestForm()

    return render(request, "scholarships/request_form.html", {"form": form})


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            email = form.cleaned_data.get("email")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=email, password=raw_password)
            login(request, user)
            messages.success(request, "Registration successful! You are now logged in.")
            return redirect("profile")
    else:
        form = RegistrationForm()

    return render(request, "scholarships/register.html", {"form": form})


def user_login(request):
    if request.method == "POST":
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Login successful!")
                next_url = request.GET.get("next", "profile")
                return redirect(next_url)
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = CustomLoginForm()

    return render(request, "scholarships/login.html", {"form": form})


def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("login")


@login_required
def profile(request):
    user_requests = ScholarshipRequest.objects.filter(user=request.user)
    return render(
        request,
        "scholarships/profile.html",
        {"user_requests": user_requests},
    )


class CustomPasswordChangeView(PasswordChangeView):
    template_name = "scholarships/password_change.html"
    success_url = "/password-change/done/"


class CustomPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = "scholarships/password_change_done.html"
