"""Views for listings app."""

import random
import secrets
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.cache import cache
from django.db.models import Prefetch, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from listings.forms import (
    ListingDocumentForm,
    ListingForm,
    ListingPhotoForm,
    OwnerProfileForm,
    SignupForm,
)
from listings.models import AuditEntry, Listing, ListingDocument, OwnerProfile
from listings.services import NotificationService, VerificationService


class SignupView(CreateView):
    """User registration view."""

    form_class = SignupForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("listings:dashboard")

    def form_valid(self, form):
        """Auto-login after signup."""
        response = super().form_valid(form)
        login(self.request, self.object)
        # Create owner profile
        OwnerProfile.objects.get_or_create(user=self.object)
        return response


@login_required
def dashboard_view(request):
    """
    Dashboard view showing user's listings and profile status.

    Optimized with prefetch_related to avoid N+1 queries.
    """
    owner_profile, _ = OwnerProfile.objects.get_or_create(user=request.user)

    # Fetch listings with related data in minimal queries
    listings = (
        Listing.objects.filter(owner_profile=owner_profile)
        .select_related("owner_profile")
        .prefetch_related("photos", "documents")
        .order_by("-created_at")
    )

    # Group by status
    listings_by_status = {
        "draft": listings.filter(status="draft"),
        "pending": listings.filter(status__in=["pending_identity", "pending_documents", "in_review"]),
        "verified": listings.filter(status="verified"),
        "rejected": listings.filter(status="rejected"),
        "archived": listings.filter(status="archived"),
    }

    # Get prerequisites for submission
    incomplete_listings = listings.filter(status="draft")
    prerequisites = {}
    for listing in incomplete_listings[:5]:  # Limit to 5 to avoid too many queries
        prerequisites[listing.id] = VerificationService.get_submission_prerequisites(listing)

    context = {
        "owner_profile": owner_profile,
        "listings": listings,  # All listings
        "listings_by_status": listings_by_status,
        "prerequisites": prerequisites,
    }
    return render(request, "listings/dashboard.html", context)


class OwnerProfileUpdateView(LoginRequiredMixin, UpdateView):
    """View for updating owner profile and KYC information."""

    model = OwnerProfile
    form_class = OwnerProfileForm
    template_name = "listings/owner_profile_form.html"

    def get_object(self):
        """Get or create owner profile for current user."""
        owner_profile, _ = OwnerProfile.objects.get_or_create(user=self.request.user)
        return owner_profile
    
    def get_context_data(self, **kwargs):
        """Add owner_profile to context for template."""
        context = super().get_context_data(**kwargs)
        context['owner_profile'] = self.get_object()
        return context

    def get_success_url(self):
        """Redirect back to the profile page after update."""
        return reverse_lazy("listings:profile")

    def form_valid(self, form):
        """Set status to pending_review when ID information is provided."""
        profile = form.instance

        # Check if a file was uploaded in this request
        file_uploaded = 'id_document' in self.request.FILES

        # Save first to get the uploaded file
        response = super().form_valid(form)

        # Refresh from database to get the saved file
        profile.refresh_from_db()

        # Debug logging
        if file_uploaded:
            if profile.id_document:
                messages.info(self.request, f"File uploaded successfully: {profile.id_document.name}")
            else:
                messages.error(self.request, "File upload failed - please try again with a smaller file.")

        # Only set to pending_review if user has provided all ID information
        if profile.id_type and profile.id_number and profile.id_document:
            profile.identity_status = "pending_review"
            profile.save()
            messages.success(self.request, "Profile submitted for review! Your identity will be reviewed soon.")
        else:
            # Keep as incomplete if ID info not fully provided
            if profile.identity_status == "pending_review":
                profile.identity_status = "incomplete"
                profile.save()

            missing = []
            if not profile.id_type:
                missing.append("ID type")
            if not profile.id_number:
                missing.append("ID number")
            if not profile.id_document:
                missing.append("ID document file")

            messages.warning(
                self.request,
                f"Profile saved! Still need: {', '.join(missing)} to submit for verification."
            )

        return response

    def form_invalid(self, form):
        """Handle form validation errors."""
        messages.error(
            self.request,
            "Please correct the errors below before submitting."
        )
        return super().form_invalid(form)


class ListingCreateView(LoginRequiredMixin, CreateView):
    """View for creating new property listing."""

    model = Listing
    form_class = ListingForm
    template_name = "listings/listing_form.html"
    success_url = reverse_lazy("listings:dashboard")

    def form_valid(self, form):
        """Set owner_profile and status."""
        owner_profile, _ = OwnerProfile.objects.get_or_create(user=self.request.user)
        form.instance.owner_profile = owner_profile
        form.instance.status = "draft"
        messages.success(self.request, "Listing created! Add photos and documents to continue.")
        return super().form_valid(form)


class ListingUpdateView(LoginRequiredMixin, UpdateView):
    """View for updating property listing."""

    model = Listing
    form_class = ListingForm
    template_name = "listings/listing_form.html"

    def get_queryset(self):
        """Only show listings owned by current user."""
        owner_profile, _ = OwnerProfile.objects.get_or_create(user=self.request.user)
        return Listing.objects.filter(owner_profile=owner_profile)

    def get_success_url(self):
        """Redirect to listing detail."""
        return reverse("listings:listing_detail", kwargs={"pk": self.object.pk})


class ListingDetailView(LoginRequiredMixin, DetailView):
    """View for viewing listing details."""

    model = Listing
    template_name = "listings/listing_detail.html"

    def get_queryset(self):
        """Only show listings owned by current user."""
        owner_profile, _ = OwnerProfile.objects.get_or_create(user=self.request.user)
        return Listing.objects.filter(owner_profile=owner_profile).prefetch_related(
            "photos", "documents"
        )


@login_required
def listing_photo_upload(request, pk):
    """Handle photo uploads for listing - supports multiple files."""
    listing = get_object_or_404(
        Listing.objects.filter(owner_profile__user=request.user), pk=pk
    )

    if request.method == "POST":
        # Check if multiple files were uploaded
        files = request.FILES.getlist('image')

        if not files:
            messages.error(request, "Please select at least one photo to upload.")
            return redirect("listings:listing_photos", pk=listing.pk)

        uploaded_count = 0
        errors = []

        for file in files:
            # Create a form for each file
            form = ListingPhotoForm({'caption': '', 'is_primary': False}, {'image': file})

            if form.is_valid():
                photo = form.save(commit=False)
                photo.listing = listing
                photo.uploaded_by = request.user
                photo.save()
                uploaded_count += 1
            else:
                # Collect errors
                for field_errors in form.errors.values():
                    errors.extend(field_errors)

        # Set first photo as primary if no primary exists
        if not listing.photos.filter(is_primary=True).exists():
            first_photo = listing.photos.first()
            if first_photo:
                first_photo.is_primary = True
                first_photo.save()

        if uploaded_count > 0:
            messages.success(request, f"{uploaded_count} photo(s) uploaded successfully!")

        if errors:
            for error in errors:
                messages.error(request, error)

        return redirect("listings:listing_detail", pk=listing.pk)
    else:
        form = ListingPhotoForm()

    context = {"listing": listing, "form": form, "photos": listing.photos.all()}
    return render(request, "listings/listing_photos.html", context)


@login_required
def listing_document_upload(request, pk):
    """Handle document uploads for listing."""
    listing = get_object_or_404(
        Listing.objects.filter(owner_profile__user=request.user), pk=pk
    )

    if request.method == "POST":
        form = ListingDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.listing = listing
            document.save()
            messages.success(request, "Document uploaded successfully!")
            return redirect("listings:listing_detail", pk=listing.pk)
    else:
        form = ListingDocumentForm()

    context = {
        "listing": listing,
        "form": form,
        "documents": listing.documents.all(),
    }
    return render(request, "listings/listing_documents.html", context)


@login_required
def submit_for_review(request, pk):
    """Submit listing for verification."""
    listing = get_object_or_404(
        Listing.objects.filter(owner_profile__user=request.user), pk=pk
    )

    success, errors = VerificationService.submit_listing(listing, request.user)

    if success:
        NotificationService.notify_listing_submitted(listing)
        messages.success(
            request,
            "Listing submitted for review! We'll notify you once it's been reviewed.",
        )
        return redirect("listings:dashboard")
    else:
        for error in errors:
            messages.error(request, error)
        return redirect("listings:listing_detail", pk=listing.pk)


@login_required
def listing_preview(request, pk):
    """Preview listing (read-only view for owners)."""
    listing = get_object_or_404(
        Listing.objects.filter(owner_profile__user=request.user), pk=pk
    )
    listing = Listing.objects.filter(pk=listing.pk).prefetch_related(
        "photos", "documents"
    ).first()

    prerequisites = VerificationService.get_submission_prerequisites(listing)

    context = {
        "listing": listing,
        "prerequisites": prerequisites,
    }
    return render(request, "listings/listing_preview.html", context)


@login_required
def request_email_verification(request):
    """Send email verification link to user."""
    owner_profile, _ = OwnerProfile.objects.get_or_create(user=request.user)

    # Check if already verified
    if owner_profile.email_verified_at:
        messages.info(request, "Your email is already verified!")
        return redirect("listings:profile")

    # Check if user has an email
    if not request.user.email:
        messages.error(request, "No email address found. Please contact support.")
        return redirect("listings:profile")

    # Generate verification token (valid for 24 hours)
    token = secrets.token_urlsafe(32)
    cache_key = f"email_verify_{token}"
    cache.set(cache_key, request.user.id, timeout=86400)  # 24 hours

    # Build verification URL
    verification_url = request.build_absolute_uri(
        reverse("listings:confirm_email_verification", kwargs={"token": token})
    )

    # In development, just show the link in console
    # In production, send actual email
    print("\n" + "="*80)
    print("EMAIL VERIFICATION LINK")
    print("="*80)
    print(f"To: {request.user.email}")
    print(f"User: {request.user.username}")
    print(f"\nClick this link to verify your email:")
    print(f"{verification_url}")
    print("="*80 + "\n")

    # Log the action
    AuditEntry.objects.create(
        subject_type="owner_profile",
        subject_id=owner_profile.id,
        actor=request.user,
        action="email.verification_requested",
        payload={"email": request.user.email},
    )

    messages.success(
        request,
        f"Verification email sent to {request.user.email}! "
        "Check your inbox and click the verification link. (In development mode, check your console)"
    )
    return redirect("listings:profile")


@login_required
def confirm_email_verification(request, token):
    """Confirm email verification via token."""
    cache_key = f"email_verify_{token}"
    user_id = cache.get(cache_key)

    if not user_id:
        messages.error(
            request,
            "Invalid or expired verification link. Please request a new one."
        )
        return redirect("listings:profile")

    # Check if token belongs to current user
    if user_id != request.user.id:
        messages.error(request, "This verification link is not for your account.")
        return redirect("listings:profile")

    # Mark email as verified
    owner_profile, _ = OwnerProfile.objects.get_or_create(user=request.user)

    if owner_profile.email_verified_at:
        messages.info(request, "Your email was already verified!")
    else:
        owner_profile.email_verified_at = timezone.now()
        owner_profile.save()

        # Log the action
        AuditEntry.objects.create(
            subject_type="owner_profile",
            subject_id=owner_profile.id,
            actor=request.user,
            action="email.verified",
            payload={"email": request.user.email},
        )

        messages.success(request, "Email verified successfully! ✓")

    # Delete the token so it can't be reused
    cache.delete(cache_key)

    return redirect("listings:profile")


@login_required
def request_phone_otp(request):
    """Generate and display OTP for phone verification (console-based for MVP)."""
    owner_profile, _ = OwnerProfile.objects.get_or_create(user=request.user)
    
    # Check if already verified
    if owner_profile.phone_verified_at:
        messages.info(request, "Your phone number is already verified!")
        return redirect("listings:profile")
    
    # Check if user has a phone number
    if not owner_profile.phone_number:
        messages.error(request, "Please add your phone number before requesting verification.")
        return redirect("listings:profile")
    
    # Generate 6-digit OTP
    otp_code = str(random.randint(100000, 999999))
    
    # Store OTP in cache (valid for 10 minutes)
    cache_key = f"phone_otp_{request.user.id}"
    cache.set(cache_key, {
        "otp": otp_code,
        "phone": owner_profile.phone_number,
        "user_id": request.user.id,
    }, timeout=600)  # 10 minutes
    
    # Log OTP to console (instead of sending SMS)
    print("\n" + "="*80)
    print("PHONE VERIFICATION OTP")
    print("="*80)
    print(f"To: {owner_profile.phone_number}")
    print(f"User: {request.user.username}")
    print(f"\nYour verification code is: {otp_code}")
    print("\n(For demo purposes - check server console. In production, this would be sent via SMS)")
    print("="*80 + "\n")
    
    # Log the action
    AuditEntry.objects.create(
        subject_type="owner_profile",
        subject_id=owner_profile.id,
        actor=request.user,
        action="phone.otp_requested",
        payload={
            "phone": owner_profile.phone_number,
            "note": "OTP logged to console for MVP demo",
        },
    )
    
    messages.success(
        request,
        f"Verification code sent! Check the server console for your OTP code. "
        f"(Code valid for 10 minutes)"
    )
    
    # Redirect to OTP verification page
    return redirect("listings:verify_phone_otp")


@login_required
def verify_phone_otp(request):
    """Verify phone OTP code."""
    owner_profile, _ = OwnerProfile.objects.get_or_create(user=request.user)
    
    # Check if already verified
    if owner_profile.phone_verified_at:
        messages.info(request, "Your phone number is already verified!")
        return redirect("listings:profile")
    
    if request.method == "POST":
        otp_code = request.POST.get("otp_code", "").strip()
        
        if not otp_code:
            messages.error(request, "Please enter the verification code.")
            return render(request, "listings/verify_phone_otp.html", {
                "owner_profile": owner_profile,
            })
        
        # Get OTP from cache
        cache_key = f"phone_otp_{request.user.id}"
        otp_data = cache.get(cache_key)
        
        if not otp_data:
            messages.error(request, "OTP code expired or invalid. Please request a new one.")
            return render(request, "listings/verify_phone_otp.html", {
                "owner_profile": owner_profile,
            })
        
        # Verify OTP matches
        if otp_code != otp_data.get("otp"):
            messages.error(request, "Invalid verification code. Please try again.")
            return render(request, "listings/verify_phone_otp.html", {
                "owner_profile": owner_profile,
            })
        
        # Verify it's for the correct user
        if otp_data.get("user_id") != request.user.id:
            messages.error(request, "This verification code is not for your account.")
            return render(request, "listings/verify_phone_otp.html", {
                "owner_profile": owner_profile,
            })
        
        # Mark phone as verified
        owner_profile.phone_verified_at = timezone.now()
        owner_profile.save()
        
        # Log the action
        AuditEntry.objects.create(
            subject_type="owner_profile",
            subject_id=owner_profile.id,
            actor=request.user,
            action="phone.verified",
            payload={
                "phone": owner_profile.phone_number,
            },
        )
        
        # Delete OTP from cache
        cache.delete(cache_key)
        
        messages.success(request, "Phone number verified successfully! ✓")
        return redirect("listings:profile")
    
    # GET request - show OTP entry form
    return render(request, "listings/verify_phone_otp.html", {
        "owner_profile": owner_profile,
    })


# ============================================================================
# STAFF REVIEW QUEUE VIEWS
# ============================================================================


class StaffRequiredMixin(UserPassesTestMixin):
    """Mixin to restrict views to staff members only."""

    def test_func(self):
        """Check if user is staff."""
        return self.request.user.is_staff


class ReviewQueueListView(StaffRequiredMixin, ListView):
    """Staff view showing all listings pending review or all listings based on view parameter."""

    model = Listing
    template_name = "listings/staff/review_queue.html"
    context_object_name = "listings"
    paginate_by = 20

    def get_queryset(self):
        """Get listings pending review or all listings with optimized queries."""
        # Check if viewing all listings or just pending
        view_all = self.request.GET.get("view") == "all"

        if view_all:
            # Show all listings regardless of status
            queryset = (
                Listing.objects.all()
                .select_related("owner_profile", "owner_profile__user")
                .prefetch_related("photos", "documents", "verification_requests")
                .order_by("-created_at")
            )
        else:
            # Show only pending listings (default)
            queryset = (
                Listing.objects.filter(
                    status__in=["in_review", "pending_documents", "pending_identity"]
                )
                .select_related("owner_profile", "owner_profile__user")
                .prefetch_related("photos", "documents", "verification_requests")
                .order_by("-created_at")
            )

        # Filter by status if specified
        status_filter = self.request.GET.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Filter by city if specified
        city_filter = self.request.GET.get("city")
        if city_filter:
            queryset = queryset.filter(city__icontains=city_filter)

        # Search by title
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )

        return queryset

    def get_context_data(self, **kwargs):
        """Add counts and filters to context."""
        context = super().get_context_data(**kwargs)

        # Get counts by status
        context["counts"] = {
            "in_review": Listing.objects.filter(status="in_review").count(),
            "pending_documents": Listing.objects.filter(status="pending_documents").count(),
            "pending_identity": Listing.objects.filter(status="pending_identity").count(),
            "verified": Listing.objects.filter(status="verified").count(),
            "rejected": Listing.objects.filter(status="rejected").count(),
            "draft": Listing.objects.filter(status="draft").count(),
            "pending_total": Listing.objects.filter(
                status__in=["in_review", "pending_documents", "pending_identity"]
            ).count(),
            "all_total": Listing.objects.count(),
        }

        # Pass current filters and view mode
        context["current_status"] = self.request.GET.get("status", "")
        context["current_city"] = self.request.GET.get("city", "")
        context["current_search"] = self.request.GET.get("search", "")
        context["view_all"] = self.request.GET.get("view") == "all"

        return context


class ReviewDetailView(StaffRequiredMixin, DetailView):
    """Staff view for reviewing a single listing in detail."""

    model = Listing
    template_name = "listings/staff/review_detail.html"
    context_object_name = "listing"

    def get_queryset(self):
        """Get listing with all related data."""
        return (
            Listing.objects.select_related("owner_profile", "owner_profile__user")
            .prefetch_related("photos", "documents", "verification_requests")
        )

    def get_context_data(self, **kwargs):
        """Add owner verification status and prerequisites."""
        context = super().get_context_data(**kwargs)
        listing = self.object

        # Get owner verification status
        owner = listing.owner_profile
        context["owner_verification"] = {
            "email_verified": bool(owner.email_verified_at),
            "phone_verified": bool(owner.phone_verified_at),
            "identity_verified": owner.identity_status == "approved",
            "identity_status": owner.get_identity_status_display(),
        }

        # Get prerequisites
        context["prerequisites"] = VerificationService.get_submission_prerequisites(listing)

        # Get verification request if exists
        context["verification_request"] = listing.verification_requests.filter(
            state__in=["pending", "under_review"]
        ).first()

        return context


@staff_member_required
def approve_listing_review(request, pk):
    """Approve a listing after review."""
    listing = get_object_or_404(Listing, pk=pk)

    if request.method == "POST":
        notes = request.POST.get("notes", "")

        # Use the service to approve
        VerificationService.approve_listing(
            listing=listing,
            reviewer=request.user,
            notes=notes or "Approved by staff reviewer"
        )

        # Notify owner
        NotificationService.notify_listing_approved(listing)

        messages.success(
            request,
            f"Listing '{listing.title}' has been approved and is now live!"
        )

        # Log the action
        AuditEntry.objects.create(
            subject_type="listing",
            subject_id=listing.id,
            actor=request.user,
            action="listing.approved_via_review_queue",
            payload={
                "listing_id": listing.id,
                "title": listing.title,
                "notes": notes,
            },
        )

        return redirect("listings:review_queue")

    # If GET, show confirmation page
    context = {"listing": listing}
    return render(request, "listings/staff/confirm_approve.html", context)


@staff_member_required
def reject_listing_review(request, pk):
    """Reject a listing after review."""
    listing = get_object_or_404(Listing, pk=pk)

    if request.method == "POST":
        reason = request.POST.get("reason", "")

        if not reason:
            messages.error(request, "Please provide a reason for rejection.")
            return redirect("listings:review_detail", pk=pk)

        # Use the service to reject
        VerificationService.reject_listing(
            listing=listing,
            reviewer=request.user,
            reason=reason
        )

        # Notify owner (assuming service method exists)
        # NotificationService.notify_listing_rejected(listing, reason)

        messages.warning(
            request,
            f"Listing '{listing.title}' has been rejected. Owner will be notified."
        )

        # Log the action
        AuditEntry.objects.create(
            subject_type="listing",
            subject_id=listing.id,
            actor=request.user,
            action="listing.rejected_via_review_queue",
            payload={
                "listing_id": listing.id,
                "title": listing.title,
                "reason": reason,
            },
        )

        return redirect("listings:review_queue")

    # If GET, show rejection form
    context = {"listing": listing}
    return render(request, "listings/staff/confirm_reject.html", context)


@staff_member_required
@require_http_methods(["POST"])
def document_moderation_view(request, document_id):
    """
    Approve or reject a single document via AJAX.
    
    Returns JSON response for frontend to update UI.
    """
    document = get_object_or_404(ListingDocument, pk=document_id)
    action = request.POST.get("action")  # "approve" or "reject"
    comment = request.POST.get("comment", "")
    
    if action == "approve":
        document.status = "approved"
        document.reviewer = request.user
        document.reviewed_at = timezone.now()
        document.reviewer_comment = comment or "Approved by staff"
        document.save()
        
        # Log audit entry
        AuditEntry.objects.create(
            subject_type="listing_document",
            subject_id=document.id,
            actor=request.user,
            action="document.approved",
            payload={
                "document_id": document.id,
                "doc_type": document.doc_type,
                "listing_id": document.listing.id,
            },
        )
        
        return JsonResponse({
            "success": True,
            "status": "approved",
            "status_display": document.get_status_display(),
            "reviewed_at": document.reviewed_at.isoformat(),
            "reviewer": request.user.get_full_name() or request.user.username,
        })
    
    elif action == "reject":
        if not comment:
            return JsonResponse({
                "success": False,
                "error": "Comment required for rejection"
            }, status=400)
        
        document.status = "needs_resubmission"
        document.reviewer = request.user
        document.reviewed_at = timezone.now()
        document.reviewer_comment = comment
        document.save()
        
        # Log audit entry
        AuditEntry.objects.create(
            subject_type="listing_document",
            subject_id=document.id,
            actor=request.user,
            action="document.rejected",
            payload={
                "document_id": document.id,
                "doc_type": document.doc_type,
                "listing_id": document.listing.id,
                "reason": comment,
            },
        )
        
        return JsonResponse({
            "success": True,
            "status": "needs_resubmission",
            "status_display": document.get_status_display(),
            "reviewed_at": document.reviewed_at.isoformat(),
            "reviewer": request.user.get_full_name() or request.user.username,
            "comment": comment,
        })
    
    else:
        return JsonResponse({
            "success": False,
            "error": "Invalid action. Use 'approve' or 'reject'"
        }, status=400)

