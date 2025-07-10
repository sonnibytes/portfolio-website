# AURA Portfolio Project
*Advanced User Repository & Archive - A tech-inspired Django portfolio*

![AURA Badge](https://img.shields.io/badge/AURA-Portfolio-cyan) ![Django](https://img.shields.io/badge/Django-4.2-green) ![Python](https://img.shields.io/badge/Python-3.11-blue)

## 🎯 Project Overview

AURA (Advanced User Repository & Archive) is a Django-based portfolio site with a futuristic HUD-themed aesthetic that showcases my Python development skills. The site features a modular architecture with three distinct Django applications working together to create a cohesive learning journey showcase.

### Key Features

- **Modern Tech Stack**: Built with Django, Python, CSS, and JavaScript
- **HUD-Inspired Design**: Futuristic interface with glass-morphism cards, data visualizations, and animated components
- **Learning Journey Focus**: Authentic metrics showing progression from beginner to advanced
- **Custom Admin System**: Professional content management interface
- **Responsive Design**: Mobile-first approach that works seamlessly across all devices

## 📁 Project Structure

```
portfolio-project/
├── static/                                # Global static files
│   ├── css/
│   │   ├── base.css                       # AURA core design system
│   │   └── components/                    # Reusable components
│   ├── js/
│   │   ├── base.js                        # AURA core JavaScript
│   │   └── components/                    # Component JS
│   └── images/                            # Global images, icons, assets
│
├── templates/                             # Global templates
│   ├── base.html                          # Root layout (AURA header/footer)
│   └── components/                        # Reusable template components
│
├── blog/                                  # DataLogs App (Blog)
│   ├── models.py                          # Post, Category, Tag, Series models
│   ├── views.py                           # DataLog views
│   ├── urls.py                            # DataLog URL routing
│   ├── admin.py                           # Admin integration
│   ├── templatetags/                      # Custom template tags
│   ├── templates/blog/                    # DataLog templates
│   └── static/blog/                       # DataLog-specific assets
│
├── projects/                              # Systems App (Projects)
│   ├── models.py                          # SystemModule, Technology models
│   ├── views.py                           # System views
│   ├── urls.py                            # System URL routing
│   ├── admin.py                           # Admin integration
│   ├── templatetags/                      # Custom template tags
│   ├── templates/projects/                # System templates
│   └── static/projects/                   # System-specific assets
│
├── core/                                  # Core App
│   ├── models.py                          # Shared models
│   ├── views.py                           # Main views (home, about, contact)
│   ├── urls.py                            # Main URL routing
│   ├── admin.py                           # Admin customization
│   ├── templatetags/                      # Global template tags
│   ├── templates/core/                    # Core templates
│   └── static/core/                       # Core-specific assets
│
├── manage.py                              # Django management script
├── portfolio/                             # Project settings package
│   ├── settings.py                        # Django settings
│   ├── urls.py                            # Root URL configuration
│   └── wsgi.py                            # WSGI configuration
└── requirements.txt                       # Project dependencies
```

## 🚀 Core Applications

### 1. DataLogs (blog)
The DataLogs app presents blog posts as technical log entries with a futuristic interface, documenting my learning journey and technical explorations.

**Key Features:**
- Technical writing organized by categories and series
- Code syntax highlighting
- Learning progression tracking
- Connection to project Systems

### 2. Systems (projects)
The Systems app showcases Python projects with an interactive dashboard interface and detailed technical information.

**Key Features:**
- Project portfolio with filterable grid
- System control interface with 8 specialized panels
- Technology stack visualization
- Performance metrics and timeline

### 3. Core
The Core app houses the main pages and shared functionality across the site.

**Key Features:**
- Home page with featured content
- About page with skills and learning journey
- Contact functionality
- Global navigation and shared components

## 🎨 Design System

AURA features a cohesive design system inspired by futuristic HUDs and interfaces:

### Color Palette
- **Primary**: Cyan (#00FFFF) - Main accent color
- **Background**: Dark Navy (#0A1929) - Base background
- **Container**: Gunmetal (#2A3B47) - Card backgrounds
- **Accent Colors**:
  - Lavender (#9D8EC7) - DataLogs theme
  - Coral (#FF7F50) - Technology theme
  - Mint (#98FB98) - Status indicators
  - Yellow (#FFD700) - Analytics elements

### UI Components
- **Glass Cards**: Semi-transparent containers with backdrop blur
- **HUD Elements**: Data-driven panels with borders and accent colors
- **Animations**: Loading sequences, hover effects, and transitions
- **Progress Indicators**: Dynamic bars and metrics

## 🛠️ Technologies

### Backend
- **Django 4.2**: Web framework
- **Python 3.11**: Programming language
- **SQLite/PostgreSQL**: Database

### Frontend
- **HTML5/CSS3**: Structure and styling
- **JavaScript**: Interactivity and animations
- **Chart.js**: Data visualizations
- **Custom CSS Components**: No external CSS frameworks

### Development Tools
- **Git**: Version control
- **VSCode**: Development environment
- **Django Debug Toolbar**: Performance optimization

## 📊 Learning Journey Focus

This portfolio is designed to showcase my authentic learning progression as a Python developer, rather than simulating enterprise experience. Key metrics highlight:

- **Educational Progress**: Courses completed, technologies learned
- **Project Development**: Complexity progression from beginner to advanced
- **Documentation**: Technical writing and problem-solving
- **Skill Development**: Competency growth across technologies

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- pip (Python package manager)
- Virtual environment tool (optional but recommended)

### Installation

1. Clone the repository
```bash
git clone https://github.com/your-username/portfolio-project.git
cd portfolio-project
```

2. Set up a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Run migrations
```bash
python manage.py migrate
```

5. Create a superuser
```bash
python manage.py createsuperuser
```

6. Run the development server
```bash
python manage.py runserver
```

7. Access the site at http://127.0.0.1:8000/

## 🔄 Custom Management Commands

The project includes several custom management commands to help with development and content generation:

```bash
# Generate sample DataLog entries
python manage.py generate_sample_logs

# Create test Systems with relationships
python manage.py create_test_systems

# Analyze technology usage across Systems
python manage.py analyze_tech_stack
```

## 🧪 Testing

Run the test suite with:

```bash
python manage.py test
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- Django documentation and community
- Chart.js for visualization capabilities
- The open-source community for inspiration and tools