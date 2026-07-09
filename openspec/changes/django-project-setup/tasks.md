## 1. Django Dependencies

- [x] 1.1 Add Django to pyproject.toml dependencies
- [x] 1.2 Install Django via pip

## 2. Django Project Scaffold

- [x] 2.1 Run `django-admin startproject config .` to create project files at root
- [x] 2.2 Verify `manage.py` and `config/` directory exist
- [x] 2.3 Run `python manage.py startapp scholarships` to create the app

## 3. Database Models

- [x] 3.1 Define `User` model in `scholarships/models.py` with name, email, education, discipline, prefecture fields and `__str__()`
- [x] 3.2 Define `Scholarship` model with name, provider, award_amount, education_level, discipline, prefecture, deadline, requirements, description fields and `__str__()`
- [x] 3.3 Define `ScholarshipRequest` model with ForeignKey to User, scholarship_name, provider, award_amount, notes fields and `__str__()`

## 4. App Registration & Migrations

- [x] 4.1 Register `scholarships` in `INSTALLED_APPS` in `config/settings.py`
- [x] 4.2 Run `python manage.py makemigrations scholarships`
- [x] 4.3 Run `python manage.py migrate`

## 5. Verification

- [x] 5.1 Run `python manage.py check` and confirm it exits with code 0
- [x] 5.2 Run `ruff check .` and confirm it exits with code 0
- [x] 5.3 Run `black --check .` and confirm it exits with code 0
- [x] 5.4 Run `pytest` (or `python manage.py test scholarships`) and confirm tests are discovered and pass
