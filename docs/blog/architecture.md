# Blog Architecture Specification

## Overview
This document outlines the technical architecture for integrating a blog into the portfolio project.

## Research Summary

### Django Blog Implementation Options
1. **Integrated Approach**
   - Blog as a Django app within the portfolio project
   - Shared database and authentication
   - Unified deployment
   
2. **Separate Approach**
   - Blog as a standalone Django project
   - Separate deployment
   - API communication if needed

### Decision: Integrated Approach
Additional Pros:
Django framework allows for modular development, so scaling/adding/etc much more manageable longterm.

## Technical Specification

### Data Models w Fields

**No need for Author or Comments models for this context*

#### Post Model
- title (char)
- excerpt (char) - for previews
- thumbnail (img) - for cards
- banner_image (img) for banner
- status (char/select['draft' or 'published'])
- created (datetime) - created date
- updated (datetime) - updated date
- published_date (datetime) - published date
- slug (slug)
- content (markdownx field)
- featured (bool) for blog homepage
- featured_code (text) - code to display on featured terminal card
- show_toc (bool) - show table of contents on post page
- reading_time (pos int)
- tags (many-to-many) - FK
- category (one-to-many) - FK
- author (FK to built-in User)

#### Category Model
- name (char)
- slug (slug)
- code (char) -- two-letter code for hexagons
- description (text)

#### Tag Model
- name (char)
- slug (slug)


### URL Structure
`/blog/` - Blog Homepage <br>
`/blog/posts/` - All Posts <br>
`/blog/posts/<slug>/` - Individual Post <br>
`/blog/category/<slug>/` - Category Listing <br>
`/blog/tag/<slug>/` - Tag Listing


### Implementation Plan
Blog App Components:
- CRUD Ops for Posts
- Pre-defined Categories v Add by Post?
- DB handled by Django?
- Hosting?

Possible Thoughts for Later:
- Later add "X minute read" feature? Updated to include in initial model
- Translation feature

### Dependencies
Django
....

#### Potential Django Packages
Resources:
[Django Blog Packages Comparison](https://djangopackages.org/grids/g/blog/?csrfmiddlewaretoken=6uEpLfmIJgFGnE4xiBgzaJnBIHIHx5Xnua6KixFHAcrB00qnYr5RJ5kXkFize8Cs&python3=on&sort=score)

1. django-blog-zinnia: 
    - **Impression**: Sketchy...lots of dead links and securiguard file just for the demo seems like a red flag
    - demo wanted to install securiguard file? Malware?
2. Wagtail
    - **Impression**: Seems kind of heavy for my needs, option to integrate later if it feels necessary
    - Seems a popular choice
    - Nice admin interface
    - It's sitewide generally, with option to integrate into existing site
3. Mezzanine
    - **Impression**: Seems great but don't think it's still maintained, docs site is down and discussions last updated in mid-2024 commented on it not being maintained.
    - SEO-friendly urls and metadata
    - Save as draft and preview on site
    - Scheduled Publishing
    - In-line page editing
    - Don't think it's still maintained
4. DjangoCMS-Blog
    - **Impression**: 
    - Front-end editing
    - Multisite: posts can be visible in one or more django sites on the same project
5. Django-Cast
    - **Impression**: Good Option, but still more than I need right now.
    - Integration option
    - Targeted to podcasts and blog posts
    - Posts, comments models and more
    - pagination, thorough templating
    - Build w wagtail
    - Categories and Tags (Beta)

### Decision: Think can build custom for now.

Don't really need support for multiple authors, comments, reactions initially. Think I can start with a simpler custom setup and can always integrate something more complex if needed down the line.

_____________________________

Last Updated: 5/13/2025

Document Status: In Progress...

