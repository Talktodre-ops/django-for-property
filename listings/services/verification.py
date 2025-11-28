"""Verification service for listing state transitions."""

from typing import Dict, List, Tuple

from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone

from listings.models import (
    AuditEntry,
    Listing,
    ListingStatus,
    VerificationRequest,
    VerificationRequestState,
)


class VerificationService:
    """Service for managing listing verification state transitions."""

    @staticmethod
    def submit_listing(listing: Listing, user: User) -> Tuple[bool, List[str]]:
        """
        Submit a listing for verification.

        Args:
            listing: The listing to submit
            user: The user submitting the listing

        Returns:
            Tuple of (success: bool, errors: List[str])
        """
        errors = []

        # Validate owner identity
        owner_profile = listing.owner_profile
        if owner_profile.identity_status != "approved":
            errors.append("Owner identity must be verified first")

        # Validate contact verification
        if not owner_profile.has_verified_contact:
            errors.append("At least one contact method (email or phone) must be verified")

        # Validate photos
        photo_count = listing.photos.count()
        if photo_count < 1:
            errors.append("At least one photo is required")
        elif not listing.photos.filter(is_primary=True).exists():
            errors.append("At least one primary photo is required")

        # Validate documents (at least one document uploaded)
        doc_count = listing.documents.count()
        if doc_count < 1:
            errors.append("At least one property document is required")

        if errors:
            return False, errors

        # Create verification request and update listing
        with transaction.atomic():
            verification_request = VerificationRequest.objects.create(
                listing=listing,
                requested_by=user,
                state=VerificationRequestState.PENDING,
            )

            # Determine listing status
            if owner_profile.identity_status == "approved" and doc_count >= 1:
                listing.status = ListingStatus.IN_REVIEW
            else:
                listing.status = ListingStatus.PENDING_DOCUMENTS

            listing.submitted_at = timezone.now()
            listing.visibility_state = "limited"
            listing.save()

            # Audit log
            AuditEntry.objects.create(
                subject_type="listing",
                subject_id=listing.id,
                actor=user,
                action="listing.submitted_for_review",
                payload={
                    "listing_id": listing.id,
                    "verification_request_id": verification_request.id,
                    "status": listing.status,
                },
            )

        return True, []

    @staticmethod
    def approve_listing(
        listing: Listing,
        reviewer: User,
        notes: str = "",
    ) -> None:
        """
        Approve a listing for publication.

        Args:
            listing: The listing to approve
            reviewer: The staff member approving
            notes: Optional notes about the approval
        """
        with transaction.atomic():
            listing.status = ListingStatus.VERIFIED
            listing.visibility_state = "public"
            listing.verified_at = timezone.now()
            listing.save()

            # Update verification request
            verification_request = listing.verification_requests.filter(
                state__in=["pending", "under_review"]
            ).first()
            if verification_request:
                verification_request.state = VerificationRequestState.APPROVED
                verification_request.reviewer = reviewer
                verification_request.decided_at = timezone.now()
                verification_request.notes = notes
                verification_request.save()

            # Audit log
            AuditEntry.objects.create(
                subject_type="listing",
                subject_id=listing.id,
                actor=reviewer,
                action="listing.approved",
                payload={
                    "listing_id": listing.id,
                    "notes": notes,
                },
            )

    @staticmethod
    def reject_listing(
        listing: Listing,
        reviewer: User,
        reason: str,
    ) -> None:
        """
        Reject a listing.

        Args:
            listing: The listing to reject
            reviewer: The staff member rejecting
            reason: Reason for rejection
        """
        with transaction.atomic():
            listing.status = ListingStatus.REJECTED
            listing.rejected_at = timezone.now()
            listing.rejection_reason = reason
            listing.save()

            # Update verification request
            verification_request = listing.verification_requests.filter(
                state__in=["pending", "under_review"]
            ).first()
            if verification_request:
                verification_request.state = VerificationRequestState.REJECTED
                verification_request.reviewer = reviewer
                verification_request.decided_at = timezone.now()
                verification_request.notes = reason
                verification_request.save()

            # Audit log
            AuditEntry.objects.create(
                subject_type="listing",
                subject_id=listing.id,
                actor=reviewer,
                action="listing.rejected",
                payload={
                    "listing_id": listing.id,
                    "reason": reason,
                },
            )

    @staticmethod
    def get_submission_prerequisites(listing: Listing) -> Dict:
        """
        Get checklist of prerequisites for submission.

        Args:
            listing: The listing to check

        Returns:
            Dictionary of prerequisite name -> completion status and issues
        """
        owner_profile = listing.owner_profile
        
        # Check individual owner verification requirements
        identity_verified = owner_profile.identity_status == "approved"
        contact_verified = owner_profile.has_verified_contact
        
        # Combined owner verification status
        owner_verified = identity_verified and contact_verified
        
        # List of owner verification issues
        owner_issues = []
        if not identity_verified:
            owner_issues.append("Identity not approved")
        if not contact_verified:
            owner_issues.append("Contact not verified")
        
        return {
            "owner_identity_verified": identity_verified,
            "contact_verified": contact_verified,
            "owner_verified": owner_verified,  # Combined status for template
            "owner_issues": owner_issues,  # List of missing requirements
            "has_photos": listing.photos.count() >= 1,
            "has_primary_photo": listing.photos.filter(is_primary=True).exists(),
            "has_documents": listing.documents.count() >= 1,
        }

