import logging
import re

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import PasswordChangeDoneView, PasswordChangeView
from django.core.management import call_command
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Exists, OuterRef, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import (
    CustomLoginForm,
    RegistrationForm,
    ScholarshipFilterForm,
    ScholarshipRequestForm,
)
from .models import Favorite, Scholarship, ScholarshipRequest

logger = logging.getLogger(__name__)

SCHOLARSHIP_PAGE_SIZE = 12


def extract_max_award_value(contents):
    """
    Extract the maximum award value from contents.
    For ranges (e.g., "25-41,000"), use the MAXIMUM value.
    Returns monthly value as integer, or None if parsing fails.
    """
    if not contents:
        return None

    try:
        contents = str(contents).strip()

        # Normalize full-width characters and hyphens
        contents = contents.replace("Ｍ", "M").replace("Ｄ", "D").replace("／", "/")
        contents = contents.replace("−", "-").replace("ー", "-")

        # Find all amount patterns with their time units
        # Pattern: number(s) + optional range + optional time unit
        amount_pattern = (
            r"(\d[\d,]*)(?:\s*[-−ー]\s*(\d[\d,]*))?\s*(?:/|／)?\s*([YMymy年月])?"
        )
        matches = re.findall(amount_pattern, contents, re.IGNORECASE)

        max_monthly_value = 0

        for match in matches:
            part1, part2, time_unit = match

            # Clean numbers (remove commas)
            part1_clean = part1.replace(",", "") if part1 else "0"
            part2_clean = part2.replace(",", "") if part2 else None

            # Get the maximum value from this match
            if part2_clean:
                # It's a range - use MAXIMUM value
                try:
                    match_value = float(part2_clean)
                except ValueError:
                    continue
            else:
                # It's a single value
                try:
                    match_value = float(part1_clean)
                except ValueError:
                    continue

            # CSV values are in ¥1,000 units
            match_value = match_value * 1000

            # Convert to monthly if yearly
            time_unit = time_unit.upper() if time_unit else ""
            if time_unit in ["Y", "年"]:
                monthly_value = match_value / 12
            else:
                # Assume monthly if not explicitly yearly
                monthly_value = match_value

            # Track maximum
            if monthly_value > max_monthly_value:
                max_monthly_value = monthly_value

        # If no structured pattern found, try to find any large number
        if max_monthly_value == 0:
            # Look for any numbers in the text
            all_numbers = re.findall(r"\d[\d,]*", contents)
            if all_numbers:
                # Use the largest number found
                clean_numbers = []
                for n in all_numbers:
                    try:
                        clean_numbers.append(float(n.replace(",", "")))
                    except ValueError:
                        continue

                if clean_numbers:
                    max_monthly_value = (
                        max(clean_numbers) * 1000
                    )  # CSV values are in ¥1,000 units
                    # Assume it's yearly if very large
                    if max_monthly_value > 500000:
                        max_monthly_value = max_monthly_value / 12

        return int(max_monthly_value) if max_monthly_value > 0 else None

    except (ValueError, TypeError, AttributeError) as e:
        logger.warning(f"Error extracting max award value: {str(e)}")
        return None


def filter_scholarships(queryset, data):
    """Apply ``ScholarshipFilterForm`` cleaned data to a Scholarship queryset.

    Shared by the full-page and HTMX code paths so filtering behavior stays
    consistent.
    """
    if data["section"]:
        queryset = queryset.filter(section=data["section"])

    if data["scholarship_name"]:
        queryset = queryset.filter(scholarship_name__icontains=data["scholarship_name"])

    if data["qualifier"]:
        qualifier_q = Q()
        for code in data["qualifier"]:
            try:
                if not code or not isinstance(code, str):
                    continue
                clean_code = re.sub(r"[^\w\(\)\-]", "", code).strip()
                if not clean_code:
                    continue
                if not re.match(r"^[A-Za-z]+(?:\d+)?(?:\([^)]*\))?$", clean_code):
                    logger.warning(f"Invalid qualifier code format: '{code}'")
                    continue
                qualifier_q |= Q(qualifier__icontains=clean_code)
            except (re.error, ValueError, TypeError) as e:
                logger.warning(f"Invalid qualifier code '{code}': {str(e)}")
                continue
            except Exception as e:
                logger.error(
                    f"Unexpected error processing qualifier code '{code}': {str(e)}"
                )
                continue
        if qualifier_q:
            queryset = queryset.filter(qualifier_q)

    if data["designated_schools"]:
        queryset = queryset.filter(
            designated_schools__icontains=data["designated_schools"]
        )

    if data["designated_fields"]:
        queryset = queryset.filter(
            designated_fields__icontains=data["designated_fields"]
        )

    if data["plural_grants"]:
        queryset = queryset.filter(plural_grants=data["plural_grants"])

    # Minimum award amount: filtered in Python (parsed from free-text contents)
    # before pagination so page size stays bounded.
    if data.get("award_amount_min") is not None:
        min_amount = max(0, min(data["award_amount_min"], 600000))
        variable_indicators = [
            "not fixed",
            "tba",
            "tbc",
            "to be announced",
            "to be confirmed",
            "variable",
            "未定",
            "未確定",
        ]
        matching_ids = []
        for scholarship in queryset:
            if not scholarship.contents:
                continue
            contents = (
                str(scholarship.contents)
                .strip()
                .replace("Ｍ", "M")
                .replace("Ｄ", "D")
                .replace("／", "/")
            )
            if any(indicator in contents.lower() for indicator in variable_indicators):
                matching_ids.append(scholarship.id)
                continue
            max_award_value = extract_max_award_value(contents)
            if max_award_value is not None and max_award_value >= min_amount:
                matching_ids.append(scholarship.id)
        queryset = queryset.filter(id__in=matching_ids)

    return queryset


def annotate_favorited(queryset, user):
    """Annotate each scholarship with an ``is_favorited`` boolean for ``user``.

    Anonymous users get the queryset back unchanged. Uses an ``Exists``
    subquery so the list renders without an N+1 hit.
    """
    if not user.is_authenticated:
        return queryset
    fav_exists = Favorite.objects.filter(user=user, scholarship=OuterRef("pk"))
    return queryset.annotate(is_favorited=Exists(fav_exists))


def home(request):
    return render(request, "scholarships/home.html")


def scholarship_list(request):
    scholarships = annotate_favorited(Scholarship.objects.all(), request.user)
    filter_form = ScholarshipFilterForm(request.GET or None)

    if filter_form.is_valid():
        scholarships = filter_scholarships(scholarships, filter_form.cleaned_data)

    paginator = Paginator(scholarships, SCHOLARSHIP_PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get("page"))

    # Preserve active filters across pagination links (drop the page param).
    filter_qs = request.GET.copy()
    filter_qs.pop("page", None)

    context = {
        "scholarships": page_obj,
        "filter_form": filter_form,
        "page_obj": page_obj,
        "paginator": paginator,
        "filter_querystring": filter_qs.urlencode(),
    }

    if request.headers.get("HX-Request"):
        return render(request, "scholarships/_scholarship_results.html", context)

    return render(request, "scholarships/scholarship_list.html", context)


def scholarship_detail(request, pk):
    scholarship = get_object_or_404(
        annotate_favorited(Scholarship.objects.all(), request.user), pk=pk
    )
    return render(
        request, "scholarships/scholarship_detail.html", {"scholarship": scholarship}
    )


@login_required
def request_form(request):
    if request.method == "POST":
        form = ScholarshipRequestForm(request.POST)
        if form.is_valid():
            request_obj = form.save(commit=False)
            request_obj.user = request.user
            request_obj.status = "pending"
            request_obj.save()
            messages.success(
                request,
                "Your suggestion to add a scholarship has been submitted and is "
                "pending admin review!",
            )
            return render(
                request,
                "scholarships/request_success.html",
                {"request_obj": request_obj},
            )
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
    user_requests = ScholarshipRequest.objects.filter(user=request.user).order_by(
        "-created_at"
    )
    return render(
        request, "scholarships/profile.html", {"user_requests": user_requests}
    )


@login_required
def toggle_favorite(request, pk):
    """Idempotently toggle the current user's favorite on a scholarship.

    HTMX requests receive the ``_favorite_button.html`` partial rendered with
    the new state; non-HTMX requests are redirected to the scholarship detail.
    """
    scholarship = get_object_or_404(Scholarship, pk=pk)

    if request.method == "POST":
        favorite = Favorite.objects.filter(
            user=request.user, scholarship=scholarship
        ).first()
        if favorite:
            favorite.delete()
        else:
            Favorite.objects.get_or_create(user=request.user, scholarship=scholarship)

    scholarship_qs = annotate_favorited(
        Scholarship.objects.filter(pk=scholarship.pk), request.user
    )
    scholarship = scholarship_qs.get()

    if request.headers.get("HX-Request"):
        return render(
            request, "scholarships/_favorite_button.html", {"scholarship": scholarship}
        )

    return redirect("scholarship-detail", pk=scholarship.pk)


@login_required
def favorite_list(request):
    favorites = (
        Favorite.objects.filter(user=request.user)
        .select_related("scholarship")
        .order_by("-created_at")
    )
    # Every scholarship shown here is favorited by this user by definition.
    for fav in favorites:
        fav.scholarship.is_favorited = True
    return render(request, "scholarships/favorites.html", {"favorites": favorites})


# Admin views
@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    pending_requests = ScholarshipRequest.objects.filter(status="pending").count()
    total_requests = ScholarshipRequest.objects.count()
    recent_requests = ScholarshipRequest.objects.order_by("-created_at")[:10]

    return render(
        request,
        "scholarships/admin_dashboard.html",
        {
            "pending_requests": pending_requests,
            "total_requests": total_requests,
            "recent_requests": recent_requests,
        },
    )


@user_passes_test(lambda u: u.is_superuser)
def admin_requests(request):
    status_filter = request.GET.get("status", "all")
    requests = ScholarshipRequest.objects.all()

    if status_filter != "all":
        requests = requests.filter(status=status_filter)

    requests = requests.order_by("-created_at")

    return render(
        request,
        "scholarships/admin_requests.html",
        {"requests": requests, "status_filter": status_filter},
    )


@user_passes_test(lambda u: u.is_superuser)
def admin_request_detail(request, pk):
    request_obj = get_object_or_404(ScholarshipRequest, pk=pk)

    if request.method == "POST":
        action = request.POST.get("action")
        admin_notes = request.POST.get("admin_notes", "")

        if action in ["approve", "reject"]:
            linked_existing = False
            with transaction.atomic():
                if action == "approve":
                    if request_obj.status != "approved":
                        scholarship, created = Scholarship.objects.get_or_create(
                            foundation_name=request_obj.provider,
                            scholarship_name=request_obj.scholarship_name,
                            defaults={
                                "section": "IV",
                                "contents": request_obj.award_amount,
                            },
                        )
                        request_obj.created_scholarship = scholarship
                        linked_existing = not created
                    request_obj.status = "approved"
                else:
                    request_obj.status = "rejected"

                request_obj.admin_notes = admin_notes
                request_obj.reviewed_by = request.user
                request_obj.reviewed_date = timezone.now()
                request_obj.save()

            if action == "approve" and linked_existing:
                messages.info(
                    request,
                    "An existing scholarship with this name and provider was "
                    "linked to the request.",
                )
            else:
                action_text = "approved" if action == "approve" else "rejected"
                messages.success(request, f"Request {action_text} successfully.")
            return redirect("admin-requests")

    return render(
        request, "scholarships/admin_request_detail.html", {"request_obj": request_obj}
    )


@user_passes_test(lambda u: u.is_superuser)
def reload_scholarships(request):
    """Admin endpoint to reload CSV data"""
    if request.method == "POST":
        try:
            call_command("import_scholarships", "--overwrite")
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
