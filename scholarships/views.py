from django.http import HttpResponse


def home(request):
    return HttpResponse("<h1>Welcome to ScholarshipFinder</h1>")


def scholarship_list(request):
    scholarships = [
        "1. Tokyo STEM Scholarship — $5,000",
        "2. Kyoto Arts Grant — $3,000",
        "3. Osaka Engineering Fund — $10,000",
    ]
    html = "<h1>Available Scholarships</h1><ul>"
    for s in scholarships:
        html += f"<li>{s}</li>"
    html += "</ul>"
    return HttpResponse(html)


def scholarship_detail(request, pk):
    return HttpResponse(
        f"<h1>Scholarship #{pk}</h1>"
        f"<p>Name: Placeholder Scholarship</p>"
        f"<p>Provider: Placeholder Provider</p>"
        f"<p>Award Amount: $5,000</p>"
        f"<p>Deadline: 2026-12-31</p>"
    )


def request_form(request):
    return HttpResponse(
        "<h1>Submit a Scholarship Request</h1>"
        "<p>Use this form to request a scholarship that is not yet listed.</p>"
        "<p><em>(Form coming soon)</em></p>"
    )


def user_detail(request, pk):
    return HttpResponse(
        f"<h1>User #{pk}</h1>"
        f"<p>Name: Placeholder User</p>"
        f"<p>Email: user{pk}@example.com</p>"
        f"<p>Education: Undergraduate</p>"
        f"<p>Discipline: Computer Science</p>"
        f"<p>Prefecture: Tokyo</p>"
    )

