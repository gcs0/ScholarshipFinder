"""
Admin Account Setup Script
Reads ADMIN_PASSWORD from .env file or environment variable.
If neither is set, generates a random password printed to stdout.
"""

import os
import sys
import secrets
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth import get_user_model
from django.core.management import call_command

User = get_user_model()

def get_admin_password():
    """Read admin password from .env, env var, or generate random"""
    # Try .env file
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    if os.path.isfile(env_path):
        with open(env_path, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('ADMIN_PASSWORD='):
                    return line.split('=', 1)[1]
    # Try environment variable
    pwd = os.environ.get('ADMIN_PASSWORD')
    if pwd:
        return pwd
    # Generate random 16-char password
    return secrets.token_urlsafe(16)

def create_admin_account(admin_password):
    admin_username = 'jtob'
    admin_email = 'admin@scholarshipfinder.local'

    if User.objects.filter(username=admin_username).exists():
        print(f"Admin user '{admin_username}' already exists.")
        user = User.objects.get(username=admin_username)
        if not user.check_password(admin_password):
            user.set_password(admin_password)
            user.is_superuser = True
            user.is_staff = True
            user.email = admin_email
            user.name = 'Admin'
            user.save()
            print(f"Updated admin user '{admin_username}' password and permissions.")
        else:
            print(f"Admin user '{admin_username}' is already configured correctly.")
        return user

    try:
        admin_user = User.objects.create_user(
            username=admin_username,
            email=admin_email,
            password=admin_password,
            name='Admin',
            is_superuser=True,
            is_staff=True
        )
        admin_user.save()
        print(f"Successfully created admin user '{admin_username}'")
        return admin_user
    except Exception as e:
        print(f"Error creating admin user: {e}")
        return None

def setup_project():
    print("Starting ScholarshipFinder project setup...")
    print("Running database migrations...")
    call_command('migrate', '--run-syncdb', verbosity=0)
    print("Migrations completed.")
    print("Setting up admin account...")

    admin_password = get_admin_password()
    admin_user = create_admin_account(admin_password)

    if admin_user:
        print("Admin account setup completed successfully!")
        print("\n" + "=" * 50)
        print("ADMIN CREDENTIALS (Login with EMAIL):")
        print("=" * 50)
        print(f"Email:    {admin_user.email}")
        print(f"Password: {admin_password}")
        print("=" * 50)
        print("\n" + "!" * 50)
        print("IMPORTANT: This password was shown once -- save it securely.")
        print("!" * 50)
        print("\nTo change it later, run:  python manage.py changepassword jtob")
        print("\nLOGIN INSTRUCTIONS:")
        print("Use the EMAIL address, NOT the username, to log in.")
        print(f"Email: {admin_user.email}")
        print("\nYou can now access the admin panel at: http://localhost:8000/admin/")
        return True
    else:
        print("Failed to create admin account.")
        return False

if __name__ == '__main__':
    success = setup_project()
    sys.exit(0 if success else 1)