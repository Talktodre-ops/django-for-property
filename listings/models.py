"""Models for property listings and verification system."""

import os
import uuid
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import slugify


def listing_photo_upload_path(instance, filename):
    """Generate unique filename for listing photos."""
    ext = os.path.splitext(filename)[1].lower()
    # Create unique filename: listing_id + uuid + extension
    unique_filename = f"listing_{instance.listing.id}_{uuid.uuid4().hex[:12]}{ext}"
    return f"listing_photos/{unique_filename}"


def listing_document_upload_path(instance, filename):
    """Generate unique filename for listing documents."""
    ext = os.path.splitext(filename)[1].lower()
    # Create unique filename: listing_id + doc_type + uuid + extension
    unique_filename = f"listing_{instance.listing.id}_{instance.doc_type}_{uuid.uuid4().hex[:8]}{ext}"
    return f"listing_documents/{unique_filename}"


def owner_id_upload_path(instance, filename):
    """Generate unique filename for owner ID documents."""
    ext = os.path.splitext(filename)[1].lower()
    # Create unique filename: user_id + uuid + extension
    unique_filename = f"owner_{instance.user.id}_id_{uuid.uuid4().hex[:8]}{ext}"
    return f"owner_ids/{unique_filename}"


class IdentityStatus(models.TextChoices):
    """Identity verification status choices."""

    INCOMPLETE = "incomplete", "Incomplete"
    PENDING_REVIEW = "pending_review", "Pending Review"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"


class IDType(models.TextChoices):
    """Government ID type choices."""

    NIN = "nin", "NIN (National Identification Number)"
    PASSPORT = "passport", "International Passport"
    DRIVER_LICENSE = "driver_license", "Driver's License"


class PreferredContact(models.TextChoices):
    """Preferred contact method choices."""

    EMAIL = "email", "Email"
    PHONE = "phone", "Phone"
    WHATSAPP = "whatsapp", "WhatsApp"


class OwnerProfile(models.Model):
    """Owner profile with KYC information."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="owner_profile",
        db_index=True,
    )
    phone_number = models.CharField(max_length=20, blank=True)
    whatsapp_number = models.CharField(max_length=20, blank=True)
    preferred_contact = models.CharField(
        max_length=20,
        choices=PreferredContact.choices,
        default=PreferredContact.EMAIL,
    )

    # ID verification
    id_type = models.CharField(
        max_length=20,
        choices=IDType.choices,
        blank=True,
    )
    id_number = models.CharField(max_length=100, blank=True, db_index=True)
    id_document = models.FileField(
        upload_to=owner_id_upload_path,
        blank=True,
        max_length=255,
        help_text="Front photo of government ID",
    )
    id_expiry_date = models.DateField(null=True, blank=True)

    # Verification status
    email_verified_at = models.DateTimeField(null=True, blank=True)
    phone_verified_at = models.DateTimeField(null=True, blank=True)
    identity_status = models.CharField(
        max_length=20,
        choices=IdentityStatus.choices,
        default=IdentityStatus.INCOMPLETE,
        db_index=True,
    )
    identity_reviewer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_profiles",
        limit_choices_to={'is_staff': True},
    )
    identity_reviewed_at = models.DateTimeField(null=True, blank=True)
    identity_notes = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta options for OwnerProfile."""

        db_table = "owner_profiles"
        indexes = [
            models.Index(fields=["identity_status", "id_number"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["id_type", "id_number"],
                condition=models.Q(id_number__gt=""),
                name="unique_id_per_type",
            ),
        ]

    def __str__(self) -> str:
        """String representation of OwnerProfile."""
        return f"{self.user.get_full_name() or self.user.username} - {self.identity_status}"

    @property
    def has_verified_contact(self) -> bool:
        """Check if at least one contact method is verified."""
        return bool(self.email_verified_at or self.phone_verified_at)


class ListingStatus(models.TextChoices):
    """Listing status choices."""

    DRAFT = "draft", "Draft"
    PENDING_IDENTITY = "pending_identity", "Pending Identity Verification"
    PENDING_DOCUMENTS = "pending_documents", "Pending Documents"
    IN_REVIEW = "in_review", "In Review"
    VERIFIED = "verified", "Verified"
    REJECTED = "rejected", "Rejected"
    ARCHIVED = "archived", "Archived"


class VisibilityState(models.TextChoices):
    """Visibility state choices."""

    PRIVATE = "private", "Private"
    LIMITED = "limited", "Limited (Owner Only)"
    PUBLIC = "public", "Public"


class PropertyType(models.TextChoices):
    """Property type choices."""

    APARTMENT = "apartment", "Apartment"
    DUPLEX = "duplex", "Duplex"
    BUNGALOW = "bungalow", "Bungalow"
    TERRACE = "terrace", "Terrace"
    DETACHED = "detached", "Detached House"
    LAND = "land", "Land"
    COMMERCIAL = "commercial", "Commercial"
    OTHER = "other", "Other"


class ListingType(models.TextChoices):
    """Listing type choices."""

    RENT = "rent", "For Rent"
    SALE = "sale", "For Sale"
    SHORTLET = "shortlet", "Shortlet"


class Listing(models.Model):
    """Property listing model."""

    owner_profile = models.ForeignKey(
        OwnerProfile,
        on_delete=models.CASCADE,
        related_name="listings",
        db_index=True,
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, blank=True, unique=True)
    description = models.TextField()

    # Property details
    property_type = models.CharField(
        max_length=20,
        choices=PropertyType.choices,
    )
    listing_type = models.CharField(
        max_length=20,
        choices=ListingType.choices,
    )

    # Location
    address_line = models.CharField(max_length=300)
    city = models.CharField(max_length=100, db_index=True)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default="Nigeria")
    postal_code = models.CharField(max_length=20, blank=True)
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )

    # Specifications
    bedrooms = models.PositiveIntegerField(null=True, blank=True)
    bathrooms = models.PositiveIntegerField(null=True, blank=True)
    parking_spaces = models.PositiveIntegerField(default=0)
    land_size_sqm = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )
    building_size_sqm = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )
    amenities = models.JSONField(default=dict, blank=True)

    # Commercial details
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    currency = models.CharField(max_length=3, default="NGN")
    service_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )
    is_negotiable = models.BooleanField(default=False)

    # Workflow status
    status = models.CharField(
        max_length=20,
        choices=ListingStatus.choices,
        default=ListingStatus.DRAFT,
        db_index=True,
    )
    visibility_state = models.CharField(
        max_length=20,
        choices=VisibilityState.choices,
        default=VisibilityState.PRIVATE,
    )
    submitted_at = models.DateTimeField(null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    rejected_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    # Flags
    requires_site_visit = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    featured_until = models.DateTimeField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta options for Listing."""

        db_table = "listings"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["owner_profile", "status"]),
            models.Index(fields=["status", "city"]),
            models.Index(fields=["status", "property_type"]),
        ]

    def __str__(self) -> str:
        """String representation of Listing."""
        return f"{self.title} - {self.status}"

    def save(self, *args, **kwargs):
        """Override save to auto-generate slug."""
        if not self.slug:
            self.slug = slugify(self.title)
            # Ensure uniqueness
            original_slug = self.slug
            counter = 1
            while Listing.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)


class ListingPhoto(models.Model):
    """Photo for property listing."""

    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name="photos",
        db_index=True,
    )
    image = models.ImageField(upload_to=listing_photo_upload_path, max_length=255)
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    position = models.PositiveIntegerField(default=0)
    metadata = models.JSONField(default=dict, blank=True)
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta options for ListingPhoto."""

        db_table = "listing_photos"
        ordering = ["is_primary", "position", "uploaded_at"]
        indexes = [
            models.Index(fields=["listing", "is_primary"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["listing"],
                condition=models.Q(is_primary=True),
                name="unique_primary_photo_per_listing",
            ),
        ]

    def __str__(self) -> str:
        """String representation of ListingPhoto."""
        primary_tag = " (Primary)" if self.is_primary else ""
        return f"{self.listing.title} - Photo{primary_tag}"


class DocumentType(models.TextChoices):
    """Document type choices for property verification."""

    C_OF_O = "c_of_o", "Certificate of Occupancy"
    DEED = "deed", "Deed of Assignment"
    UTILITY_BILL = "utility_bill", "Utility Bill"
    TAX_RECEIPT = "tax_receipt", "Tax Receipt"
    HOA_LETTER = "hoa_letter", "HOA/Estates Letter"
    OTHER = "other", "Other"


class DocumentStatus(models.TextChoices):
    """Document review status choices."""

    UPLOADED = "uploaded", "Uploaded"
    APPROVED = "approved", "Approved"
    NEEDS_RESUBMISSION = "needs_resubmission", "Needs Resubmission"


class ListingDocument(models.Model):
    """Document for property verification."""

    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name="documents",
        db_index=True,
    )
    doc_type = models.CharField(
        max_length=20,
        choices=DocumentType.choices,
        db_index=True,
    )
    file = models.FileField(upload_to=listing_document_upload_path, max_length=255)
    status = models.CharField(
        max_length=20,
        choices=DocumentStatus.choices,
        default=DocumentStatus.UPLOADED,
    )
    reviewer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_documents",
        limit_choices_to={'is_staff': True},
    )
    reviewer_comment = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        """Meta options for ListingDocument."""

        db_table = "listing_documents"
        ordering = ["-uploaded_at"]
        indexes = [
            models.Index(fields=["listing", "doc_type"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        """String representation of ListingDocument."""
        return f"{self.listing.title} - {self.get_doc_type_display()} ({self.status})"


class VerificationRequestState(models.TextChoices):
    """Verification request state choices."""

    PENDING = "pending", "Pending"
    UNDER_REVIEW = "under_review", "Under Review"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    CANCELLED = "cancelled", "Cancelled"


class VerificationRequest(models.Model):
    """Verification request tracking each submission cycle."""

    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name="verification_requests",
        db_index=True,
    )
    requested_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="verification_requests",
    )
    state = models.CharField(
        max_length=20,
        choices=VerificationRequestState.choices,
        default=VerificationRequestState.PENDING,
        db_index=True,
    )
    notes = models.TextField(blank=True)
    reviewer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_requests",
        limit_choices_to={'is_staff': True},
    )
    started_at = models.DateTimeField(auto_now_add=True)
    decided_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        """Meta options for VerificationRequest."""

        db_table = "verification_requests"
        ordering = ["-started_at"]
        indexes = [
            models.Index(fields=["state", "started_at"]),
        ]

    def __str__(self) -> str:
        """String representation of VerificationRequest."""
        return f"{self.listing.title} - {self.state}"


class AuditEntry(models.Model):
    """Audit log for traceability and analytics."""

    # Polymorphic subject reference
    subject_type = models.CharField(max_length=50, db_index=True)
    subject_id = models.PositiveIntegerField(db_index=True)
    actor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="audit_actions",
    )
    action = models.CharField(max_length=100, db_index=True)
    payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        """Meta options for AuditEntry."""

        db_table = "audit_entries"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["subject_type", "subject_id"]),
            models.Index(fields=["action", "created_at"]),
        ]

    def __str__(self) -> str:
        """String representation of AuditEntry."""
        return f"{self.action} on {self.subject_type}#{self.subject_id} by {self.actor or 'System'}"

