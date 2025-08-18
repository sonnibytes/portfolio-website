# Core App

The **core** app provides the site-wide foundations that every other
app (Blog/DataLogs, Projects/Systems, etc.) builds on.

| Category                       | What it Handles                                               |
| ------------------------------ | ------------------------------------------------------------- |
| **Site pages**                 | Static content such as Privacy Policy or Terms via `CorePage` |
| **Developer profile**          | Skills, education, work history, social links                 |
| **Contact & outreach**         | Visitor messages, social links, résumé download               |
| **Analytics**                  | Daily learning + traffic metrics for dashboards               |
| **Learning Journey utilities** | High-level aggregations via `LearningJourneyManager`          |

---

## Main Models

| Model                                     | Purpose                                                                                     | Key Relationships                                   |
| ----------------------------------------- | ------------------------------------------------------------------------------------------- | --------------------------------------------------- |
| `CorePage`                                | Markdown-backed static pages with SEO meta                                                  | —                                                   |
| `Skill`                                   | One competency with category, proficiency (1-5) and rich helper methods (mastery %, trends) | 1-to-1 with `projects.Technology` (optional)        |
| `Education` + `EducationSkillDevelopment` | Formal/online learning records and the skills they add                                      | Many-to-many through table to **Skill**             |
| `Experience`                              | Work history with tech list                                                                 | —                                                   |
| `Contact`                                 | Form submissions + response tracking                                                        | —                                                   |
| `SocialLink`                              | External profile links for footer & header                                                  | —                                                   |
| `PortfolioAnalytics`                      | Per-day visitor metrics **plus** learning-hour metrics                                      | Links to top `blog.Post` or `projects.SystemModule` |

*(The full field-by-field detail for each model will live in
**********`docs/models/core/<ModelName>.md`********** later.)*

---

## Key Views / URLs

| View                   | URL name               | Highlights                                                                  |
| ---------------------- | ---------------------- | --------------------------------------------------------------------------- |
| `HomeView`             | `core:home`            | Dynamic dashboard cards (active systems, latest DataLogs, learning metrics) |
| `DeveloperProfileView` | `core:about`           | Groups skills by category, pulls education & experience for résumé page     |
| `ResumeDownloadView`   | `core:resume_download` | Serves static PDF or JSON résumé, fallback to “not implemented” notice      |

---

## Admin / Utilities

* Custom ordering on `Skill` & `SocialLink` (`display_order`).
* Queryset helpers inside `LearningJourneyManager` for quick
  “journey overview,” progression charts, featured systems, etc.

### Template Tags

The Core app includes several template‑tag modules that power HUD‑style helpers and reusable UI components across the entire project:

| Module               | Kind           | Highlights                                                                   |
| -------------------- | -------------- | ---------------------------------------------------------------------------- |
| `core_tags.py`       | Simple tags    | Navigation helpers (`active_nav`), badge generation, hex/star rating widgets |
| `aura_filters.py`    | Custom filters | Text/number formatters, color utilities, markdown shorthands                 |
| `aura_components.py` | Inclusion tags | Re‑usable HUD components like hex‑grid nav, stat badges, and layout panels   |

*Detailed reference for each tag and filter lives in `docs/templatetags/core/…`.*

---

### Cross-App Touch Points

* `Skill` links to `projects.Technology` for one-click drill-downs.
* `LearningJourneyManager` consumes **projects** (`SystemModule`,
  `LearningMilestone`) and **blog** (`Post`) data to produce combined
  dashboards.
