---

# AURA Portfolio

Welcome to the documentation for the **AURA Portfolio**, a high-tech, HUD-inspired Django project designed to showcase your development journey, skills, and projects.

---

## 📌 Overview

**Project Purpose:**
AURA is your personal developer portal, combining a dynamic blog, project archive, portfolio showcase, and analytics dashboard into one clean interface. It features:

* Modular Django app design
* Interactive and visually distinct templates (HUD-style)
* Custom template tags and filters
* Admin-enhanced content management
* SEO, responsive design, and search integration

---

## 🧰 Tech Stack

* **Backend:** Python 3.11, Django 4.x
* **Frontend:** Bootstrap, FontAwesome, Tailwind (optional)
* **Database:** SQLite (dev) / PostgreSQL (prod-ready)
* **Deployment Options:** Heroku, Render, Vercel (with static exports)
* **Others:**

  * Custom template tags
  * Django signals
  * Context processors
  * Admin command extensions

---

## 🗂️ Project Structure (Simplified)

```
portfolio-website/
├── blog/              # Blog app (Datalogs)
│   ├── templates/blog/
│   ├── static/blog/
│   └── templatetags/
├── core/              # Portfolio app
│   ├── templates/core/
│   ├── static/core/
│   └── management/commands/
├── systems/           # Projects app
│   ├── templates/systems/
│   ├── static/systems/
│   └── models.py
├── templates/         # Base shared templates
├── static/            # Shared CSS/JS
├── media/             # Uploaded images/media
├── manage.py
└── README.md
```

---

## 📚 Docs Navigation

* [Setup Instructions](setup.md)
* [Architecture Overview](architecture.md)
* [Usage Guide](usage.md)
* [Blog App (Datalogs)](components/blog.md)
* [Core App (Portfolio)](components/core.md)
* [Projects App (Systems)](components/systems.md)
* [Deployment Instructions](deployment.md)

---

Last Updated: 7/9/2025