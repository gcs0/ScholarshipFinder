"""
Admin Account Setup Script
This script creates the admin account for the scholarship system.
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth import get_user_model
from django.core.management import call_command

User = get_user_model()

def create_admin_account():
    """Create the admin account with secure password"""
    
    admin_username = 'jtob'
    admin_password = 'txUqzbAcoRa5$2'
    admin_email = 'admin@scholarshipfinder.local'
    
    # Check if admin user already exists
    if User.objects.filter(username=admin_username).exists():
        print(f"Admin user '{admin_username}' already exists.")
        user = User.objects.get(username=admin_username)
        
        # Update password if needed
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
    
    # Create new admin user
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
        print(f"Username: {admin_username}")
        print(f"Password: {admin_password}")
        print(f"Email: {admin_email}")
        return admin_user
        
    except Exception as e:
        print(f"Error creating admin user: {e}")
        return None

def setup_project():
    """Complete project setup"""
    print("Starting ScholarshipFinder project setup...")
    
    # Run migrations
    print("Running database migrations...")
    call_command('migrate', '--run-syncdb', verbosity=0)
    print("Migrations completed.")
    
    # Create admin account
    print("Setting up admin account...")
    admin_user = create_admin_account()
    
    if admin_user:
        print("Admin account setup completed successfully!")
        print("\n" + "="*50)
        print("ADMIN CREDENTIALS (Login with EMAIL):")
        print("="*50)
        print(f"Email:    {admin_user.email}")
        print(f"Password: {admin_password}")
        print("="*50)
        print("\nIMPORTANT SECURITY NOTES:")
        print("1. Store these credentials securely")
        print("2. Change the password after first login")
        print("3. Never commit credentials to version control")
        print("4. Use environment variables for production deployments")
        print("\nLOGIN INSTRUCTIONS:")
        print("Use the EMAIL address, NOT the username, to log in.")
        print(f"Email: {admin_user.email}")
        print("\nYou can now access the admin panel at: http://localhost:8000/admin/")
        print("You can access the admin dashboard at: http://localhost:8000/admin/")
        
        return True
    else:
        print("Failed to create admin account.")
        return False

if __name__ == '__main__':
    admin_password = 'txUqzbAcoRa5$2'  # Define for the print statement
    success = setup_project()
    sys.exit(0 if success else 1)