from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import PasswordChangeDoneView, PasswordChangeView
from django.core.management import call_command
from django.shortcuts import redirect, render
from django.utils import timezone

from .forms import (
    CustomLoginForm,
    RegistrationForm,
    ScholarshipFilterForm,
    ScholarshipRequestForm,
)
from .models import Scholarship, ScholarshipRequest


def home(request):
    return render(request, "scholarships/home.html")


def scholarship_list(request):
    scholarships = Scholarship.objects.all()
    filter_form = ScholarshipFilterForm(request.GET or None)

    if filter_form.is_valid():
        data = filter_form.cleaned_data

        # Filter by section
        if data["section"]:
            scholarships = scholarships.filter(section=data["section"])

        # Filter by scholarship name (partial match)
        if data["scholarship_name"]:
            scholarships = scholarships.filter(
                scholarship_name__icontains=data["scholarship_name"]
            )

        # Filter by qualifier (multiple choices)
        if data["qualifier"]:
            from django.db.models import Q
            qualifier_q = Q()
            for code in data["qualifier"]:
                qualifier_q |= Q(qualifier__icontains=code)

            scholarships = scholarships.filter(qualifier_q)

        # Filter by designated schools (partial match)
        if data["designated_schools"]:
            scholarships = scholarships.filter(
                designated_schools__icontains=data["designated_schools"]
            )

        # Filter by designated fields (partial match)
        if data["designated_fields"]:
            scholarships = scholarships.filter(
                designated_fields__icontains=data["designated_fields"]
            )

        # Filter by plural grants
        if data["plural_grants"]:
            scholarships = scholarships.filter(plural_grants=data["plural_grants"])

        # Filter by award amount range
        if data["award_amount_min"] or data["award_amount_max"]:
            import re

            from django.db.models import Q

            from .templatetags.scholarship_extras import extract_single_amount

            min_amount = data["award_amount_min"] or 0
            max_amount = data["award_amount_max"] or 1000000

            matching_ids = []
            for scholarship in scholarships:
                if not scholarship.contents:
                    continue

                contents = str(scholarship.contents).strip()
                # Normalize full-width characters
                contents = contents.replace('Ｍ', 'M').replace('Ｄ', 'D').replace('／', '/')

                # Skip variable amounts - include them in all ranges
                variable_indicators = ['not fixed', 'tba', 'tbc', 'to be announced', 'to be confirmed', 'variable']
                if any(indicator in contents.lower() for indicator in variable_indicators):
                    matching_ids.append(scholarship.id)
                    continue

                # Handle "Up to..." format - include if max amount is within range
                if 'up to' in contents.lower():
                    match = re.search(r'(\d+(?:-\d+)?)\s*[/／]?[MYmy月]', contents, re.IGNORECASE)
                    if match:
                        amount_part = match.group(1)
                        # Extract max value from range or single value
                        if '-' in amount_part or '−' in amount_part:
                            parts = re.split(r'[-−ー]', amount_part)
                            max_val = extract_single_amount(parts[-1], contents)
                        else:
                            max_val = extract_single_amount(amount_part, contents)

                        if max_val and max_val >= min_amount:
                            matching_ids.append(scholarship.id)
                    continue

                # Handle tiered amounts - use range
                tiered_pattern = r'(\d+(?:-\d+)?\s*[/／]?[MYmy月])'
                tiered_matches = re.findall(tiered_pattern, contents, re.IGNORECASE)
                if len(tiered_matches) > 1:
                    amounts = [extract_single_amount(match, contents) for match in tiered_matches]
                    valid_amounts = [a for a in amounts if a is not None]
                    if valid_amounts:
                        tier_min = min(valid_amounts)
                        tier_max = max(valid_amounts)
                        # Check if ranges overlap
                        if not (tier_max < min_amount or tier_min > max_amount):
                            matching_ids.append(scholarship.id)
                    continue

                # Handle range format
                range_pattern = r'(\d+)\s*[-−ー]\s*(\d+)\s*[/／]?([MYmy月])'
                range_match = re.search(range_pattern, contents, re.IGNORECASE)
                if range_match:
                    range_min = extract_single_amount(range_match.group(1), contents)
                    range_max = extract_single_amount(range_match.group(2), contents)
                    if range_min and range_max:
                        # Check if ranges overlap
                        if not (range_max < min_amount or range_min > max_amount):
                            matching_ids.append(scholarship.id)
                    continue

                # Handle single value format
                single_pattern = r'(\d+(?:-\d+)?)\s*[/／]?([MYmy月])'
                single_match = re.search(single_pattern, contents, re.IGNORECASE)
                if single_match:
                    amount = extract_single_amount(single_match.group(1), contents)
                    if amount and min_amount <= amount <= max_amount:
                        matching_ids.append(scholarship.id)
                    continue

            scholarships = scholarships.filter(id__in=matching_ids)

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
def request_form(request, scholarship_id):
    scholarship = Scholarship.objects.get(pk=scholarship_id)

    # Check if user already has a pending request for this scholarship
    existing_request = ScholarshipRequest.objects.filter(
        user=request.user,
        scholarship=scholarship,
        status='pending'
    ).first()

    if existing_request:
        messages.warning(request, "You already have a pending request for this scholarship.")
        return redirect("scholarship-detail", pk=scholarship_id)

    if request.method == "POST":
        form = ScholarshipRequestForm(request.POST)
        if form.is_valid():
            request_obj = form.save(commit=False)
            request_obj.user = request.user
            request_obj.scholarship = scholarship
            request_obj.status = 'pending'
            request_obj.save()
            messages.success(request, "Your scholarship request has been submitted and is pending admin approval!")
            return redirect("profile")
    else:
        form = ScholarshipRequestForm(initial={'scholarship': scholarship})

    return render(request, "scholarships/request_form.html", {
        "form": form,
        "scholarship": scholarship
    })


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
    user_requests = ScholarshipRequest.objects.filter(user=request.user).order_by('-created_at')
    return render(
        request,
        "scholarships/profile.html",
        {"user_requests": user_requests},
    )


# Admin views
@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    pending_requests = ScholarshipRequest.objects.filter(status='pending').count()
    total_requests = ScholarshipRequest.objects.count()
    recent_requests = ScholarshipRequest.objects.order_by('-created_at')[:10]

    return render(request, "scholarships/admin_dashboard.html", {
        'pending_requests': pending_requests,
        'total_requests': total_requests,
        'recent_requests': recent_requests
    })


@user_passes_test(lambda u: u.is_superuser)
def admin_requests(request):
    status_filter = request.GET.get('status', 'all')
    requests = ScholarshipRequest.objects.all()

    if status_filter != 'all':
        requests = requests.filter(status=status_filter)

    requests = requests.order_by('-created_at')

    return render(request, "scholarships/admin_requests.html", {
        'requests': requests,
        'status_filter': status_filter
    })


@user_passes_test(lambda u: u.is_superuser)
def admin_request_detail(request, pk):
    request_obj = ScholarshipRequest.objects.get(pk=pk)

    if request.method == "POST":
        action = request.POST.get('action')
        admin_notes = request.POST.get('admin_notes', '')

        if action in ['approve', 'reject']:
            request_obj.status = 'approved' if action == 'approve' else 'rejected'
            request_obj.admin_notes = admin_notes
            request_obj.reviewed_by = request.user
            request_obj.reviewed_date = timezone.now()
            request_obj.save()

            action_text = "approved" if action == 'approve' else "rejected"
            messages.success(request, f"Request {action_text} successfully.")
            return redirect("admin-requests")

    return render(request, "scholarships/admin_request_detail.html", {
        'request_obj': request_obj
    })


@user_passes_test(lambda u: u.is_superuser)
def reload_scholarships(request):
    """Admin endpoint to reload CSV data"""
    if request.method == "POST":
        try:
            call_command('import_scholarships', '--overwrite')
            messages.success(request, "Scholarships reloaded successfully from CSV!")
        except Exception as e:
            messages.error(request, f"Error reloading scholarships: {str(e)}")

        return redirect("admin-dashboard")

    return render(request, "scholarships/reload_scholarships.html")


class CustomPasswordChangeView(PasswordChangeView):
    template_name = "scholarships/password_change.html"
    success_url = "/password-change/done/"


class CustomPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = "scholarships/password_change_done.html"
