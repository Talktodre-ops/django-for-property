"""Test script to verify owner ID document upload."""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'heimly.settings')
django.setup()

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from listings.models import OwnerProfile
from listings.forms import OwnerProfileForm

# Get or create a real user
user, created = User.objects.get_or_create(
    username='uploadtest',
    defaults={'email': 'uploadtest@example.com'}
)
if created:
    user.set_password('testpass123')
    user.save()

print(f"[OK] User: {user.username}")

# Get or create profile
profile, created = OwnerProfile.objects.get_or_create(user=user)
print(f"[OK] Profile created: {created}")
print(f"     Current ID doc: {profile.id_document}")
print(f"     Current status: {profile.identity_status}")

# Create test file (simulate user upload)
test_file = SimpleUploadedFile(
    "test_nin.pdf",
    b'%PDF-1.4\nTest NIN document',
    content_type="application/pdf"
)

# Test the form
print("\n[TEST] Testing form with file upload...")
form_data = {
    'phone_number': '+234 800 123 4567',
    'whatsapp_number': '+234 800 123 4567',
    'preferred_contact': 'phone',
    'id_type': 'nin',
    'id_number': '12345678901',
    'id_expiry_date': '2030-12-31',
}

form = OwnerProfileForm(
    data=form_data,
    files={'id_document': test_file},
    instance=profile
)

print(f"[CHECK] Form is valid: {form.is_valid()}")
if not form.is_valid():
    print(f"[ERROR] Form errors: {form.errors}")
else:
    # Save the form
    saved_profile = form.save()
    print(f"[OK] Form saved successfully")

    # Refresh and check
    saved_profile.refresh_from_db()
    print(f"\n[RESULT] After save:")
    print(f"  - ID Type: {saved_profile.id_type}")
    print(f"  - ID Number: {saved_profile.id_number}")
    print(f"  - ID Document: {saved_profile.id_document}")
    print(f"  - ID Document name: {saved_profile.id_document.name if saved_profile.id_document else 'EMPTY'}")
    print(f"  - File exists: {os.path.exists(saved_profile.id_document.path) if saved_profile.id_document else 'N/A'}")
    print(f"  - Status: {saved_profile.identity_status}")

    # Check what the view would do
    if saved_profile.id_type and saved_profile.id_number and saved_profile.id_document:
        print(f"\n[OK] All conditions met - would set status to pending_review")
    else:
        print(f"\n[ERROR] Missing data:")
        if not saved_profile.id_type:
            print(f"  - No ID type")
        if not saved_profile.id_number:
            print(f"  - No ID number")
        if not saved_profile.id_document:
            print(f"  - No ID document")

print("\n" + "="*50)
