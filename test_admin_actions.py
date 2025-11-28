"""Test admin actions are properly registered."""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'heimly.settings')
django.setup()

from listings.admin import OwnerProfileAdmin
from listings.models import OwnerProfile

print("\n" + "="*60)
print("ADMIN ACTIONS TEST")
print("="*60)

# Get the admin class
admin = OwnerProfileAdmin(OwnerProfile, None)

print(f"\n[CHECK] Registered actions:")
for action_name in admin.actions:
    print(f"  - {action_name}")

# Check if actions are callable
print(f"\n[CHECK] Action methods:")
if hasattr(admin, 'verify_email'):
    print(f"  [OK] verify_email method exists")
    print(f"    Description: {admin.verify_email.short_description}")
else:
    print(f"  [ERROR] verify_email method NOT found")

if hasattr(admin, 'verify_phone'):
    print(f"  [OK] verify_phone method exists")
    print(f"    Description: {admin.verify_phone.short_description}")
else:
    print(f"  [ERROR] verify_phone method NOT found")

if hasattr(admin, 'approve_profiles'):
    print(f"  [OK] approve_profiles method exists")
    print(f"    Description: {admin.approve_profiles.short_description}")
else:
    print(f"  [ERROR] approve_profiles method NOT found")

if hasattr(admin, 'reject_profiles'):
    print(f"  [OK] reject_profiles method exists")
    print(f"    Description: {admin.reject_profiles.short_description}")
else:
    print(f"  [ERROR] reject_profiles method NOT found")

print("\n" + "="*60)
print("HOW TO USE IN ADMIN:")
print("="*60)
print("1. Go to: http://localhost:8000/admin/")
print("2. Login with your admin account")
print("3. Navigate to: Listings > Owner profiles")
print("4. Select one or more profiles using checkboxes")
print("5. In the 'Action' dropdown at the top, you should see:")
print("   - Approve selected profiles")
print("   - Reject selected profiles")
print("   - Manually verify email")
print("   - Manually verify phone")
print("6. Select an action and click 'Go'")
print("="*60 + "\n")
