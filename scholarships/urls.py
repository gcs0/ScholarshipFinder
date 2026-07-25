from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("scholarships/", views.scholarship_list, name="scholarship-list"),
    path(
        "scholarships/<int:pk>/",
        views.scholarship_detail,
        name="scholarship-detail",
    ),
    path(
        "scholarships/<int:scholarship_id>/request/",
        views.request_form,
        name="request-form",
    ),
    path("register/", views.register, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("profile/", views.profile, name="profile"),
    path("admin/", views.admin_dashboard, name="admin-dashboard"),
    path("admin/requests/", views.admin_requests, name="admin-requests"),
    path(
        "admin/requests/<int:pk>/",
        views.admin_request_detail,
        name="admin-request-detail",
    ),
    path("admin/reload/", views.reload_scholarships, name="reload-scholarships"),
    path(
        "password-change/",
        views.CustomPasswordChangeView.as_view(),
        name="password-change",
    ),
    path(
        "password-change/done/",
        views.CustomPasswordChangeDoneView.as_view(),
        name="password-change-done",
    ),
]
