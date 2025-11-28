# How to Check ID Documents in Django Admin

## Quick Steps to Review Uploaded IDs

### Step 1: Login to Admin
```
Go to: http://127.0.0.1:8000/admin/
Login with your superuser credentials
```

### Step 2: Find Owner Profiles
1. In the admin sidebar, look for **"LISTINGS"** section
2. Click on **"Owner Profiles"**

### Step 3: View Profile Details
1. You'll see a list of all profiles with:
   - Username
   - Identity Status (Incomplete, Pending Review, Approved, Rejected)
   - ID Type (NIN, Passport, etc.)
   - ID Number
   - Created date

2. **Click on a username** to open the profile details

### Step 4: Review ID Document
In the profile detail page, you'll see:

**Identity Verification Section:**
- ID Type: Shows what type of ID (NIN, Passport, Driver's License)
- ID Number: The ID number they provided
- **ID Document:** This shows the uploaded file - **CLICK ON IT** to view/download
- ID Expiry Date: If provided
- Identity Status: Current status (change this to approve/reject)
- Identity Reviewer: Who reviewed it (auto-filled when you approve)
- Identity Reviewed At: When it was reviewed
- Identity Notes: Add notes about the review

### Step 5: View the Document
1. In the "ID Document" field, you'll see a link to the file
2. **Click the file link** - it will open/download the document
3. Review the document:
   - Is it clear and readable?
   - Does the ID number match what they entered?
   - Is it a valid ID type?
   - Does it match the ID type selected?

### Step 6: Approve or Reject

**Option A: Using Admin Actions (Easier)**
1. Go back to the Owner Profiles list
2. Check the box next to the profile(s) you want to approve
3. At the top, find the dropdown "Action:"
4. Select **"Approve selected profiles"**
5. Click the **"Go"** button
6. Done! Status changes to "Approved"

**Option B: Manual Approval**
1. In the profile detail page
2. Find "Identity Status" field
3. Change it from "Pending Review" to "Approved"
4. Add any notes in "Identity Notes" (optional)
5. Click **"Save"** at the bottom

### Step 7: Add Review Notes (Optional)
- In "Identity Notes" field, you can add:
  - Reasons for approval
  - Any concerns
  - Additional information
- This helps with audit trail

---

## Quick Checklist for Review

When reviewing a profile, check:

- [ ] ID document is clear and readable
- [ ] ID number matches what's entered
- [ ] ID type matches the document
- [ ] Contact information is provided
- [ ] Document appears legitimate

**If everything looks good:** Approve
**If something is wrong:** Reject and add notes explaining why

---

## Filter Profiles Needing Review

To see only profiles that need review:

1. In Owner Profiles list
2. Look for the filter sidebar on the right
3. Under "Identity Status" filter
4. Select **"Pending Review"**
5. Click the filter - now you only see profiles waiting for review!

---

## Search for Specific Users

To find a specific user's profile:

1. Use the search box at the top
2. Search by:
   - Username
   - Email
   - ID Number
   - Phone Number
3. Click on the result to view

---

## Tips

- **Document Preview:** If it's an image (JPG, PNG), clicking the link will show it in browser
- **PDF Files:** Will download - open to view
- **Multiple Reviews:** You can approve/reject multiple profiles at once using admin actions
- **Audit Trail:** All approvals/rejections are logged in Audit Entries

---

## Troubleshooting

**Can't see the ID document?**
- Make sure media files are being served (check MEDIA_URL setting)
- File might not have uploaded - check file size limits

**Status won't change?**
- Make sure you're logged in as superuser
- Check if you have permissions
- Try refreshing the page

**Can't find a profile?**
- Use the search function
- Check if they actually saved their profile
- Look in "Incomplete" status filter

---

That's it! Now you can easily review all uploaded ID documents in the admin! 🎯

