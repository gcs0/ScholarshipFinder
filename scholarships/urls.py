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
    path("requests/new/", views.request_form, name="request-form"),
    path("users/new/", views.user_create, name="user-create"),
    path("users/<int:pk>/", views.user_detail, name="user-detail"),
]
