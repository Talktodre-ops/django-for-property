# Verification Flow - How It Works

## Current Flow After You Save Your Profile

### Step 1: Profile Submission
When you click "Save Profile" after uploading your ID:
- Your profile status changes to **"Pending Review"**
- Your identity information is saved (ID type, ID number, ID document)
- Staff members will be notified (currently via Django admin)

### Step 2: Staff Review (Admin)
A staff member (superuser) must review your profile in Django admin:
- Go to `/admin/`
- Find your profile under "Owner Profiles"
- Review your ID document and details
- Approve or reject your identity

### Step 3: Profile Approval
Once approved:
- Your `identity_status` becomes **"Approved"**
- You can now submit listings for verification
- You'll see a success message/notification

---

## Listing Verification Flow

### Step 1: Create Listing
- Create a property listing (status: **Draft**)
- Add photos (minimum 1, including primary photo)
- Upload property documents (C of O, Deed, Utility Bill, etc.)

### Step 2: Submit for Review
Click "Submit for Review" button. System checks:
- ✅ Owner identity is approved
- ✅ At least one contact method verified (email OR phone)
- ✅ At least 1 photo uploaded
- ✅ At least 1 primary photo
- ✅ At least 1 document uploaded

If all checks pass:
- Listing status → **"In Review"** or **"Pending Documents"**
- VerificationRequest created
- Staff notification sent

### Step 3: Staff Review
Staff reviews in Django admin:
- Checks all documents
- Reviews photos
- Verifies property details
- Approves or rejects

### Step 4: Listing Goes Live
If approved:
- Status → **"Verified"**
- Visibility → **"Public"**
- Listing is live on platform!

---

## What's Currently Missing

We need to add admin actions to easily approve/reject profiles. Let me add that now!

