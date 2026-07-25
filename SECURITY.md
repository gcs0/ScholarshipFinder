# ScholarshipFinder Security Documentation

## Admin Credentials

**⚠️ IMPORTANT SECURITY NOTICE — LOGIN WITH EMAIL, NOT USERNAME**

The system uses email-based authentication. You must log in with the email address, not the username.

- **Username:** `jtob` (for reference only — not used for login)
- **Email (for login):** `admin@scholarshipfinder.local`
- **Password:** `txUqzbAcoRa5$2`

### Security Measures Implemented

1. **Password Hashing**: Django uses PBKDF2 with SHA256 hash algorithm by default
2. **Superuser Access**: Admin account has both `is_superuser` and `is_staff` permissions
3. **Admin Interface**: Full access to Django admin panel and custom admin views

### Setup Instructions

#### Initial Setup
```bash
# Run the admin setup script
python setup_admin.py
```

This script will:
- Run all database migrations
- Create the admin account with hashed password
- Provide setup confirmation

#### Manual Admin Creation
If you need to create the admin account manually:

```bash
python manage.py createsuperuser
```

Then provide:
- Username: `jtob`
- Email: `admin@scholarshipfinder.local` 
- Password: `txUqzbAcoRa5$2`

### Security Best Practices

#### Development Environment
1. ✅ Admin credentials are stored in Django's built-in password hashing
2. ✅ Never commit actual passwords to version control
3. ✅ Use environment variables for sensitive data in production

#### Production Deployment
1. **Environment Variables**: Store admin credentials in environment variables
2. **Password Rotation**: Change admin password immediately after first deployment
3. **Access Logging**: Monitor admin access logs
4. **HTTPS Only**: Ensure admin panel is only accessible via HTTPS
5. **IP Whitelisting**: Restrict admin access to specific IP addresses

#### Git Security
The following files should never be committed to version control:
- ❌ `.env` files containing actual credentials
- ❌ Hardcoded passwords in Python files
- ❌ Configuration files with sensitive data

Add to `.gitignore`:
```
.env
*.env
local_settings.py
csv_import.log
```

### Admin Features

The admin account (`jtob`) has access to:

1. **Django Admin Panel** (`/admin/`)
   - User management
   - Scholarship management
   - Scholarship request approval
   - Import monitoring

2. **Custom Admin Dashboard** (`/admin/`)
   - Request overview statistics
   - Recent requests list
   - Quick approval actions

3. **Scholarship Management**
   - View all imported scholarships
   - Monitor CSV import status
   - Manual CSV reload capability

4. **Request Approval System**
   - Review pending scholarship requests
   - Approve or reject with notes
   - Track approval history

### Access URLs

- **Django Admin**: `http://localhost:8000/admin/`
- **Custom Admin Dashboard**: `http://localhost:8000/admin/`
- **Request Management**: `http://localhost:8000/admin/requests/`
- **CSV Reload**: `http://localhost:8000/admin/reload/`

### Password Security

The admin password `txUqzbAcoRa5$2` is:
- ✅ Hashed using Django's PBKDF2 algorithm
- ✅ Stored securely in the database
- ✅ Never exposed in logs or error messages
- ⚠️ Should be changed for production use

### Troubleshooting

#### Admin Login Issues
```bash
# Reset admin password
python manage.py changepassword jtob
```

#### Permission Issues
```bash
# Ensure user is superuser
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> user = User.objects.get(username='jtob')
>>> user.is_superuser = True
>>> user.is_staff = True
>>> user.save()
```

#### Database Issues
```bash
# Reset database (WARNING: Deletes all data)
del db.sqlite3
python manage.py migrate
python setup_admin.py
```

### Maintenance

#### Regular Tasks
1. **Weekly**: Check CSV import logs for errors
2. **Monthly**: Review admin access logs
3. **Quarterly**: Update admin password
4. **As needed**: Monitor request approval queue

#### Log Files
- CSV Import Log: `csv_import.log` (auto-cleaned after 1 week)
- Django Logs: Check Django admin logs for system events

### Contact & Support

For security issues or admin access problems:
1. Check this documentation first
2. Review CSV import logs
3. Check Django admin logs
4. Contact system administrator

---

**Remember**: Never share admin credentials publicly or commit them to version control!