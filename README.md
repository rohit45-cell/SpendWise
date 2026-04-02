# 🚀 SpendWise Pro — Setup Guide

## Quick Start (5 Minutes)

### Step 1: Prerequisites
Make sure you have Python 3.10+ installed:
```bash
python --version  # Should be 3.10+
```

### Step 2: Create & Activate Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Requirements
```bash
pip install -r requirements.txt

```

### Step 4: Run Migrations
```bash
python manage.py makemigrations tracker
python manage.py migrate
```

### Step 5: Create Superuser (Admin)
```bash
python manage.py createsuperuser
# Enter username, email, and password when prompted
```

### Step 6: Start Development Server
```bash
python manage.py runserver
```

### Step 7: Open in Browser
- **App:** http://127.0.0.1:8000/
- **Admin:** http://127.0.0.1:8000/admin/

---

## 📂 Project Structure

```
spendwise_pro/
├── manage.py
├── requirements.txt
├── README.md
│
├── spendwise/              ← Django project settings
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── templates/          ← HTML templates
│   │   ├── base.html
│   │   ├── landing.html
│   │   ├── registration/
│   │   │   ├── login.html
│   │   │   ├── signup.html
│   │   │   ├── password_change_form.html
│   │   │   └── password_change_done.html
│   │   └── tracker/
│   │       ├── dashboard.html
│   │       ├── expense_list.html
│   │       ├── expense_form.html
│   │       ├── income_list.html
│   │       ├── income_form.html
│   │       ├── category_list.html
│   │       ├── category_form.html
│   │       ├── reports.html
│   │       ├── profile.html
│   │       └── confirm_delete.html
│   └── static/
│       ├── css/style.css
│       └── js/main.js
│
└── tracker/                ← Django app
    ├── models.py
    ├── views.py
    ├── urls.py
    ├── forms.py
    ├── admin.py
    └── apps.py
```

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔐 Auth | Register, Login, Logout, Change Password |
| 📊 Dashboard | Stats, Charts, Recent Transactions |
| 💰 Expenses | Add, Edit, Delete, Filter, Search, Paginate |
| 💵 Income | Add, Edit, Delete, Filter, Search |
| 📁 Categories | Custom + default categories with icons & colors |
| 📈 Reports | Monthly/Yearly charts, category breakdown |
| 👤 Profile | Edit info, avatar, budget, currency, theme |
| 🌙 Dark Mode | Smooth toggle, persistent via localStorage |
| 📱 Responsive | Mobile, tablet, desktop fully supported |

---

## 🎨 Tech Stack

- **Backend:** Django 4.2+ (Python)
- **Database:** SQLite (default)
- **Frontend:** HTML5, CSS3, Vanilla JS
- **Charts:** Chart.js 4.4
- **Icons:** FontAwesome 6.5
- **Fonts:** Plus Jakarta Sans + Syne (Google Fonts)

---

## 🔧 Customization

### Change Currency
Go to **Profile → Currency Symbol** and enter your preferred symbol (₹, $, €, £, etc.)

### Set Monthly Budget  
Go to **Profile → Monthly Budget** to enable budget tracking on the dashboard.

### Dark Mode
Click the 🌙 moon icon in the top navbar to toggle dark mode.

---

## 📦 Production Deployment

For production, update `settings.py`:
```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']
SECRET_KEY = 'your-very-secret-key-here'

# Use PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'spendwise_db',
        'USER': 'db_user',
        'PASSWORD': 'db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

Then run:
```bash
python manage.py collectstatic
pip install gunicorn psycopg2-binary
gunicorn spendwise.wsgi:application
```

---

## 👨‍💻 Author

**© 2026 Ganesh45 | All Rights Reserved**

---

## 🐛 Troubleshooting

**"No module named tracker"**
→ Make sure you're in the `spendwise_pro/` directory before running commands.

**"Table doesn't exist"**
→ Run `python manage.py makemigrations tracker && python manage.py migrate`

**Static files not loading**
→ Run `python manage.py collectstatic` or ensure `DEBUG=True` in development.
