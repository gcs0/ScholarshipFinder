# ScholarshipFinder Security Documentation

## Admin Credentials

**⚠️ The admin password is stored in `.env` (gitignored) — never hardcoded in source code.**

- **Username:** `jtob` (for reference only — not used for login)
- **Email (for login):** `admin@scholarshipfinder.local`
- **Password:** Set via `.env` file — see below

### Setup

1. Copy `.env.example` to `.env`:
   ```bash
   copy .env.example .env
   ```
2. Edit `.env` and set `ADMIN_PASSWORD` to your desired password (or keep the default)
3. Run the setup script:
   ```bash
   python setup_admin.py
   ```

The script reads the password from `.env` or the `ADMIN_PASSWORD` environment variable. If neither is set, it generates a random 16-character password and prints it once.

### Security Best Practices

| Environment | Password Source | Notes |
|-------------|----------------|-------|
| Development | `.env` file | Default password safe for local dev |
| Production | Environment variable | Use `ADMIN_PASSWORD=... python setup_admin.py` or set in CI/CD secrets |

#### Production Deployment
1. **Environment Variables**: Set `ADMIN_PASSWORD` via your deployment platform's secrets manager
2. **Password Rotation**: Change admin password immediately after each deployment
3. **HTTPS Only**: Ensure admin panel is only accessible via HTTPS
4. **Access Logging**: Monitor admin access logs
5. **IP Whitelisting**: Restrict admin access to specific IP addresses

#### Git Security
The following files must **never** be committed:
- ❌ `.env` — contains real secrets (it's in `.gitignore`)
- ❌ `*.env.local` — local overrides

Safe to commit:
- ✅ `.env.example` — template with placeholder values only

Add to `.gitignore` (already done):
```
.env
.env.local
*.env.local
```

### Login Instructions

The `User` model uses `USERNAME_FIELD = "email"`. You must log in with the **email address**, not the username.

**Login URL:** http://localhost:8000/login/  
**Email:** `admin@scholarshipfinder.local`  
**Password:** The value you set in `.env`

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

- **Django Admin**: http://localhost:8000/admin/
- **Custom Admin Dashboard**: http://localhost:8000/admin/
- **Request Management**: http://localhost:8000/admin/requests/
- **CSV Reload**: http://localhost:8000/admin/reload/

### Password Security

Passwords are:
- ✅ Hashed using Django's PBKDF2 algorithm (stored in database)
- ✅ Never stored in source code
- ✅ Never exposed in logs or error messages
- ✅ Configurable via `.env` or environment variables

### Troubleshooting

#### Admin Login Issues
```bash
# Reset admin password
python manage.py changepassword jtob
```

#### Permission Issues
```bash
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
del db.sqlite3
python manage.py migrate
python setup_admin.py
```

### Maintenance

#### Regular Tasks
1. **Weekly**: Check CSV import logs for errors
2. **Monthly**: Review admin access logs
3. **Quarterly**: Update admin password via `.env` and `python manage.py changepassword jtob`
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

**Remember**: Never share admin credentials publicly or commit `.env` to version control!