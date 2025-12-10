#!/usr/bin/env python
"""
Create or update Django superuser
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nuam.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Superuser credentials
USERNAME = 'admin'
EMAIL = 'admin@nuam.com'
PASSWORD = 'admin123'

# Check if user exists
if User.objects.filter(username=USERNAME).exists():
    print(f"User '{USERNAME}' already exists. Updating...")
    user = User.objects.get(username=USERNAME)
    user.set_password(PASSWORD)
    user.is_superuser = True
    user.is_staff = True
    user.is_active = True
    user.email = EMAIL
    user.save()
    print(f"✓ User '{USERNAME}' updated successfully")
else:
    print(f"Creating superuser '{USERNAME}'...")
    user = User.objects.create_superuser(
        username=USERNAME,
        email=EMAIL,
        password=PASSWORD
    )
    print(f"✓ Superuser '{USERNAME}' created successfully")

print("\n" + "="*50)
print("SUPERUSER CREDENTIALS")
print("="*50)
print(f"Username: {USERNAME}")
print(f"Password: {PASSWORD}")
print(f"Email:    {EMAIL}")
print("="*50)
print("\nLogin URLs:")
print("  Django Admin:  http://localhost/admin/")
print("  Django App:    http://localhost/accounts/login/")
print("="*50)
