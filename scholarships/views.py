from django.shortcuts import get_object_or_404, redirect, render

from .forms import ScholarshipFilterForm, ScholarshipRequestForm, UserForm
from .models import Scholarship, User


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
    scholarship = get_object_or_404(Scholarship, pk=pk)
    return render(
        request,
        "scholarships/scholarship_detail.html",
        {"scholarship": scholarship},
    )


def request_form(request):
    if request.method == "POST":
        form = ScholarshipRequestForm(request.POST)
        if form.is_valid():
            request_obj = form.save()
            return render(
                request,
                "scholarships/request_success.html",
                {"request_obj": request_obj},
            )
    else:
        form = ScholarshipRequestForm()

    return render(request, "scholarships/request_form.html", {"form": form})


def user_create(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect("user-detail", pk=user.pk)
    else:
        form = UserForm()

    return render(request, "scholarships/user_form.html", {"form": form})


def user_detail(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    return render(
        request,
        "scholarships/user_detail.html",
        {"user_obj": user_obj},
    )
