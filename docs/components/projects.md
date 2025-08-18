# Projects App ("Systems")

The **projects** app—surfaced throughout the UI as **Systems**—is the heartbeat of the portfolio.  Each **System Module** encapsulates a project, micro‑service, or long‑running experiment and records everything from tech stack and features to learning impact and real‑time GitHub activity.

| Category                            | What it Handles                                                                                                                   |
| ----------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| **Project catalog**                 | CRUD records for every project you want to showcase (`SystemModule`)                                                              |
| **Technology stack**                | Canonical list of technologies with HUD icons & colors (`Technology`)                                                             |
| **Feature & gallery**               | Rich screenshots, architecture diagrams, feature chips (`SystemImage`, `SystemFeature`)                                           |
| **Learning impact**                 | Skill gains, milestones, portfolio readiness scores (`SystemSkillGain`, `LearningMilestone`)                                      |
| **Performance metrics**             | Uptime, response time, custom KPIs (`SystemMetric`)                                                                               |
| **GitHub metrics & code analytics** | Local mirror of repo metadata, weekly commit stats, language breakdown (`GitHubRepository`, `GitHubCommitWeek`, `GitHubLanguage`) |

---

## Main Models

| Model               | Purpose                                                                                       | Key Highlights / Relationships                                            |
| ------------------- | --------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| `Technology`        | Canonical tech‑stack item (language / framework / DB)                                         | Color & icon power HUD theming; M2M with `SystemModule`                   |
| `SystemType`        | High‑level category (API, ML, Web, IoT…)                                                      | Short `code` drives hex‑grid nav                                          |
| `SystemModule`      | **The** project record (status, complexity, metrics)                                          | Custom manager (`dashboard_stats`, etc.); links to tech, skills, GH repos |
| `SystemImage`       | Extra screenshots / diagrams                                                                  | Ordered gallery with alt‑text                                             |
| `SystemFeature`     | Individual feature chips with status (planned → tested)                                       | Visual badges via `get_status_color()`                                    |
| `SystemSkillGain`   | Through table linking **core.Skill** and `SystemModule`, recording proficiency deltas + notes | Drives learning velocity charts                                           |
| `LearningMilestone` | Stand‑alone “aha!” moments across projects                                                    | Timestamped, weighted for learning impact                                 |
| `SystemMetric`      | Operational & performance KPIs (uptime, error rate, throughput)                               | Displayed on dashboards and detail pages                                  |
| `GitHubRepository`  | Local cache of GitHub repo metadata & **summary commit stats**                                | FK to `SystemModule`; custom manager for sync scheduling                  |
| `GitHubCommitWeek`  | Weekly commit snapshots for deep analytics                                                    | FK to `GitHubRepository`; powers trend charts & velocity scores           |
| `GitHubLanguage`    | Breakdown of language usage (%) per repo                                                      | FK to `GitHubRepository`; future link to `Technology`                     |

*(Field‑by‑field detail lives under `docs/models/projects/<ModelName>.md`.)*

---

## GitHub Integration Workflow

1. **Repository sync** — management command hits the GitHub API, upserts `GitHubRepository`, toggles `enable_detailed_tracking` based on linkage to a System.
2. **Weekly stats job** — scheduled task fetches contribution graphs → populates `GitHubCommitWeek` with ISO week roll‑ups.
3. **Language snapshot** — on repo sync, `/languages` endpoint fills `GitHubLanguage` for colourful stack pies.
4. **System roll‑up** — `SystemModule.update_summary_from_weekly_data()` recalculates commit counts, averages & trends to feed HUD dashboards.

---

## Key Views / URLs

| URL                    | Purpose                                                             |
| ---------------------- | ------------------------------------------------------------------- |
| `/systems/`            | Filterable grid of all Systems (status, type, tech filters)         |
| `/systems/<slug>/`     | Detail page with features, metrics, GitHub charts, related DataLogs |
| `/technology/<slug>/`  | All systems using a given Technology                                |
| `/system-type/<slug>/` | All systems of a given SystemType                                   |

*Dashboard partials surface GitHub spark‑bars, commit trend badges, and learning metrics.*

---

## Cross‑App Touch Points

* `SystemSkillGain` links back to **core.Skill** for learning charts.
* `SystemModule` embeds related **blog.Post** entries via `SystemLogEntry` (in DataLogs app).
* GitHub commit data informs portfolio‑wide analytics panels surfaced on the **core** home dashboard.

---

Last Updated: 7/10/2025