"""Test script to verify document upload functionality."""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'heimly.settings')
django.setup()

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from listings.models import OwnerProfile, Listing, ListingDocument

# Create test user if doesn't exist
user, created = User.objects.get_or_create(
    username='testuser',
    defaults={'email': 'test@example.com'}
)
if created:
    user.set_password('testpass123')
    user.save()
    print(f"[OK] Created test user: {user.username}")
else:
    print(f"[OK] Using existing user: {user.username}")

# Create owner profile
profile, created = OwnerProfile.objects.get_or_create(user=user)
print(f"[OK] Owner profile: {profile}")

# Create test listing if doesn't exist
listing, created = Listing.objects.get_or_create(
    owner_profile=profile,
    title="Test Property",
    defaults={
        'description': 'Test property for upload verification',
        'property_type': 'apartment',
        'listing_type': 'rent',
        'address_line': '123 Test Street',
        'city': 'Lagos',
        'state': 'Lagos',
        'price': 100000,
    }
)
print(f"[OK] Listing: {listing.title}")

# Create a simple test PDF file
test_file_content = b'%PDF-1.4\nTest PDF content for document upload verification'
test_file = SimpleUploadedFile(
    "test_certificate.pdf",
    test_file_content,
    content_type="application/pdf"
)

# Create document
doc = ListingDocument.objects.create(
    listing=listing,
    doc_type='c_of_o',
    file=test_file,
    status='uploaded'
)
print(f"[OK] Document created: {doc}")
print(f"  - File path: {doc.file.name}")
print(f"  - File exists on disk: {os.path.exists(doc.file.path)}")
print(f"  - Full path: {doc.file.path}")

# Verify in database
total_docs = ListingDocument.objects.count()
print(f"\n[OK] Total documents in database: {total_docs}")

# Check media directory
media_root = django.conf.settings.MEDIA_ROOT
print(f"\n[OK] MEDIA_ROOT: {media_root}")
print(f"[OK] MEDIA_URL: {django.conf.settings.MEDIA_URL}")

if os.path.exists(media_root):
    print(f"[OK] Media directory exists")
    for root, dirs, files in os.walk(media_root):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, media_root)
            print(f"  - {rel_path}")
else:
    print(f"[ERROR] Media directory does NOT exist!")

print("\n" + "="*50)
print("TEST COMPLETE")
print("="*50)
