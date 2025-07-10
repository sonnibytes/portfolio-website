# Inherited/Includes Styles and Templates

*AURA Streamlined Rework*

*Versions 2.0.1, 1.0.1*

## Global / Project-Level

### Base Refs
*base.html*

CSS:
- base.css
- components/hud-elements.css
- components/animations.css
- components/navigation.css

HTML: (only includes I could find...may need to include html components manually)
- components/breadcrumbs.html

JS:
- base.js
- components/navigation.js

---------------------------

### Admin Base Refs
*admin_base.html*

Extends > base.html

CSS:
- components/admin.css
- components/forms.css
- components/dashboard.css


JS:
- components/admin.js


--------------------------
## Blog / Datalogs

### Blog Base Refs
*datalogs_base.html*

Extends > base.html

CSS:
- (app-level) / datalogs.css
- (global) / components/dashboard.css
- (global) / components/forms.css

JS:
- (app-level) / datalogs.js


-----------------------

## Core

### Core Base Refs
*core_base.html*

Extends > base.html

CSS:
- (app-level) / core.css
- (global) / components/dashboard.css
- (global) / components/forms.css

JS:
- (app-level) / core.js


-------------------------

## Projects / Systems

### Systems Base Refs
*systems_base.html*

Extends > base.html

CSS:
- (app-level) / systems.css
- (global) / components/dashboard.css
- (global) / components/forms.css

JS:
- (app-level) / systems.js
- (global) / components/charts.js

---------------------------------
Last Updated: 5/23/2025

Doc Status: In Progress..
