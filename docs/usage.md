# Usage Guide

This guide explains how to use the AURA Portfolio during development and as a viewer/administrator.

---

## 👩‍💻 For Developers

### Starting the Dev Server

```bash
python manage.py runserver
```

Visit the site at: [http://127.0.0.1:8000](http://127.0.0.1:8000)

Admin login: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

### Testing Features

* Use `python manage.py test` to run unit tests (if configured).
* Use custom admin commands to seed content or run diagnostics:

```bash
python manage.py create_learning_sample_data
python manage.py deployment_check
```

---

## 🧭 Navigating the Site

### Main Sections

* **Home**: Overview and introduction
* **Portfolio**: Interactive display of your dev experience and skills
* **Systems**: Projects (from the `projects` app)
* **DataLogs**: Blog-style technical logs and learning updates
* **Search**: Explore entries by keyword, category, or tag

### Special UI Features

* Category hexagons for fast filtering
* Terminal-style code output blocks
* Timeline view for logs and system events

---

## ⚙️ Admin Features

From `/admin/`, you can manage:

* Blog posts, categories, tags, and series (DataLogs)
* System/project entries (Systems)
* Developer profile and contact inquiries (Core)
* Upload media, configure navigation elements, and control feature visibility

Custom dashboards, forms, and inline elements improve the admin workflow.

### Aura Admin Interface

The admin interface is enhanced with a custom HUD-style design:

* Dashboard overview panels with post/system stats
* Tabbed admin pages for post creation and tag/category management
* Color-coded status indicators and category icons
* Interactive filtering and preview modes for DataLogs
* Modular design enables plug-and-play features for Systems or Core data

This custom admin improves the UX for both content creation and system maintenance.

---

## 💡 Tips

* Use draft mode and preview features in the admin to test layouts before publishing
* Track blog post activity via the `SystemLogEntry` model
* Projects can be linked to blog posts for deeper context (if configured)

---

Last Updated: 7/9/2025
