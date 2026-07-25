# ScholarshipFinder Setup Guide

## Quick Start

### 1. Install Dependencies
```bash
pip install django
```

### 2. Configure Admin Password
```bash
copy .env.example .env
```
Then edit `.env` and set `ADMIN_PASSWORD` to your desired password (or keep the default).

### 3. Run Setup Script
```bash
python setup_admin.py
```

This will:
- Create database tables
- Set up admin account (reads password from `.env`)
- Configure the system

### 4. Import Scholarship Data
```bash
python manage.py import_scholarships --overwrite
```

### 5. Start Development Server
```bash
python manage.py runserver
```

### 6. Access the Application
- **Main Site**: http://localhost:8000/
- **Admin Panel**: http://localhost:8000/admin/
- **Admin Dashboard**: http://localhost:8000/admin/

## Admin Login

- **Email:** `admin@scholarshipfinder.local` ⬅️ use this to log in
- **Password:** The value you set in `.env` (default: `txUqzbAcoRa5$2`)
- **Note:** Login requires the **email address**, not the username
- **Setup:** See `SECURITY.md` for detailed instructions

⚠️ **Important**: Never commit `.env` to version control. It's already in `.gitignore`.

## Features

### For Users
- Browse scholarships with advanced filtering
- View detailed scholarship information
- Submit scholarship requests (requires admin approval)
- Track request status in profile

### For Admin
- Approve/reject scholarship requests
- Manage scholarship data via CSV import
- Monitor system statistics
- Access full Django admin panel

## CSV Import System

### Manual Import
```bash
python manage.py import_scholarships --overwrite
```

### Automatic Import
The system is configured for weekly CSV imports on Day 2 at 00:00.

### Import Features
- ✅ Handles complex multi-line CSV fields
- ✅ Skips problematic rows with detailed logging
- ✅ Overwrites existing data
- ✅ Generates import reports
- ✅ Auto-cleans logs older than 1 week

### Import Logs
- Location: `csv_import.log`
- Retention: 1 week
- Contains: Detailed error reports and statistics

## Filtering System

Users can filter scholarships by:
- **Scholarship Type** (Local Govts, Private Foundations, Applicants Abroad)
- **Scholarship Name** (text search)
- **School Year** (qualifier codes with expanded display)
- **Designated Schools** (text search)
- **Fields of Study** (text search)  
- **Multiple Grants** (Yes/No)
- **Award Amount** (text search)

## Qualifier Code Expansion

The system automatically expands qualifier codes for better readability:
- `HS` → High School
- `CT` → College of Technology
- `ST` → Specialized Training
- `UJ` → University Japanese Program
- `JL` → Japanese Language Institute
- `JC` → Junior College
- `A` → Auditors (Undergraduate)
- `U` → Undergraduate
- `R` → Research Student
- `P` → Professional Degree
- `M` → Master's
- `D` → Doctoral

## Request Approval Workflow

1. **User submits request** → Status: `pending`
2. **Admin reviews request** → Can approve/reject with notes
3. **Admin decision** → Status: `approved` or `rejected`
4. **User can view status** in their profile

## File Structure

```
ScholarshipFinder/
├── scholarships/           # Main app
│   ├── models.py          # Database models
│   ├── views.py           # View logic
│   ├── forms.py           # Form definitions
│   ├── admin.py           # Admin configuration
│   ├── urls.py            # URL routing
│   ├── templates/         # HTML templates
│   ├── management/        # Management commands
│   │   └── commands/
│   │       └── import_scholarships.py
│   └── templatetags/      # Template filters
│       └── scholarship_extras.py
├── config/                # Django settings
├── Scholarships.csv       # Scholarship data
├── setup_admin.py         # Admin setup script
├── SECURITY.md           # Security documentation
└── README.md             # This file
```

## Development

### Run Tests
```bash
pytest
```

### Code Quality
```bash
ruff check .
black .
```

### Create Superuser (if needed)
```bash
python manage.py createsuperuser
```

### Access Django Shell
```bash
python manage.py shell
```

## Troubleshooting

### Database Issues
```bash
# Reset database
del db.sqlite3
python manage.py migrate
python setup_admin.py
```

### Import Issues
```bash
# Check import logs
type csv_import.log

# Re-run import
python manage.py import_scholarships --overwrite
```

### Admin Access
```bash
# Reset admin password
python manage.py changepassword jtob
```

## Production Deployment

1. **Security**
   - Change admin password
   - Use environment variables
   - Enable HTTPS
   - Set up proper logging

2. **Performance**
   - Configure database indexes
   - Set up caching
   - Optimize static files

3. **Monitoring**
   - Monitor CSV imports
   - Track request approvals
   - Review system logs

## Support

For detailed security information, see `SECURITY.md`.

For issues with:
- **Admin access**: Check `SECURITY.md`
- **CSV imports**: Review `csv_import.log`
- **User requests**: Check admin dashboard
- **System errors**: Review Django logs