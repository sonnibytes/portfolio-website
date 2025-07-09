# Architecture Overview

This document explains how the AURA Portfolio project is organized at a high level, including Django apps, shared resources, data flow, and custom components.

---

## 🧱 App Overview

### 1. `core/` — Portfolio & Infrastructure

* Contains developer profile models, contact forms, homepage content, etc.
* Custom admin commands for maintenance, data sync, and analytics
* Context processors for global navigation and footer data
* Shared templates and static files for the site's layout

### 2. `blog/` — Technical Blog (DataLogs)

* Post, Tag, Category, Series, and SystemLogEntry models
* Feature-rich admin panel with custom views and forms
* Context-aware features using shared processors
* Complex template tag system (`datalog_tags.py`) for dynamic rendering
* Modular template includes (e.g. `post_card`, `terminal_code_display`)
* Static files scoped in `static/blog/`

### 3. `projects/` — Projects App (Systems)

* Manages project/system entries separate from blog posts
* Designed for showcasing build details, statuses, and metadata
* May include future integration with blog cross-references
* Contains its own templates and static assets
* Uses `models.py` to define project schemas
* Includes reusable components if `templatetags/` exist (to confirm)

---

## 🌐 Templates and Layout

Templates follow a layered inheritance model:

```
templates/
├── base.html                 # Master layout (global)
├── blog/datalogs_base.html  # Blog-specific layout
├── includes/                # Shared UI components
├── projects/systems_base.html # Projects-specific layout (if exists)
```

Each app has its own layout file where needed, with modular includes for consistent UI.

---

## 🎨 Static and Media Files

* Located in `static/` and `media/`
* Separated by app:

  * `static/blog/`
  * `static/core/`
  * `static/projects/`
* CSS/JS themed for a HUD-style look with category-based colors and glassmorphic elements

---

## 🧩 Custom Template Tags

### `blog/templatetags/datalog_tags.py`

* Terminal-style code blocks
* Category hexagons
* Timeline components
* Metadata panels

### `core/templatetags/` *(if present)*

* Custom reusable blocks for site-wide use (to confirm and document)

### `projects/templatetags/` *(if present)*

* Tags related to system/project cards, status icons, timelines, etc. (to confirm and document)

---

## 🧵 Context Processors

Defined in `core/context_processors.py`:

* Current year (footer)
* Global nav context (active tab, categories, etc)

If other apps provide context processors, they should be added to `settings.py` and documented per app.

---

## ⚙️ Admin Extensions

Custom admin enhancements include:

### In `core/`

* Admin views for contact management, profile updates, etc.
* Custom admin commands (e.g. deployment checks, data sync)

### In `blog/`

* Admin dashboards for managing posts, tags, categories, series
* Post preview, filtering, and dashboard overview

### In `projects/`

* Admin panels for managing system entries, status fields, and visual grouping (to confirm and expand)

---

Last Updated: 7/9/2025
