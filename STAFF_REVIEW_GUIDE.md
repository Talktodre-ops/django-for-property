# Staff Review Queue - User Guide

## Overview
The Staff Review Queue is a dedicated interface for staff members to efficiently review and approve property listings submitted by owners.

## Access Requirements
- Must be logged in as a staff user (`is_staff=True`)
- Staff users can access via the "Review Queue" link in the navigation bar

## Features

### 1. Review Queue List
**URL:** `http://localhost:8000/staff/reviews/`

**What you see:**
- Stats cards showing:
  - In Review count
  - Pending Documents count
  - Pending Identity count
- Filter and search options:
  - Search by title/description
  - Filter by status
  - Filter by city
- Table showing all pending listings with:
  - Property photo thumbnail
  - Property title and type
  - Owner name and email
  - Owner verification badges (email, ID)
  - Location
  - Price
  - Current status
  - Submission date
  - "Review" button

### 2. Review Detail Page
**URL:** `http://localhost:8000/staff/reviews/<listing_id>/`

**What you see:**
- **Property Photos:** Full gallery with primary photo indicator
- **Property Details:**
  - Type, listing type, price, size
  - Bedrooms, bathrooms
  - Address and location
  - Full description
  - Amenities list
- **Property Documents:** All uploaded documents with view links
- **Owner Information (Sidebar):**
  - Name, email, phone
  - Verification status badges
  - Link to view owner ID document
- **Prerequisites Check:**
  - Owner verified status
  - Photos uploaded status
  - Documents uploaded status
- **Review Actions:**
  - Green "Approve Listing" button
  - Red "Reject Listing" button
- **Timeline:** Created and updated dates

### 3. Approve Listing
**URL:** `http://localhost:8000/staff/reviews/<listing_id>/approve/`

**What happens:**
1. Shows confirmation page with listing details
2. Optional field for approval notes
3. Information box explaining what happens when you approve
4. On submit:
   - Listing status → "Verified"
   - Listing visibility → "Public"
   - Owner receives email notification
   - Action logged in audit trail
   - Redirects back to review queue

### 4. Reject Listing
**URL:** `http://localhost:8000/staff/reviews/<listing_id>/reject/`

**What happens:**
1. Shows rejection form with listing details
2. **Required** rejection reason field
3. Helpful tips for common rejection reasons
4. Information box explaining what happens when you reject
5. On submit:
   - Listing status → "Rejected"
   - Listing remains private
   - Owner receives notification with rejection reason
   - Owner can revise and resubmit
   - Action logged in audit trail
   - Redirects back to review queue

## Testing the Workflow

### Step 1: Create Test Data
As a regular user:
1. Login at `http://localhost:8000/login/`
2. Complete your profile with ID verification
3. Create a listing
4. Upload photos and documents
5. Submit for review

### Step 2: Access Review Queue
As a staff user (victus):
1. Login at `http://localhost:8000/login/`
2. Click "Review Queue" in navigation
3. You should see the listing in the pending list

### Step 3: Review Listing
1. Click "Review" button on the listing
2. Review all details:
   - Check photos are clear and appropriate
   - Verify property information is complete
   - Check owner verification status
   - Review uploaded documents
3. Check prerequisites are met

### Step 4: Approve or Reject

**To Approve:**
1. Click green "Approve Listing" button
2. Optionally add approval notes
3. Click "Confirm Approval"
4. See success message
5. Listing disappears from review queue
6. Check owner's dashboard - listing should show as "Verified"

**To Reject:**
1. Click red "Reject Listing" button
2. Enter specific rejection reason (required)
3. Click "Confirm Rejection"
4. See warning message
5. Listing disappears from review queue
6. Check owner's dashboard - listing should show as "Rejected"

## Database Changes

### When Approving:
- `listing.status` → `"verified"`
- `listing.visibility_state` → `"public"`
- `listing.verified_at` → current timestamp
- `verification_request.state` → `"approved"`
- `verification_request.reviewer` → staff user
- `verification_request.decided_at` → current timestamp
- New `AuditEntry` created

### When Rejecting:
- `listing.status` → `"rejected"`
- `listing.rejection_reason` → provided reason
- `verification_request.state` → `"rejected"`
- `verification_request.reviewer` → staff user
- `verification_request.decided_at` → current timestamp
- New `AuditEntry` created

## Audit Trail
All approve/reject actions are logged with:
- Subject type: "listing"
- Subject ID: listing ID
- Actor: staff user who performed action
- Action: "listing.approved_via_review_queue" or "listing.rejected_via_review_queue"
- Payload: listing details, notes/reason

## Running Tests

### Test 1: URL Configuration
```bash
python -c "from django.urls import reverse; import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'heimly.settings'); import django; django.setup(); print('Review Queue:', reverse('listings:review_queue'))"
```

### Test 2: Check Staff Access
```bash
python test_staff_review.py
```

### Test 3: Manual Testing
1. Create listing as regular user
2. Submit for review
3. Login as staff
4. Navigate to review queue
5. Test approve flow
6. Create another listing
7. Test reject flow

## Troubleshooting

**Q: I don't see "Review Queue" in navigation**
- A: Make sure you're logged in as a staff user. Check `user.is_staff` is `True`

**Q: Review queue shows 0 pending**
- A: No listings have been submitted for review yet. Create and submit a listing first.

**Q: I get permission denied accessing review pages**
- A: Only staff users can access. Check `is_staff` flag on your user account.

**Q: Approve/reject buttons don't work**
- A: Check browser console for JavaScript errors. Ensure Django server is running.

**Q: Listing doesn't update after approval**
- A: Check server logs for errors. Verify VerificationService methods are working correctly.

## Integration Points

The Staff Review Queue integrates with:
- **VerificationService:** Uses `approve_listing()` and `reject_listing()` methods
- **NotificationService:** Calls `notify_listing_approved()`
- **AuditEntry:** Creates audit logs for compliance
- **Owner Dashboard:** Approved listings appear as "Verified"
- **Public Listings:** Approved listings become publicly visible

## Screenshots Location
Screenshots of the review queue in action can be found in the user's browser at:
- Review Queue: `http://localhost:8000/staff/reviews/`
- (Screenshot showing 0 pending listings is already provided by user)
