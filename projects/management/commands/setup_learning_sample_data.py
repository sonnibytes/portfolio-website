# Create this as: projects/management/commands/setup_learning_sample_data.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from projects.models import (
    SystemModule,
    SystemSkillGain,
    LearningMilestone,
    Technology,
    SystemType,
)
from core.models import Skill
from blog.models import Post, Category
import random


class Command(BaseCommand):
    help = "Setup comprehensive sample data for learning-focused portfolio"

    def handle(self, *args, **options):
        self.stdout.write("🚀 Setting up learning portfolio sample data...")

        # Create or get skills
        self.create_skills()

        # Update existing systems with learning data
        self.enhance_existing_systems()

        # Create additional learning milestones
        self.create_learning_milestones()

        # Connect skills to systems
        self.connect_skills_to_systems()

        self.stdout.write(
            self.style.SUCCESS("✅ Learning portfolio sample data setup complete!")
        )
        self.show_summary()

    def create_skills(self):
        """Create comprehensive skills for learning tracking"""
        skills_data = [
            # Programming Languages
            {
                "name": "Python",
                "category": "languages",
                "proficiency": 4,
                "color": "#3776ab",
                "icon": "fab fa-python",
            },
            {
                "name": "JavaScript",
                "category": "languages",
                "proficiency": 3,
                "color": "#f7df1e",
                "icon": "fab fa-js",
            },
            {
                "name": "HTML/CSS",
                "category": "languages",
                "proficiency": 4,
                "color": "#e34f26",
                "icon": "fab fa-html5",
            },
            {
                "name": "SQL",
                "category": "languages",
                "proficiency": 3,
                "color": "#336791",
                "icon": "fas fa-database",
            },
            # Frameworks & Libraries
            {
                "name": "Django",
                "category": "frameworks",
                "proficiency": 4,
                "color": "#092e20",
                "icon": "fab fa-python",
            },
            {
                "name": "React",
                "category": "frameworks",
                "proficiency": 2,
                "color": "#61dafb",
                "icon": "fab fa-react",
            },
            {
                "name": "Bootstrap",
                "category": "frameworks",
                "proficiency": 3,
                "color": "#7952b3",
                "icon": "fab fa-bootstrap",
            },
            {
                "name": "Chart.js",
                "category": "frameworks",
                "proficiency": 2,
                "color": "#ff6384",
            },
            # Tools & Technologies
            {
                "name": "Git/GitHub",
                "category": "tools",
                "proficiency": 3,
                "color": "#f05032",
                "icon": "fab fa-git-alt",
            },
            {
                "name": "VS Code",
                "category": "tools",
                "proficiency": 4,
                "color": "#007acc",
            },
            {
                "name": "Docker",
                "category": "tools",
                "proficiency": 2,
                "color": "#2496ed",
                "icon": "fab fa-docker",
            },
            {
                "name": "Linux",
                "category": "tools",
                "proficiency": 2,
                "color": "#fcc624",
                "icon": "fab fa-linux",
            },
            # Databases
            {
                "name": "PostgreSQL",
                "category": "databases",
                "proficiency": 3,
                "color": "#336791",
            },
            {
                "name": "SQLite",
                "category": "databases",
                "proficiency": 3,
                "color": "#003b57",
            },
            # Other Skills
            {
                "name": "API Development",
                "category": "other",
                "proficiency": 3,
                "color": "#00d9ff",
            },
            {
                "name": "Responsive Design",
                "category": "other",
                "proficiency": 3,
                "color": "#ff6b6b",
            },
            {
                "name": "Database Design",
                "category": "other",
                "proficiency": 3,
                "color": "#4ecdc4",
            },
            {
                "name": "Problem Solving",
                "category": "other",
                "proficiency": 4,
                "color": "#45b7d1",
            },
            {
                "name": "Code Review",
                "category": "other",
                "proficiency": 2,
                "color": "#96ceb4",
            },
            {
                "name": "Testing",
                "category": "other",
                "proficiency": 2,
                "color": "#ffeaa7",
            },
        ]

        for skill_data in skills_data:
            skill, created = Skill.objects.get_or_create(
                name=skill_data["name"],
                defaults={
                    "category": skill_data["category"],
                    "proficiency": skill_data["proficiency"],
                    "color": skill_data["color"],
                    "icon": skill_data.get("icon", ""),
                    "is_featured": skill_data["proficiency"] >= 3,
                    "years_experience": skill_data["proficiency"]
                    * 0.5,  # Rough estimate
                    "is_currently_learning": skill_data["proficiency"] <= 3,
                },
            )
            if created:
                self.stdout.write(f"  ✅ Created skill: {skill.name}")

    def enhance_existing_systems(self):
        """Add learning data to existing systems"""
        systems = SystemModule.objects.all()

        learning_stages = ["tutorial", "guided", "independent", "refactoring"]

        for i, system in enumerate(systems):
            # Add learning stage
            system.learning_stage = learning_stages[i % len(learning_stages)]

            # Add GitHub metrics (simulate real data)
            system.commit_count = random.randint(10, 150)
            system.code_lines = random.randint(500, 5000)

            # Add time estimates
            if not system.estimated_dev_hours:
                system.estimated_dev_hours = random.randint(20, 100)
            if not system.actual_dev_hours:
                system.actual_dev_hours = system.estimated_dev_hours + random.randint(
                    -10, 30
                )

            # Set portfolio readiness
            system.portfolio_ready = i < 3  # First 3 systems are portfolio ready

            system.save()
            self.stdout.write(f"  📈 Enhanced system: {system.title}")

    def connect_skills_to_systems(self):
        """Connect skills to systems with learning context"""
        systems = SystemModule.objects.all()
        skills = Skill.objects.all()

        # Define skill mappings for different types of projects
        skill_mappings = {
            "portfolio": [
                "Django",
                "Python",
                "HTML/CSS",
                "JavaScript",
                "Bootstrap",
                "Responsive Design",
                "Git/GitHub",
            ],
            "blog": ["Django", "Python", "HTML/CSS", "Database Design", "PostgreSQL"],
            "iss": ["Python", "API Development", "HTML/CSS", "Problem Solving"],
            "bookstore": ["Django", "Python", "Database Design", "SQLite", "HTML/CSS"],
            "hangman": ["Python", "Problem Solving"],
            "snake": ["Python", "Problem Solving"],
        }

        for system in systems:
            # Determine skills based on project name/type
            project_skills = []
            system_name_lower = system.title.lower()

            for project_type, skill_names in skill_mappings.items():
                if project_type in system_name_lower:
                    project_skills = skill_names
                    break

            # Default skills if no match
            if not project_skills:
                project_skills = ["Python", "Problem Solving", "Git/GitHub"]

            # Add 2-5 skills per project
            skills_to_add = random.sample(
                project_skills, min(len(project_skills), random.randint(2, 5))
            )

            for skill_name in skills_to_add:
                try:
                    skill = Skill.objects.get(name=skill_name)

                    # Create skill gain with learning context
                    skill_gain, created = SystemSkillGain.objects.get_or_create(
                        system=system,
                        skill=skill,
                        defaults={
                            "proficiency_gained": random.randint(2, 4),
                            "how_learned": self.get_learning_context(system, skill),
                            "skill_level_before": random.randint(1, 2),
                            "skill_level_after": random.randint(3, 4),
                        },
                    )

                    if created:
                        self.stdout.write(
                            f"    🧠 Connected {skill.name} to {system.title}"
                        )

                except Skill.DoesNotExist:
                    continue

    def get_learning_context(self, system, skill):
        """Generate realistic learning context for skill gains"""
        contexts = {
            "Django": [
                "Built complete web application using Django framework",
                "Learned Django models, views, and templates",
                "Implemented user authentication and admin interface",
                "Created custom Django commands and middleware",
            ],
            "Python": [
                "Developed backend logic and data processing",
                "Implemented algorithms and data structures",
                "Built API endpoints and business logic",
                "Created utility functions and helper modules",
            ],
            "HTML/CSS": [
                "Designed responsive user interface",
                "Implemented modern CSS Grid and Flexbox layouts",
                "Created custom styling with SCSS",
                "Built mobile-first responsive design",
            ],
            "JavaScript": [
                "Added interactive features and animations",
                "Implemented real-time UI updates",
                "Created dynamic content loading",
                "Built client-side validation and UX enhancements",
            ],
            "API Development": [
                "Integrated external APIs for data fetching",
                "Built RESTful API endpoints",
                "Implemented API authentication and error handling",
                "Created data serialization and validation",
            ],
            "Database Design": [
                "Designed relational database schema",
                "Implemented complex queries and relationships",
                "Optimized database performance",
                "Created data migration scripts",
            ],
        }

        skill_contexts = contexts.get(
            skill.name,
            [
                f"Applied {skill.name} in {system.title} development",
                f"Gained practical experience with {skill.name}",
                f"Implemented {skill.name} features and functionality",
            ],
        )

        return random.choice(skill_contexts)

    def create_learning_milestones(self):
        """Create learning milestones for systems"""
        systems = SystemModule.objects.all()
        milestone_types = [
            "first_time",
            "breakthrough",
            "completion",
            "deployment",
            "debugging",
            "teaching",
        ]

        milestone_templates = {
            "first_time": {
                "titles": [
                    "First Django Project",
                    "First API Integration",
                    "First Database Design",
                    "First Responsive Website",
                    "First Python Script",
                ],
                "descriptions": [
                    "Successfully built my first web application using Django framework",
                    "Integrated external API for the first time and handled data processing",
                    "Designed my first relational database with proper relationships",
                    "Created my first mobile-responsive website design",
                    "Wrote my first Python script and saw it work perfectly",
                ],
            },
            "breakthrough": {
                "titles": [
                    "Finally Understood OOP",
                    "CSS Grid Click Moment",
                    "Django Models Breakthrough",
                    "JavaScript Async Understanding",
                    "Database Relationships Clarity",
                ],
                "descriptions": [
                    "Had a major breakthrough understanding object-oriented programming concepts",
                    "CSS Grid finally clicked and I could create complex layouts effortlessly",
                    "Django models and relationships suddenly made perfect sense",
                    "Asynchronous JavaScript and promises finally became clear",
                    "Database foreign keys and relationships clicked into place",
                ],
            },
            "completion": {
                "titles": [
                    "Project Successfully Completed",
                    "All Features Implemented",
                    "Portfolio Project Finished",
                    "Learning Goal Achieved",
                    "Complex Feature Completed",
                ],
                "descriptions": [
                    "Successfully completed all planned features and functionality",
                    "Implemented every feature on my original project roadmap",
                    "Finished building a complete portfolio-worthy project",
                    "Achieved my learning goals for this project",
                    "Completed the most complex feature I've built so far",
                ],
            },
            "deployment": {
                "titles": [
                    "First Successful Deployment",
                    "Production Environment Live",
                    "Public Demo Available",
                    "Live Website Launched",
                ],
                "descriptions": [
                    "Successfully deployed my first web application to production",
                    "Got the project running in a live production environment",
                    "Created a public demo that others can access and use",
                    "Launched my website and shared it with the world",
                ],
            },
            "debugging": {
                "titles": [
                    "Major Bug Finally Fixed",
                    "Complex Issue Resolved",
                    "Performance Problem Solved",
                    "Critical Error Debugged",
                ],
                "descriptions": [
                    "Spent hours debugging and finally solved a major issue",
                    "Resolved a complex problem that was blocking progress",
                    "Fixed performance issues and optimized the application",
                    "Successfully debugged and fixed a critical error",
                ],
            },
        }

        for i, system in enumerate(systems):
            # Create 1-3 milestones per system
            num_milestones = random.randint(1, 3)

            for j in range(num_milestones):
                milestone_type = milestone_types[j % len(milestone_types)]
                templates = milestone_templates.get(
                    milestone_type, milestone_templates["completion"]
                )

                # Create milestone with realistic date
                days_ago = random.randint(1, 365)
                milestone_date = timezone.now() - timedelta(days=days_ago)

                milestone = LearningMilestone.objects.create(
                    system=system,
                    milestone_type=milestone_type,
                    title=random.choice(templates["titles"]),
                    description=random.choice(templates["descriptions"]),
                    date_achieved=milestone_date,
                    difficulty_level=random.randint(2, 5),
                    confidence_boost=random.randint(3, 5),
                    shared_publicly=random.choice([True, False]),
                )

                self.stdout.write(f"    🏆 Created milestone: {milestone.title}")

    def show_summary(self):
        """Show summary of created data"""
        self.stdout.write("\n📊 Sample Data Summary:")
        self.stdout.write(f"  Skills: {Skill.objects.count()}")
        self.stdout.write(f"  Systems: {SystemModule.objects.count()}")
        self.stdout.write(f"  Skill Gains: {SystemSkillGain.objects.count()}")
        self.stdout.write(f"  Milestones: {LearningMilestone.objects.count()}")
        self.stdout.write(
            f"  Portfolio Ready: {SystemModule.objects.filter(portfolio_ready=True).count()}"
        )

        # Show learning stage distribution
        self.stdout.write("\n📈 Learning Stage Distribution:")
        from django.db.models import Count

        stages = SystemModule.objects.values("learning_stage").annotate(
            count=Count("id")
        )
        for stage in stages:
            stage_display = dict(SystemModule.LEARNING_STAGE_CHOICES).get(
                stage["learning_stage"]
            )
            self.stdout.write(f"  {stage_display}: {stage['count']}")

        self.stdout.write("\n🎯 Next Steps:")
        self.stdout.write(
            "  1. Visit /projects/learning/ to see the learning dashboard"
        )
        self.stdout.write("  2. Check individual system pages to see skill connections")
        self.stdout.write("  3. Review the Django admin to see all the new data")
        self.stdout.write("  4. Test the learning metrics and charts")
