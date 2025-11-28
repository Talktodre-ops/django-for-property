"""Test email verification flow."""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'heimly.settings')
django.setup()

from django.contrib.auth.models import User
from django.core.cache import cache
from listings.models import OwnerProfile
import secrets

print("\n" + "="*60)
print("EMAIL VERIFICATION FLOW TEST")
print("="*60)

# Get a test user
user = User.objects.filter(username='testuser').first()
if not user:
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
    print(f"[CREATED] New test user: {user.username}")
else:
    print(f"[FOUND] Test user: {user.username}")

# Get or create profile
profile, created = OwnerProfile.objects.get_or_create(user=user)
print(f"[OK] Profile status:")
print(f"     Email verified: {profile.email_verified_at}")
print(f"     Phone verified: {profile.phone_verified_at}")
print(f"     Identity status: {profile.identity_status}")

# Test token generation (simulate what view does)
token = secrets.token_urlsafe(32)
cache_key = f"email_verify_{token}"
cache.set(cache_key, user.id, timeout=86400)  # 24 hours

print(f"\n[TOKEN] Generated verification token:")
print(f"     Token: {token[:20]}...")
print(f"     Cache key: {cache_key}")
print(f"     User ID stored: {user.id}")

# Verify token can be retrieved
retrieved_user_id = cache.get(cache_key)
print(f"\n[VERIFY] Token retrieval test:")
print(f"     Retrieved user ID: {retrieved_user_id}")
print(f"     Match: {retrieved_user_id == user.id}")

# Clean up
cache.delete(cache_key)
print(f"\n[CLEANUP] Token deleted from cache")

print("\n" + "="*60)
print("VERIFICATION FLOW URLS:")
print("="*60)
print(f"Request verification: http://localhost:8000/verify-email/")
print(f"Confirm with token: http://localhost:8000/verify-email/{token}/")
print("\nTo test manually:")
print("1. Login as the test user")
print("2. Go to Profile page")
print("3. Click 'Verify Email' button")
print("4. Check console output for verification link")
print("5. Click the link to verify")
print("="*60 + "\n")
