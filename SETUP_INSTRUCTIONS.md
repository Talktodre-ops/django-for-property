# Setup Instructions

## Step 1: Create Django Project
```bash
django-admin startproject heimly .
```

## Step 2: Create Listings App
```bash
python manage.py startapp listings
```

## Step 3: Run Initial Migrations (after models are created)
```bash
python manage.py makemigrations
python manage.py migrate
```

## Step 4: Create Superuser (for admin access)
```bash
python manage.py createsuperuser
```

---

**Note**: Run these commands one by one. After Step 2, I'll create all the models and code, then you can run Steps 3-4.

