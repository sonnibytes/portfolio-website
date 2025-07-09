# Setup Instructions

Follow these steps to get the AURA Portfolio project running locally for development or testing.

---

## 📦 Prerequisites

* Python 3.11+
* pip
* virtualenv (recommended)
* Git
* A code editor like VS Code

---

## 🧰 Installation

1. **Clone the repository**

```bash
git clone https://github.com/ksg-dev/portfolio-website.git
cd portfolio-website
```

2. **Create and activate a virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install project dependencies**

```bash
pip install -r requirements.txt
```

---

## ⚙️ Environment Setup

1. **Create a `.env` file** at the root of the project with the following keys:

```dotenv
SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

Add additional variables as needed (e.g. `DATABASE_URL` for PostgreSQL).

2. **Set up the database**

```bash
python manage.py migrate
```

3. **Create a superuser** for admin access:

```bash
python manage.py createsuperuser
```

---

## 🚀 Running the Project

Start the Django development server:

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` to view the site.
Visit `http://127.0.0.1:8000/admin/` to log into the admin interface.

---

## 🧪 Testing (Optional)

If test scripts are included:

```bash
python manage.py test
```

---

Last Updated: 7/9/2025