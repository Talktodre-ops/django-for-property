# Testing Multiple Users (Admin + Regular User)

## The Problem You're Experiencing

When you login as different users in different tabs, **they conflict** because Django uses **session cookies** that are shared across all tabs in the same browser.

When you login as "admin" in one tab, then login as "talktodre" in another tab, the second login **overwrites** the session cookie, so both tabs are now logged in as "talktodre".

---

## Solution: Use Different Browsers or Incognito/Private Windows

### Option 1: Different Browsers (Recommended)
- **Tab 1:** Use **Chrome** - Login as `admin`
- **Tab 2:** Use **Firefox** or **Edge** - Login as `talktodre`

Each browser has separate cookies, so they won't interfere.

### Option 2: Incognito/Private Windows (Easier)
- **Tab 1:** Normal Chrome window - Login as `admin`
- **Tab 2:** **Incognito/Private window** (Ctrl+Shift+N in Chrome) - Login as `talktodre`

Incognito windows use separate cookie storage.

### Option 3: Different Browser Profiles
- Chrome/Edge allow you to create multiple profiles
- Each profile has separate cookies
- Click your profile icon → "Add" → Create "Admin Profile" and "User Profile"

---

## Why This Happens

Django authentication uses **session cookies**:
1. When you login, Django creates a session ID
2. This session ID is stored in a cookie called `sessionid`
3. **All tabs in the same browser share the same cookies**
4. When you login again, the `sessionid` cookie gets overwritten
5. Now all tabs use the new session

This is normal browser behavior, not a Django bug!

---

## Quick Test Workflow

### Setup:
1. **Regular Chrome window:** Login as `admin` → Go to http://localhost:8000/admin
2. **Incognito Chrome window:** Login as `talktodre` → Go to http://localhost:8000/profile

### Workflow:
1. In Incognito window (talktodre):
   - Upload ID document
   - Save profile
   - See status: "Pending Review"

2. In Regular window (admin):
   - Go to "Owner profiles"
   - See talktodre's profile
   - Click the ID document link
   - Approve the profile

3. Back in Incognito window (talktodre):
   - Refresh the profile page
   - See status: "Approved"! ✅

---

## Alternative: Use Django Debug Toolbar (Future)

For development, you could install Django Debug Toolbar which lets you see which user is logged in on each tab. But the easiest solution is just using different browsers/incognito.

