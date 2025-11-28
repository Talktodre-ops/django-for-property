# Django Explained - How It Works

## What Are Those HTML Files?

The `.html` files you see are **Django Templates**. They're NOT plain HTML - they're HTML with special Django template syntax that lets you:
- Insert dynamic data from your views
- Use loops and conditionals
- Include reusable components
- Keep your HTML organized

### Example: `dashboard.html`

```html
<h1>{{ listing.title }}</h1>  <!-- Django inserts the title here -->
{% if user.is_authenticated %}  <!-- Django checks if user is logged in -->
    <p>Welcome, {{ user.username }}</p>
{% endif %}
```

Django fills in the `{{ }}` parts with actual data from your Python code!

---

## Django Architecture - MVT Pattern

Django uses the **Model-View-Template** (MVT) pattern. Here's how it works:

```
┌─────────────┐
│   BROWSER   │ (User requests a page)
└──────┬──────┘
       │ HTTP Request
       ▼
┌─────────────────────────────────────────┐
│           DJANGO PROJECT                │
│                                         │
│  ┌──────────┐    ┌──────────┐          │
│  │   URLS   │───▶│  VIEWS   │          │
│  │ (Router) │    │(Business │          │
│  └──────────┘    │  Logic)  │          │
│                  └─────┬────┘          │
│                        │               │
│                  ┌─────▼────┐          │
│                  │  MODELS  │          │
│                  │(Database)│          │
│                  └─────┬────┘          │
│                        │               │
│                  ┌─────▼────┐          │
│                  │TEMPLATES │          │
│                  │  (HTML)  │          │
│                  └──────────┘          │
│                        │               │
└────────────────────────┼───────────────┘
                         │
                         ▼
┌─────────────────────────────────────────┐
│           DATABASE (SQLite)             │
└─────────────────────────────────────────┘
                         │
                         ▼
┌─────────────┐
│   BROWSER   │ (User sees the final HTML page)
└─────────────┘
```

---

## The 4 Main Components

### 1. **MODELS** (`listings/models.py`)
**What it does:** Defines your database structure

**Think of it as:** The blueprint for your data

**Example:**
```python
class Listing(models.Model):
    title = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=12, decimal_places=2)
```

This tells Django: "Create a database table called `listing` with a `title` field and a `price` field"

**Key Point:** Models are Python classes that represent database tables. Django automatically creates SQL tables from these!

---

### 2. **VIEWS** (`listings/views.py`)
**What it does:** Contains your business logic - what happens when a user visits a page

**Think of it as:** The "brain" - it processes requests and returns responses

**Example:**
```python
def dashboard_view(request):
    # 1. Get data from database
    listings = Listing.objects.filter(status='verified')
    
    # 2. Prepare data for template
    context = {'listings': listings}
    
    # 3. Render template with data
    return render(request, 'listings/dashboard.html', context)
```

**Flow:**
1. User visits `/dashboard/`
2. Django calls `dashboard_view()`
3. View queries database
4. View passes data to template
5. Template renders HTML
6. HTML sent back to user

---

### 3. **TEMPLATES** (`listings/templates/listings/*.html`)
**What it does:** HTML files that display your data

**Think of it as:** The "face" - what users see

**Template Syntax:**
```html
<!-- Insert a variable -->
<h1>{{ listing.title }}</h1>

<!-- Conditional logic -->
{% if user.is_authenticated %}
    <p>Welcome back!</p>
{% else %}
    <p>Please login</p>
{% endif %}

<!-- Loops -->
{% for listing in listings %}
    <div>{{ listing.title }}</div>
{% endfor %}

<!-- Include other templates -->
{% extends 'base.html' %}
```

**Key Point:** Templates separate HTML design from Python logic!

---

### 4. **URLS** (`listings/urls.py` + `heimly/urls.py`)
**What it does:** Routes URLs to the correct views

**Think of it as:** A traffic director - "When user goes to /dashboard/, send them to dashboard_view()"

**Example:**
```python
urlpatterns = [
    path('dashboard/', dashboard_view, name='dashboard'),
    path('listings/<int:pk>/', listing_detail, name='listing_detail'),
]
```

**How it works:**
- User visits: `http://127.0.0.1:8000/dashboard/`
- Django checks URLs: "Ah, `/dashboard/` matches `dashboard_view`"
- Django calls: `dashboard_view(request)`

---

## Complete Request Flow Example

Let's trace what happens when a user visits the dashboard:

### Step 1: User Types URL
```
http://127.0.0.1:8000/dashboard/
```

### Step 2: Django Checks URLs
```python
# heimly/urls.py
path('', include('listings.urls'))

# listings/urls.py
path('', dashboard_view, name='dashboard')
```
✅ Match found! Call `dashboard_view(request)`

### Step 3: View Executes
```python
# listings/views.py
def dashboard_view(request):
    # Get user's profile
    owner_profile = OwnerProfile.objects.get(user=request.user)
    
    # Get user's listings
    listings = Listing.objects.filter(owner_profile=owner_profile)
    
    # Prepare data
    context = {
        'owner_profile': owner_profile,
        'listings': listings,
    }
    
    # Render template
    return render(request, 'listings/dashboard.html', context)
```

### Step 4: View Queries Database (if needed)
```python
# Django converts this Python code:
Listing.objects.filter(owner_profile=owner_profile)

# Into SQL:
# SELECT * FROM listings WHERE owner_profile_id = 1;
```

### Step 5: Template Renders
```html
<!-- listings/templates/listings/dashboard.html -->
{% extends 'base.html' %}

<h1>Welcome, {{ owner_profile.user.username }}</h1>

{% for listing in listings %}
    <div>{{ listing.title }}</div>
{% endfor %}
```

Django processes template:
- `{{ owner_profile.user.username }}` → "john_doe"
- `{% for listing in listings %}` → Loops through each listing
- `{{ listing.title }}` → "Beautiful Apartment in Lagos"

### Step 6: HTML Sent to Browser
```html
<h1>Welcome, john_doe</h1>
<div>Beautiful Apartment in Lagos</div>
<div>Luxury Villa in Abuja</div>
```

User sees the final HTML page!

---

## Key Django Concepts

### Models → Database
- Models define database structure
- Django creates tables automatically via migrations
- You interact with models using Python, not SQL

```python
# Instead of SQL:
# SELECT * FROM listings WHERE price > 1000000;

# You write Python:
listings = Listing.objects.filter(price__gt=1000000)
```

### Views → Business Logic
- Views handle HTTP requests
- Views can read/write to database
- Views return HTML responses (or JSON for APIs)

### Templates → Presentation
- Templates are HTML + Django template language
- Templates receive data from views via `context`
- Templates are rendered server-side

### URLs → Routing
- URLs map URLs to views
- Supports parameters: `/listings/123/` → `pk=123`
- Named URLs for easy linking: `{% url 'dashboard' %}`

---

## How Our Project Uses This

### Example: Creating a Listing

1. **User clicks "New Listing"** → URL: `/listings/new/`

2. **URL Router:**
   ```python
   path('listings/new/', ListingCreateView.as_view())
   ```

3. **View (ListingCreateView):**
   ```python
   # GET request: Show form
   # POST request: Save to database
   ```

4. **Template (`listing_form.html`):**
   ```html
   <form method="post">
       {{ form }}  <!-- Django renders the form -->
   </form>
   ```

5. **Model (`Listing`):**
   ```python
   # When form is submitted, Django:
   # 1. Validates data
   # 2. Creates new Listing object
   # 3. Saves to database
   # 4. Redirects to success page
   ```

---

## Why This Architecture?

✅ **Separation of Concerns:**
- Models handle data
- Views handle logic
- Templates handle display

✅ **DRY (Don't Repeat Yourself):**
- Reuse templates with `{% extends %}`
- Reuse model definitions
- Share code across views

✅ **Scalable:**
- Easy to add new features
- Database changes = just update models
- UI changes = just update templates

✅ **Secure:**
- Django handles SQL injection protection
- CSRF protection built-in
- Authentication built-in

---

## File Organization in Our Project

```
django-for-property/
├── heimly/                    # Main project config
│   ├── settings.py           # Database, apps, etc.
│   └── urls.py               # Main URL routing
│
├── listings/                  # Our app
│   ├── models.py             # Database structure (OwnerProfile, Listing, etc.)
│   ├── views.py              # Business logic (dashboard_view, etc.)
│   ├── forms.py              # Form definitions
│   ├── urls.py               # App URL routing
│   ├── admin.py              # Admin interface config
│   ├── templates/            # HTML templates
│   │   └── listings/
│   │       ├── dashboard.html
│   │       └── listing_detail.html
│   └── services/             # Business logic helpers
│
└── templates/                 # Project-wide templates
    ├── base.html             # Base template (header, footer)
    └── registration/         # Auth templates
```

---

## The Magic of Django ORM

Django's ORM (Object-Relational Mapping) lets you use Python instead of SQL:

### Instead of writing SQL:
```sql
SELECT * FROM listings 
WHERE owner_profile_id = 1 
AND status = 'verified' 
ORDER BY created_at DESC;
```

### You write Python:
```python
listings = Listing.objects.filter(
    owner_profile_id=1,
    status='verified'
).order_by('-created_at')
```

Django automatically:
- Generates the SQL
- Executes the query
- Converts results to Python objects
- Handles database connections

**This is why we can use SQLite now and switch to Postgres later - Django handles the differences!**

---

## Summary

**Models** = Database structure (Python classes)
**Views** = Business logic (Python functions/classes)
**Templates** = HTML display (HTML + Django syntax)
**URLs** = Routing (URL patterns → views)

**Flow:**
1. User requests URL
2. URLs route to view
3. View gets data from models
4. View passes data to template
5. Template renders HTML
6. HTML sent to user

That's Django in a nutshell! 🎯

