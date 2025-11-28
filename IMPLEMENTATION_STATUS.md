# Implementation Status - What's Left to Do

Based on `plan.md`, here's what's been completed and what remains:

## ✅ COMPLETED (Fully Working)

### Models & Database
- ✅ All domain models (OwnerProfile, Listing, ListingPhoto, ListingDocument, VerificationRequest, AuditEntry)
- ✅ All fields and relationships
- ✅ Indexes for O(1) performance
- ✅ Migrations applied

### Owner-Facing Features
- ✅ Dashboard view with profile status and listings grouped by status
- ✅ Owner profile update form (with ID upload)
- ✅ Listing create/edit views
- ✅ Listing detail view
- ✅ Photo upload (supports multiple files)
- ✅ Document upload
- ✅ Submit for review functionality
- ✅ Email verification (request + confirm)

### Staff/Review Features
- ✅ Review queue list view (with filters)
- ✅ Review detail view (shows all listing info)
- ✅ Approve/reject listing actions
- ✅ Django admin with custom actions

### Services & Business Logic
- ✅ VerificationService (submit, approve, reject listings)
- ✅ NotificationService (email notifications)
- ✅ Prerequisites checking

### Templates
- ✅ Dashboard
- ✅ Profile form
- ✅ Listing forms (create/edit)
- ✅ Listing detail
- ✅ Photo upload
- ✅ Document upload
- ✅ Review queue
- ✅ Review detail

---

## ❌ MISSING (To Complete MVP)

### 1. Phone OTP Verification ⚠️ **HIGH PRIORITY**

**Status:** Views don't exist yet

**Plan Requirements:**
- `PhoneOtpRequestView` (`POST /account/verify-phone/`)
- `PhoneOtpVerifyView` (`POST /account/verify-phone/confirm/`)

**What to build:**
- Generate OTP (4-6 digit code)
- Store in cache for 10 minutes
- Send OTP to console (for MVP, no SMS provider)
- Verify OTP and set `phone_verified_at`
- Similar pattern to email verification

**Files to create:**
- Add views in `listings/views.py`
- Add URLs in `listings/urls.py`
- Add buttons/forms in `owner_profile_form.html`

---

### 2. Listing Preview Template ⚠️ **MEDIUM PRIORITY**

**Status:** View exists (`listing_preview`), but template is missing

**What exists:**
- View function: `listing_preview()` in `views.py`
- URL: `/listings/<pk>/preview/`

**What's missing:**
- Template: `listings/templates/listings/listing_preview.html`

**Plan Requirements:**
- Read-only view owners can share internally
- Shows status
- Shows blocked steps
- Shows sample public view once verified

---

### 3. Document Moderation View (AJAX) ⚠️ **MEDIUM PRIORITY**

**Status:** Not implemented

**Plan Requirements:**
- `DocumentModerationView` (`POST /staff/documents/<id>/update/`)
- Allows approving/rejecting single docs without leaving list view
- Returns JSON `{"status": "approved", "reviewed_at": ...}`
- AJAX/HTMX friendly

**What to build:**
- View that accepts document ID and action (approve/reject)
- Updates document status
- Returns JSON response
- Can be called from review detail page via AJAX

---

### 4. Enhanced Document Upload Form ⚠️ **LOW PRIORITY**

**Status:** Basic form exists, but missing status badges and reviewer comments

**Plan Requirements:**
- Formset per doc type
- Shows status badges inline
- Shows reviewer comments inline
- Current form is basic - needs enhancement

**Current state:**
- Basic document upload works
- Shows list of documents
- Missing: status badges, reviewer comments display

---

### 5. Profile Page UI Integration ⚠️ **LOW PRIORITY**

**Status:** Email verification works, but UI could be better

**What exists:**
- Email verification views work
- Phone verification doesn't exist yet

**What's missing:**
- Clear buttons/UI for requesting email verification on profile page
- Clear buttons/UI for requesting phone verification on profile page
- Visual indicators of verification status

**Current state:**
- Email verification exists but might not be prominently displayed in profile form
- Phone verification needs to be added

---

## 📋 Summary

### High Priority (Complete MVP)
1. **Phone OTP Verification** - Required for full verification flow

### Medium Priority (Improve UX)
2. **Listing Preview Template** - View exists, needs template
3. **Document Moderation View** - Nice-to-have for staff workflow

### Low Priority (Polish)
4. **Enhanced Document Form** - Status badges and comments
5. **Profile UI Integration** - Better verification buttons/indicators

---

## 🎯 Recommended Next Steps

1. **Implement Phone OTP Verification** (matches email pattern)
2. **Create listing_preview.html template** (quick win)
3. **Add DocumentModerationView** (if you want AJAX document approval)
4. **Enhance profile page UI** (better verification indicators)

---

## 📝 Notes

- Most core functionality is **complete and working**
- Missing items are mostly **UX improvements** and **phone verification**
- All critical paths (create listing → upload → submit → review → approve) **work end-to-end**
- The MVP is **functional** but could use the polish items above

