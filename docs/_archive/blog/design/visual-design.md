# Visual Design Guide for ML DEVLOG

## Brand Identity

This document outlines the visual design elements, guidelines, and components for the ML DEVLOG tech blog. The design follows a futuristic, tech-oriented aesthetic with a focus on readability and visual appeal for technical content.

## Color Palette

### Primary Colors

| Name | Hex Code | Description | Usage |
|------|----------|-------------|-------|
| Background Dark | `#0a0a1a` | Deep space black | Main background |
| Cyan Accent | `#00f0ff` | Neon cyan | Primary accent, highlights, links |
| Purple Accent | `#7928ca` | Deep purple | Secondary accent, alternate highlights |
| Text Light | `#e5e5e5` | Off-white | Primary text color |
| Text Gray | `#aaaaaa` | Medium gray | Secondary text, metadata |

### Secondary Colors

| Name | Hex Code | Description | Usage |
|------|----------|-------------|-------|
| Dark Gray | `#121212` | Charcoal | Card backgrounds, containers |
| Medium Gray | `#1a1a1a` | Dark charcoal | Navigation, secondary elements |
| Code Background | `#1e1e1e` | VS Code dark | Code block backgrounds |
| Code Header | `#2a2a2a` | Lighter code bg | Code block headers |
| Terminal Red | `#ff5f56` | Terminal close button | Terminal UI elements |
| Terminal Yellow | `#ffbd2e` | Terminal minimize | Terminal UI elements |
| Terminal Green | `#27c93f` | Terminal maximize | Terminal UI elements |

### Syntax Highlighting Colors

| Name | Hex Code | Description |
|------|----------|-------------|
| Keyword | `#569cd6` | Blue for keywords |
| Function | `#dcdcaa` | Yellow-tan for functions |
| String | `#ce9178` | Coral for strings |
| Comment | `#6a9955` | Green for comments |
| Type | `#4ec9b0` | Teal for types |
| Normal Text | `#d4d4d4` | Light gray for general code |
| Control | `#c586c0` | Purple for control flow |

## Typography

### Fonts

| Font | Usage | Fallbacks |
|------|-------|-----------|
| `'Orbitron', sans-serif` | Headings, titles, logos | `'Rajdhani', 'Russo One', sans-serif` |
| `'JetBrains Mono', monospace` | Body text, code, navigation | `'Roboto Mono', 'Courier New', monospace` |

### Font Sizes

| Element | Size | Weight | Family |
|---------|------|--------|--------|
| Logo | 24px | 700 (Bold) | Orbitron |
| Main Heading (H1) | 28px | 700 (Bold) | Orbitron |
| Section Heading (H2) | 24px | 700 (Bold) | Orbitron |
| Card Title (H3) | 16px | 700 (Bold) | Orbitron |
| Body Text | 14px | 400 (Regular) | JetBrains Mono |
| Card Description | 11px | 400 (Regular) | JetBrains Mono |
| Metadata | 10px | 400 (Regular) | JetBrains Mono |
| Navigation | 12px | 400 (Regular) | JetBrains Mono |
| Code | 12px | 400 (Regular) | JetBrains Mono |

## Gradients & Effects

### Gradient Borders

```css
background: linear-gradient(90deg, #00f0ff, #7928ca);
```

### Holographic Gradient

```css
background: linear-gradient(45deg, #00f0ff 0%, #7928ca 25%, #00f0ff 50%, #7928ca 75%, #00f0ff 100%);
opacity: 0.05;
```

### Glow Effect

```css
filter: drop-shadow(0 0 5px rgba(0, 240, 255, 0.7));
```

### Matrix Background Pattern

A subtle pattern of binary numbers ("01010", "10101") with low opacity (0.1) using the cyan and purple accent colors.

## Components

### Navigation

- **Chip Style**: Rounded pills (border-radius: 15px)
- **Active State**: Cyan text color
- **Inactive State**: Light gray text
- **Hover Effect**: Subtle glow effect

### Cards

- **Border**: 1px gradient border
- **Border Radius**: 8px
- **Background**: #121212
- **Shadow**: None
- **Hover Effect**: Subtle scale transformation (1.02)

### Buttons & Interactive Elements

- **Primary Button**: Gradient background with white text
- **Secondary Button**: Dark background with gradient border
- **Hover State**: Glow effect

### Code Blocks

- **Background**: #1e1e1e (VS Code dark theme)
- **Border**: None
- **Border Radius**: 8px
- **Header**: #2a2a2a with terminal buttons
- **Syntax Highlighting**: VS Code-inspired color scheme

### Category Indicators

- **Shape**: Hexagonal
- **Border**: 2px solid accent color (cyan or purple)
- **Background**: Transparent
- **Text**: Two-letter abbreviation in accent color

### Tag Pills

- **Shape**: Rounded pills (border-radius: 11px)
- **Border**: 1px solid accent color
- **Background**: Transparent
- **Text**: Small text in accent color

## Layout Guidelines

### Spacing

- **Section Spacing**: 50px
- **Card Spacing**: 20px
- **Internal Padding**: 20px
- **Text Line Height**: 1.6

### Container Widths

- **Maximum Content Width**: 1200px
- **Card Width**: 330px
- **Featured Section Width**: 700px

### Responsive Breakpoints

- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

## Animation & Interaction

### Hover Effects

- **Links**: Color transition + subtle underline
- **Cards**: Slight scale (1.02) + glow
- **Buttons**: Increased glow + slight scale

### Micro-interactions

- **Navigation**: Subtle hover feedback
- **Code Blocks**: Syntax highlighting 
- **Category Hexagons**: Glow on hover

### Page Transitions

- **Page Load**: Fade in
- **Between Pages**: Slide transition

## Implementation Notes

### CSS Variables

```css
:root {
  --color-background: #0a0a1a;
  --color-cyan: #00f0ff;
  --color-purple: #7928ca;
  --color-text: #e5e5e5;
  --color-text-secondary: #aaaaaa;
  --color-card-bg: #121212;
  --color-nav-bg: #1a1a1a;
  --color-code-bg: #1e1e1e;
  --color-code-header: #2a2a2a;
  
  --font-heading: 'Orbitron', sans-serif;
  --font-body: 'JetBrains Mono', monospace;
  
  --border-radius-small: 8px;
  --border-radius-large: 15px;
  
  --transition-speed: 0.3s;
}
```

### Critical CSS

Priority styles to load first:
- Background color
- Typography
- Basic layout structure
- Navigation

### Accessibility Considerations

- Maintain text contrast ratio of at least 4.5:1
- Ensure interactive elements have visible focus states
- Include hover/focus states for all interactive elements
- Implement keyboard navigation for interactive components

## Component Examples

### Featured Post Section

```html
<div class="featured-post">
  <div class="featured-post__left">
    <div class="featured-badge">FEATURED POST</div>
    <h1 class="featured-title">From Compliance to Machine Learning</h1>
    <div class="featured-divider"></div>
    <p class="featured-description">
      My journey transitioning from compliance to AI/ML development,
      and how I built my first ML projects in 100 days...
    </p>
    <div class="featured-meta">
      <div class="author-avatar">SG</div>
      <span class="author-name">Sonni Gunnels</span>
      <span class="post-date">May 12, 2025</span>
    </div>
  </div>
  <div class="featured-post__right">
    <!-- Terminal-style code block -->
    <div class="code-block">
      <div class="code-header">
        <div class="terminal-button red"></div>
        <div class="terminal-button yellow"></div>
        <div class="terminal-button green"></div>
        <span class="filename">career_transition.py</span>
      </div>
      <div class="code-content">
        <!-- Syntax highlighted code -->
      </div>
    </div>
  </div>
</div>
```

### Blog Post Card

```html
<div class="post-card">
  <div class="post-image">
    <!-- Post image or icon -->
  </div>
  <div class="category-hex category-jn">JN</div>
  <h3 class="post-title">30-Day ML Transition Plan</h3>
  <p class="post-excerpt">
    A step-by-step approach to transitioning into 
    machine learning in just one month...
  </p>
  <div class="post-tags">
    <span class="tag tag-python">Python</span>
    <span class="tag tag-ml">ML/AI</span>
    <span class="tag tag-learning">Learning</span>
  </div>
  <div class="post-meta">
    <span class="post-date">MAY 10, 2025</span>
  </div>
  <div class="post-divider"></div>
  <a href="#" class="post-link">
    <span>ACCESS TRANSMISSION</span>
    <span class="arrow">→</span>
  </a>
</div>
```

### Category Section

```html
<section class="categories">
  <h2 class="section-title">Categories</h2>
  
  <div class="categories-list">
    <div class="category-hex category-ml">ML</div>
    <div class="category-hex category-py">PY</div>
    <div class="category-hex category-ds">DS</div>
    <div class="category-hex category-ai">AI</div>
    <div class="category-hex category-jn">JN</div>
  </div>
  
  <div class="search-bar">
    <input type="text" placeholder="Search articles...">
    <button class="search-button">⌕</button>
  </div>
</section>
```

## File Structure

```
styles/
├── base/
│   ├── _variables.scss
│   ├── _typography.scss
│   ├── _colors.scss
│   └── _animations.scss
├── components/
│   ├── _header.scss
│   ├── _post-card.scss
│   ├── _featured-post.scss
│   ├── _category-hexagon.scss
│   ├── _code-blocks.scss
│   └── _tags.scss
├── layouts/
│   ├── _blog-list.scss
│   ├── _blog-detail.scss
│   └── _responsive.scss
└── main.scss
```

## Imagery Guidelines

- **Style**: Minimalist, tech-oriented
- **Color Treatment**: Monochromatic with accent color highlights
- **Icons**: Simple, line-based icons
- **Code Snippets**: Clean, syntax-highlighted code examples
- **Diagrams**: Technical diagrams with grid backgrounds

This style guide serves as a reference for consistent implementation of the ML DEVLOG visual identity across all blog pages and components.

---
Last Updated: 5/12/2025