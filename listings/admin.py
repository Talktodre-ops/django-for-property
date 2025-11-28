"""Django admin configuration for listings app."""

from django.contrib import admin
from django.utils.html import format_html

from listings.models import (
    AuditEntry,
    Listing,
    ListingDocument,
    ListingPhoto,
    OwnerProfile,
    VerificationRequest,
)


@admin.register(OwnerProfile)
class OwnerProfileAdmin(admin.ModelAdmin):
    """Admin interface for OwnerProfile."""

    list_display = [
        "user",
        "identity_status",
        "id_type",
        "id_number",
        "has_id_document_display",
        "has_verified_contact_display",
        "created_at",
    ]
    list_filter = ["identity_status", "id_type", "created_at"]
    search_fields = ["user__username", "user__email", "id_number", "phone_number"]
    readonly_fields = [
        "created_at",
        "updated_at",
        "email_verified_at",
        "phone_verified_at",
    ]
    fieldsets = (
        ("User Information", {"fields": ("user",)}),
        (
            "Contact Information",
            {
                "fields": (
                    "phone_number",
                    "whatsapp_number",
                    "preferred_contact",
                    "email_verified_at",
                    "phone_verified_at",
                )
            },
        ),
        (
            "Identity Verification",
            {
                "fields": (
                    "id_type",
                    "id_number",
                    "id_document",
                    "id_expiry_date",
                    "identity_status",
                    "identity_reviewer",
                    "identity_reviewed_at",
                    "identity_notes",
                )
            },
        ),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    actions = ["approve_profiles", "reject_profiles", "verify_email", "verify_phone"]

    def has_verified_contact_display(self, obj):
        """Display verified contact status."""
        return "Yes" if obj.has_verified_contact else "No"

    has_verified_contact_display.short_description = "Contact Verified"

    def has_id_document_display(self, obj):
        """Display ID document upload status with link."""
        if obj.id_document:
            return format_html(
                '<a href="{}" target="_blank" style="color: green;">✓ Uploaded</a>',
                obj.id_document.url,
            )
        return format_html('<span style="color: red;">✗ Missing</span>')

    has_id_document_display.short_description = "ID Document"

    def approve_profiles(self, request, queryset):
        """Admin action to approve owner profiles."""
        from django.utils import timezone

        count = 0
        for profile in queryset:
            if profile.identity_status != "approved":
                profile.identity_status = "approved"
                profile.identity_reviewer = request.user
                profile.identity_reviewed_at = timezone.now()
                profile.save()

                # Audit log
                AuditEntry.objects.create(
                    subject_type="owner_profile",
                    subject_id=profile.id,
                    actor=request.user,
                    action="owner_profile.approved",
                    payload={
                        "user_id": profile.user.id,
                        "id_type": profile.id_type,
                    },
                )
                count += 1

        self.message_user(
            request,
            f"{count} profile(s) approved successfully. Owners can now submit listings.",
        )

    approve_profiles.short_description = "Approve selected profiles"

    def reject_profiles(self, request, queryset):
        """Admin action to reject owner profiles."""
        from django.utils import timezone

        count = 0
        for profile in queryset:
            if profile.identity_status != "rejected":
                profile.identity_status = "rejected"
                profile.identity_reviewer = request.user
                profile.identity_reviewed_at = timezone.now()
                profile.save()

                # Audit log
                AuditEntry.objects.create(
                    subject_type="owner_profile",
                    subject_id=profile.id,
                    actor=request.user,
                    action="owner_profile.rejected",
                    payload={
                        "user_id": profile.user.id,
                    },
                )
                count += 1

        self.message_user(request, f"{count} profile(s) rejected.")

    reject_profiles.short_description = "Reject selected profiles"

    def verify_email(self, request, queryset):
        """Admin action to manually verify email."""
        from django.utils import timezone

        count = 0
        for profile in queryset:
            if not profile.email_verified_at:
                profile.email_verified_at = timezone.now()
                profile.save()

                # Audit log
                AuditEntry.objects.create(
                    subject_type="owner_profile",
                    subject_id=profile.id,
                    actor=request.user,
                    action="email.verified_by_admin",
                    payload={
                        "user_id": profile.user.id,
                        "email": profile.user.email,
                    },
                )
                count += 1

        self.message_user(
            request,
            f"{count} email(s) verified successfully.",
        )

    verify_email.short_description = "Manually verify email"

    def verify_phone(self, request, queryset):
        """Admin action to manually verify phone."""
        from django.utils import timezone

        count = 0
        for profile in queryset:
            if not profile.phone_verified_at and profile.phone_number:
                profile.phone_verified_at = timezone.now()
                profile.save()

                # Audit log
                AuditEntry.objects.create(
                    subject_type="owner_profile",
                    subject_id=profile.id,
                    actor=request.user,
                    action="phone.verified_by_admin",
                    payload={
                        "user_id": profile.user.id,
                        "phone": profile.phone_number,
                    },
                )
                count += 1

        self.message_user(
            request,
            f"{count} phone number(s) verified successfully.",
        )

    verify_phone.short_description = "Manually verify phone"


class ListingPhotoInline(admin.TabularInline):
    """Inline admin for listing photos."""

    model = ListingPhoto
    extra = 0
    readonly_fields = ["uploaded_at", "image_preview"]
    fields = ["image_preview", "image", "caption", "is_primary", "position", "uploaded_at"]

    def image_preview(self, obj):
        """Display image thumbnail preview."""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 150px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" />',
                obj.image.url
            )
        return "No image"

    image_preview.short_description = "Preview"


class ListingDocumentInline(admin.TabularInline):
    """Inline admin for listing documents."""

    model = ListingDocument
    extra = 0
    readonly_fields = ["uploaded_at", "reviewed_at", "file_link"]
    fields = ["doc_type", "file_link", "file", "status", "reviewer", "reviewer_comment", "uploaded_at", "reviewed_at"]

    def file_link(self, obj):
        """Display clickable link to view/download the document."""
        if obj.file:
            file_name = obj.file.name.split('/')[-1]  # Get just the filename
            return format_html(
                '<a href="{}" target="_blank" style="color: #4F46E5; font-weight: 600; text-decoration: none; padding: 6px 12px; background: #EEF2FF; border-radius: 6px; display: inline-block;">'
                '<i class="fas fa-file-download"></i> View {}</a>',
                obj.file.url,
                obj.get_doc_type_display()
            )
        return "No file"

    file_link.short_description = "Document"


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    """Admin interface for Listing."""

    list_display = [
        "title",
        "owner_profile",
        "status",
        "city",
        "price",
        "property_type",
        "photo_count",
        "doc_count",
        "created_at",
    ]
    list_filter = [
        "status",
        "property_type",
        "listing_type",
        "city",
        "requires_site_visit",
        "is_featured",
        "created_at",
    ]
    search_fields = ["title", "description", "address_line", "city", "state"]
    readonly_fields = ["created_at", "updated_at", "submitted_at", "verified_at", "rejected_at"]
    inlines = [ListingPhotoInline, ListingDocumentInline]
    fieldsets = (
        ("Basic Information", {"fields": ("owner_profile", "title", "slug", "description")}),
        ("Property Details", {"fields": ("property_type", "listing_type", "bedrooms", "bathrooms", "parking_spaces", "land_size_sqm", "building_size_sqm", "amenities")}),
        ("Location", {"fields": ("address_line", "city", "state", "country", "postal_code", "latitude", "longitude")}),
        ("Commercial", {"fields": ("price", "currency", "service_charge", "is_negotiable")}),
        ("Status", {"fields": ("status", "visibility_state", "requires_site_visit", "is_featured", "featured_until")}),
        ("Timestamps", {"fields": ("created_at", "updated_at", "submitted_at", "verified_at", "rejected_at")}),
        ("Rejection", {"fields": ("rejection_reason",)}),
    )

    def photo_count(self, obj):
        """Display count of photos."""
        count = obj.photos.count()
        if count == 0:
            return format_html('<span style="color: #DC2626;">0 photos</span>')
        elif count < 3:
            return format_html('<span style="color: #F59E0B;">{} photos</span>', count)
        else:
            return format_html('<span style="color: #059669;">{} photos</span>', count)

    photo_count.short_description = "Photos"

    def doc_count(self, obj):
        """Display count of documents."""
        count = obj.documents.count()
        approved = obj.documents.filter(status='approved').count()
        if count == 0:
            return format_html('<span style="color: #DC2626;">0 docs</span>')
        else:
            return format_html(
                '<span style="color: #059669;">{}/{} approved</span>',
                approved, count
            )

    doc_count.short_description = "Documents"

    actions = ["approve_listings", "reject_listings"]

    def approve_listings(self, request, queryset):
        """Admin action to approve listings."""
        from listings.services import NotificationService, VerificationService

        count = 0
        for listing in queryset:
            if listing.status == "in_review":
                VerificationService.approve_listing(listing, request.user, "Approved via admin")
                NotificationService.notify_listing_approved(listing)
                count += 1
        self.message_user(request, f"{count} listing(s) approved.")

    approve_listings.short_description = "Approve selected listings"

    def reject_listings(self, request, queryset):
        """Admin action to reject listings."""
        from listings.services import VerificationService

        count = 0
        for listing in queryset:
            if listing.status in ["in_review", "pending_documents"]:
                VerificationService.reject_listing(
                    listing, request.user, "Rejected via admin action"
                )
                count += 1
        self.message_user(request, f"{count} listing(s) rejected.")

    reject_listings.short_description = "Reject selected listings"


@admin.register(ListingDocument)
class ListingDocumentAdmin(admin.ModelAdmin):
    """Admin interface for ListingDocument."""

    list_display = [
        "listing",
        "doc_type",
        "file_preview",
        "status",
        "reviewer",
        "uploaded_at",
        "reviewed_at",
    ]
    list_filter = ["status", "doc_type", "uploaded_at"]
    search_fields = ["listing__title", "reviewer_comment"]
    readonly_fields = ["uploaded_at", "reviewed_at", "file_preview_large"]
    fieldsets = (
        ("Document Information", {
            "fields": ("listing", "doc_type", "file", "file_preview_large")
        }),
        ("Review Status", {
            "fields": ("status", "reviewer", "reviewer_comment", "reviewed_at")
        }),
        ("Timestamps", {
            "fields": ("uploaded_at",)
        }),
    )
    actions = ["approve_documents", "reject_documents"]

    def file_preview(self, obj):
        """Display file link in list view."""
        if obj.file:
            return format_html(
                '<a href="{}" target="_blank" style="color: #059669; font-weight: 600; text-decoration: none;">'
                '<i class="fas fa-file-pdf"></i> View</a>',
                obj.file.url
            )
        return "-"

    file_preview.short_description = "File"

    def file_preview_large(self, obj):
        """Display large file preview in detail view."""
        if obj.file:
            file_ext = obj.file.name.lower().split('.')[-1]
            if file_ext in ['jpg', 'jpeg', 'png']:
                # Show image preview
                return format_html(
                    '<div style="margin: 20px 0;">'
                    '<img src="{}" style="max-width: 600px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);" />'
                    '<p style="margin-top: 10px;"><a href="{}" target="_blank" class="button">Open Full Size</a></p>'
                    '</div>',
                    obj.file.url,
                    obj.file.url
                )
            else:
                # Show PDF link
                return format_html(
                    '<div style="margin: 20px 0;">'
                    '<a href="{}" target="_blank" class="button" style="background: #059669; color: white; padding: 12px 24px; border-radius: 6px; text-decoration: none; display: inline-block;">'
                    '<i class="fas fa-file-pdf"></i> Open PDF Document</a>'
                    '<p style="margin-top: 10px; color: #666;">Filename: {}</p>'
                    '</div>',
                    obj.file.url,
                    obj.file.name.split('/')[-1]
                )
        return "No file uploaded"

    file_preview_large.short_description = "Document Preview"

    def approve_documents(self, request, queryset):
        """Admin action to approve documents."""
        from django.utils import timezone

        count = queryset.update(
            status="approved",
            reviewer=request.user,
            reviewed_at=timezone.now(),
        )
        self.message_user(request, f"{count} document(s) approved.")

    approve_documents.short_description = "Approve selected documents"

    def reject_documents(self, request, queryset):
        """Admin action to reject documents."""
        from django.utils import timezone

        count = queryset.update(
            status="needs_resubmission",
            reviewer=request.user,
            reviewed_at=timezone.now(),
        )
        self.message_user(request, f"{count} document(s) marked for resubmission.")

    reject_documents.short_description = "Reject selected documents (needs resubmission)"


@admin.register(VerificationRequest)
class VerificationRequestAdmin(admin.ModelAdmin):
    """Admin interface for VerificationRequest."""

    list_display = ["listing", "state", "requested_by", "reviewer", "started_at", "decided_at"]
    list_filter = ["state", "started_at"]
    search_fields = ["listing__title", "notes"]
    readonly_fields = ["started_at"]

    def save_model(self, request, obj, form, change):
        """Update listing status when verification request state changes."""
        from listings.services import VerificationService, NotificationService

        # Check if state changed to approved
        if change and 'state' in form.changed_data:
            if obj.state == 'approved':
                # Use the service to properly approve the listing
                VerificationService.approve_listing(
                    listing=obj.listing,
                    reviewer=request.user,
                    notes=obj.notes or "Approved via admin"
                )
                NotificationService.notify_listing_approved(obj.listing)
                self.message_user(request, f"Listing '{obj.listing.title}' approved and set to verified status!")
                return  # Service already saved everything
            elif obj.state == 'rejected':
                # Use the service to reject the listing
                VerificationService.reject_listing(
                    listing=obj.listing,
                    reviewer=request.user,
                    reason=obj.notes or "Rejected via admin"
                )
                self.message_user(request, f"Listing '{obj.listing.title}' rejected!")
                return  # Service already saved everything

        # Default save
        super().save_model(request, obj, form, change)


@admin.register(AuditEntry)
class AuditEntryAdmin(admin.ModelAdmin):
    """Admin interface for AuditEntry."""

    list_display = ["action", "subject_type", "subject_id", "actor", "created_at"]
    list_filter = ["action", "subject_type", "created_at"]
    search_fields = ["action", "payload"]
    readonly_fields = ["created_at"]
    date_hierarchy = "created_at"
