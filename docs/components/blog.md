# Blog App Model Documentation

This document outlines the models used in the `blog` app (DataLogs) of the AURA Portfolio project.

---

## 📁 Models Overview

### `Category`

Used to organize posts into themed categories. Each category has a name, slug, code, description, color, and optional icon.

* **Important Fields**:

  * `name`, `slug`, `code`, `description`, `color`, `icon`

* **Important Methods**:

  * `get_absolute_url()`: Returns the category page URL.
  * `save()`: Auto-generates the slug if missing.

---

### `Tag`

Simple label model for flexible tagging of blog posts.

* **Important Fields**:

  * `name`, `slug`

* **Important Methods**:

  * `get_absolute_url()`: Returns tag page URL.
  * `save()`: Auto-generates the slug.

---

### `Post`

The primary model representing a blog post entry. Highly customizable and supports:

* Featured code block with syntax highlighting

* Relationships to category, tags, author, and related systems (via `SystemLogEntry`)

* Custom status control (draft/published)

* Markdown content rendering

* Dynamic reading time, slug, excerpt generation

* **Important Fields**:

  * `title`, `slug`, `author`, `content`, `excerpt`
  * `featured_code`, `featured_code_format`, `featured_image`
  * `category`, `tags`, `related_systems`
  * `status`, `published_date`, `reading_time`
  * `series`, `series_order`, `custom_icon`, `meta_description`, `meta_keywords`

* **Important Methods**:

  * `save()`: Handles slug creation, reading time, published date, excerpt generation
  * `rendered_content()`: Converts Markdown to HTML with heading anchors
  * `get_code_filename()`: Maps code block format to suggested filename
  * `get_icon_text()`: Returns emoji or code for category-based visual ID
  * `get_headings()`: Extracts H2/H3s for in-page TOC
  * `get_series()`, `get_primary_system()`, `get_similar_posts()`...

---

### `Comment`

Model for reader-submitted comments on posts. Includes basic moderation support with `approved` flag.

* **Important Fields**:

  * `post`, `name`, `email`, `body`, `created`, `approved`

---

### `PostView`

Tracks views of individual posts with IP address and timestamp. Prevents duplicate view counts.

* **Important Fields**:

  * `post`, `ip_address`, `timestamp`

* **Unique Constraint**: IP+Post combo

---

### `Series`

Organizes multiple blog posts into a themed series. Supports:

* Metadata and difficulty level

* Progress tracking

* Auto-updated metrics

* **Important Fields**:

  * `title`, `slug`, `description`, `difficulty_level`, `reading_time`, `post_count`

* **Important Methods**:

  * `update_metrics()`: Refresh post count and reading time
  * `get_next_post()` / `get_previous_post()`

---

### `SeriesPost`

Junction table linking posts to a `Series`, with a sortable order field.

* **Important Fields**:

  * `series`, `post`, `order`

---

### `SystemLogEntry`

Bridge model connecting blog posts with systems from the `projects` app.

Supports advanced metadata for HUD-style system tracking:

* Connection type, impact level, hours, status, icons, etc.

* **Important Fields**:

  * `post`, `system`, `log_id`, `connection_type`, `impact_level`, `hours_spent`
  * `status`, `system_status`, `status_icon`, `affected_components`, `created_at`, `updated_at`

* **Important Methods**:

  * `save()`: Auto-generates log ID and syncs post status
  * `get_status_color()`, `get_impact_color()`, `get_connection_icon()`
  * `get_affected_components_list()`

---

Last Updated: 7/10/2025