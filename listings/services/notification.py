"""Notification service for sending emails and messages."""

from typing import Optional

from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string

from listings.models import Listing, OwnerProfile


class NotificationService:
    """Service for sending notifications."""

    @staticmethod
    def send_verification_email(user_email: str, token: str) -> None:
        """
        Send email verification link.

        Args:
            user_email: User's email address
            token: Verification token
        """
        subject = "Verify your Heimly email address"
        verification_url = f"/account/verify-email/{token}/"
        message = f"Click this link to verify your email: {verification_url}"

        # In development, this prints to console
        send_mail(
            subject=subject,
            message=message,
            from_email="noreply@heimly.com",
            recipient_list=[user_email],
            fail_silently=False,
        )

    @staticmethod
    def notify_listing_submitted(listing: Listing) -> None:
        """
        Notify user that listing was submitted.

        Args:
            listing: The submitted listing
        """
        owner_email = listing.owner_profile.user.email
        if owner_email:
            subject = f"Listing Submitted: {listing.title}"
            message = (
                f"Your listing '{listing.title}' has been submitted for review. "
                f"We'll notify you once it's been reviewed."
            )

            send_mail(
                subject=subject,
                message=message,
                from_email="noreply@heimly.com",
                recipient_list=[owner_email],
                fail_silently=False,
            )

    @staticmethod
    def notify_listing_approved(listing: Listing) -> None:
        """
        Notify user that listing was approved.

        Args:
            listing: The approved listing
        """
        owner_email = listing.owner_profile.user.email
        if owner_email:
            subject = f"Listing Approved: {listing.title}"
            message = (
                f"Great news! Your listing '{listing.title}' has been approved "
                f"and is now live on Heimly."
            )

            send_mail(
                subject=subject,
                message=message,
                from_email="noreply@heimly.com",
                recipient_list=[owner_email],
                fail_silently=False,
            )

    @staticmethod
    def notify_listing_rejected(listing: Listing, reason: str) -> None:
        """
        Notify user that listing was rejected.

        Args:
            listing: The rejected listing
            reason: Reason for rejection
        """
        owner_email = listing.owner_profile.user.email
        if owner_email:
            subject = f"Listing Review: {listing.title}"
            message = (
                f"Your listing '{listing.title}' requires some changes.\n\n"
                f"Reason: {reason}\n\n"
                f"Please update your listing and resubmit."
            )

            send_mail(
                subject=subject,
                message=message,
                from_email="noreply@heimly.com",
                recipient_list=[owner_email],
                fail_silently=False,
            )

    @staticmethod
    def add_flash_message(request, level: str, message: str) -> None:
        """
        Add flash message to request.

        Args:
            request: Django request object
            level: Message level (success, error, warning, info)
            message: Message text
        """
        messages.add_message(request, getattr(messages, level.upper()), message)

