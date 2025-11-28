"""URL configuration for listings app."""

from django.urls import path

from listings import views

app_name = "listings"

urlpatterns = [
    path("", views.dashboard_view, name="dashboard"),
    path("home/", views.dashboard_view, name="home"),
    path("profile/", views.OwnerProfileUpdateView.as_view(), name="profile"),
    path("listings/new/", views.ListingCreateView.as_view(), name="listing_create"),
    path("listings/<int:pk>/", views.ListingDetailView.as_view(), name="listing_detail"),
    path("listings/<int:pk>/edit/", views.ListingUpdateView.as_view(), name="listing_edit"),
    path(
        "listings/<int:pk>/photos/",
        views.listing_photo_upload,
        name="listing_photos",
    ),
    path(
        "listings/<int:pk>/documents/",
        views.listing_document_upload,
        name="listing_documents",
    ),
    path(
        "listings/<int:pk>/submit/",
        views.submit_for_review,
        name="listing_submit",
    ),
    path(
        "listings/<int:pk>/preview/",
        views.listing_preview,
        name="listing_preview",
    ),
    # Email verification
    path(
        "verify-email/",
        views.request_email_verification,
        name="request_email_verification",
    ),
    path(
        "verify-email/<str:token>/",
        views.confirm_email_verification,
        name="confirm_email_verification",
    ),
    # Staff review queue
    path(
        "staff/reviews/",
        views.ReviewQueueListView.as_view(),
        name="review_queue",
    ),
    path(
        "staff/reviews/<int:pk>/",
        views.ReviewDetailView.as_view(),
        name="review_detail",
    ),
    path(
        "staff/reviews/<int:pk>/approve/",
        views.approve_listing_review,
        name="review_approve",
    ),
    path(
        "staff/reviews/<int:pk>/reject/",
        views.reject_listing_review,
        name="review_reject",
    ),
    # Document moderation (AJAX)
    path(
        "staff/documents/<int:document_id>/moderate/",
        views.document_moderation_view,
        name="document_moderate",
    ),
]

