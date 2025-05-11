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

## Technical Specification

### Data Models w Fields

**No need for Author or Comments models for this context*

#### Post Model
- title (char)
- excerpt (char) - for previews
- image (img) - for cards/header
- date (date) - created date
- slug (slug)
- content (text)
- tags (many-to-many) - FK
- category (one-to-many) - FK

#### Category Model
- name (char)
- slug (slug)

#### Tag Model
- caption (char)
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
- Later add "X minute read" feature?
- Translation feature

### Dependencies
Django
....

_____________________________

Last Updated: 5/10/2025

Document Status: In Progress...

