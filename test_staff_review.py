"""Test staff review queue functionality."""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'heimly.settings')
django.setup()

from django.contrib.auth.models import User
from listings.models import Listing, OwnerProfile

print("\n" + "="*60)
print("STAFF REVIEW QUEUE TEST")
print("="*60)

# Check for staff user
staff_users = User.objects.filter(is_staff=True)
if staff_users.exists():
    staff = staff_users.first()
    print(f"\n[FOUND] Staff user: {staff.username}")
else:
    print(f"\n[WARNING] No staff users found!")
    print("Create a staff user by running:")
    print("  python manage.py createsuperuser")

# Check for listings pending review
pending_listings = Listing.objects.filter(
    status__in=["in_review", "pending_documents", "pending_identity"]
)

print(f"\n[LISTINGS] Pending Review Count:")
print(f"  Total: {pending_listings.count()}")
print(f"  In Review: {Listing.objects.filter(status='in_review').count()}")
print(f"  Pending Documents: {Listing.objects.filter(status='pending_documents').count()}")
print(f"  Pending Identity: {Listing.objects.filter(status='pending_identity').count()}")

if pending_listings.exists():
    print(f"\n[SAMPLE] First pending listing:")
    listing = pending_listings.first()
    print(f"  ID: {listing.id}")
    print(f"  Title: {listing.title}")
    print(f"  Status: {listing.get_status_display()}")
    print(f"  Owner: {listing.owner_profile.user.username}")
    print(f"  Photos: {listing.photos.count()}")
    print(f"  Documents: {listing.documents.count()}")
else:
    print(f"\n[INFO] No listings pending review")
    print("To test the review queue:")
    print("  1. Login as a regular user")
    print("  2. Create a listing with photos and documents")
    print("  3. Submit for review")
    print("  4. Login as staff to see it in the review queue")

print("\n" + "="*60)
print("STAFF REVIEW QUEUE URLS")
print("="*60)
print(f"Review Queue List: http://localhost:8000/staff/reviews/")
if pending_listings.exists():
    listing_id = pending_listings.first().id
    print(f"Review Detail (example): http://localhost:8000/staff/reviews/{listing_id}/")
    print(f"Approve (example): http://localhost:8000/staff/reviews/{listing_id}/approve/")
    print(f"Reject (example): http://localhost:8000/staff/reviews/{listing_id}/reject/")

print("\n[INSTRUCTIONS] To access the staff review queue:")
print("1. Login as a staff/admin user")
print("2. Navigate to: http://localhost:8000/staff/reviews/")
print("3. You'll see all pending listings with filters")
print("4. Click 'Review' to see details and approve/reject")
print("="*60 + "\n")
