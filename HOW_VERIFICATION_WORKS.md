# How Verification Works - Complete Guide

## What Happens When You Save Your Profile

### 1. **You Save Your Profile** (What you just did)
- Fill in phone number, ID details, upload ID document
- Click "Save Profile"
- Your profile status automatically changes to **"Pending Review"**
- You see a success message

### 2. **Staff Reviews Your Profile** (Admin Process)
Currently, this happens in Django Admin:

**To Review Your Own Profile:**
1. Login as superuser at `http://127.0.0.1:8000/admin/`
2. Go to "Owner Profiles" section
3. Find your profile
4. Click on it to open
5. Review the ID document
6. Use admin actions to approve/reject

**What Staff Checks:**
- ID document is clear and valid
- ID number matches the type selected
- Contact information is provided

### 3. **Profile Gets Approved**
Once approved:
- Status changes to **"Approved"**
- You can now submit listings
- Dashboard shows green "Approved" status

---

## What Happens When You Submit a Listing

### Prerequisites Check:
Before you can submit, the system verifies:
- ✅ Owner identity is approved
- ✅ At least one contact verified (email OR phone)
- ✅ At least 1 photo uploaded
- ✅ At least 1 primary photo
- ✅ At least 1 document uploaded

If anything is missing, you'll see error messages telling you what to fix.

### Submission Process:
1. Click "Submit for Review" on your listing
2. System checks all prerequisites
3. If all pass → Listing status becomes **"In Review"**
4. VerificationRequest is created
5. Staff gets notification (currently in admin)

### Staff Reviews Listing:
1. Go to admin → Listings
2. Filter by status "In Review"
3. Open listing to see:
   - All photos
   - All documents
   - Property details
   - Owner information
4. Review everything
5. Approve or reject with reason

### Listing Goes Live:
Once approved:
- Status → **"Verified"**
- Visibility → **"Public"**
- Listing appears on platform
- Owner gets notification

---

## Current Verification Flow

```
┌─────────────────────────────────────────────────────┐
│  YOU (Owner)                                        │
│  1. Create account                                  │
│  2. Fill profile + Upload ID                        │
│  3. Status: "Pending Review"                        │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│  STAFF (Admin)                                      │
│  1. Go to /admin/                                   │
│  2. Open Owner Profiles                             │
│  3. Review ID document                              │
│  4. Approve/Reject                                  │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│  PROFILE APPROVED                                   │
│  • You can now create listings                      │
│  • Add photos & documents                           │
│  • Submit for review                                │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│  LISTING SUBMITTED                                  │
│  • System validates prerequisites                   │
│  • Creates VerificationRequest                      │
│  • Status: "In Review"                              │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│  STAFF REVIEWS LISTING                              │
│  • Check photos, documents, details                 │
│  • Approve or reject                                │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│  LISTING VERIFIED & LIVE!                           │
│  • Status: "Verified"                               │
│  • Visibility: "Public"                             │
│  • Appears on platform                              │
└─────────────────────────────────────────────────────┘
```

---

## How to Test the Verification Flow

### Step 1: Test Profile Approval
1. Save your profile (you already did this)
2. Login to admin: `http://127.0.0.1:8000/admin/`
3. Go to "Owner Profiles"
4. Find your profile
5. Select it
6. Use "Approve selected profiles" action from dropdown
7. Click "Go"
8. Check dashboard - status should be "Approved"

### Step 2: Create a Listing
1. Click "New Listing"
2. Fill in all details
3. Save (creates draft)

### Step 3: Add Photos & Documents
1. Go to listing detail page
2. Click "Manage Photos" - upload at least 1 photo, mark one as primary
3. Click "Manage Documents" - upload at least 1 document

### Step 4: Submit for Review
1. On listing detail page, click "Submit for Review"
2. If everything is correct, status becomes "In Review"
3. If something is missing, you'll see error messages

### Step 5: Review in Admin
1. Go to admin → Listings
2. Filter by status "In Review"
3. Open your listing
4. Review everything
5. Use "Approve selected listings" action
6. Check dashboard - listing should be "Verified"

---

## Next Steps to Improve

Currently, verification happens in Django admin. For production, you might want:
- Dedicated staff review interface (custom views)
- Email notifications when profile/listing needs review
- Better status tracking on dashboard
- Rejection reasons visible to users

But for MVP, Django admin works perfectly! ✅

---

## Quick Commands

**Check your profile status:**
- Dashboard shows it
- Or: Admin → Owner Profiles → Find yourself

**Check listing status:**
- Dashboard shows all listings by status
- Or: Admin → Listings → Filter by status

**Approve profiles/listings:**
- Admin → Select items → Choose action from dropdown → Go

