# core/management/commands/create_learning_sample_data.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Sum
from datetime import date, timedelta
import random

from core.models import (
    Education,
    Experience,
    Skill,
    PortfolioAnalytics,
    EducationSkillDevelopment,
)
from projects.models import SystemModule, LearningMilestone, Technology
from blog.models import Post


class Command(BaseCommand):
    help = "Create comprehensive learning journey sample data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear-existing",
            action="store_true",
            help="Clear existing sample data before creating new",
        )
        parser.add_argument(
            "--minimal",
            action="store_true",
            help="Create minimal dataset (faster for testing)",
        )

    def handle(self, *args, **options):
        if options["clear_existing"]:
            self.clear_existing_data()

        if options["minimal"]:
            self.create_minimal_dataset()
        else:
            self.create_comprehensive_dataset()

        self.stdout.write(
            self.style.SUCCESS("Learning journey sample data created successfully!")
        )

    def clear_existing_data(self):
        """Clear existing sample data"""
        self.stdout.write("Clearing existing sample data...")

        # Clear in dependency order
        EducationSkillDevelopment.objects.all().delete()
        Education.objects.all().delete()
        Experience.objects.all().delete()
        PortfolioAnalytics.objects.all().delete()

        self.stdout.write("Existing data cleared.")

    def create_minimal_dataset(self):
        """Create minimal dataset for quick testing"""
        self.stdout.write("Creating minimal learning dataset...")

        self.create_core_education(count=3)
        self.create_core_experience(count=2)
        self.create_education_skill_connections()
        self.create_sample_analytics(days=7)

    def create_comprehensive_dataset(self):
        """Create comprehensive realistic dataset"""
        self.stdout.write("Creating comprehensive learning dataset...")

        # Create education entries
        self.create_core_education()
        self.create_additional_courses()

        # Create experience entries
        self.create_core_experience()

        # Create relationships
        self.create_education_skill_connections()

        # Create learning milestones
        self.create_learning_milestones()

        # Create analytics data
        self.create_sample_analytics(days=90)

        # Display summary
        self.display_summary()

    def create_core_education(self, count=None):
        """Create core programming education entries"""
        self.stdout.write("Creating core education entries...")

        education_data = [
            {
                "degree": "CS50: Introduction to Computer Science",
                "institution": "Harvard University",
                "platform": "edX HarvardX",
                "field_of_study": "Computer Science",
                "learning_type": "online_course",
                "start_date": date(2022, 8, 15),
                "end_date": date(2022, 12, 10),
                "hours_completed": 100,
                "description": "Comprehensive introduction to computer science and programming. Covered algorithms, data structures, memory management, and multiple programming languages.",
                "certificate_url": "https://certificates.cs50.io/sample-certificate",
                "career_relevance": 5,
                "learning_intensity": 4,
            },
            {
                "degree": "100 Days of Code: Complete Python Pro Bootcamp",
                "institution": "Udemy",
                "platform": "Udemy",
                "field_of_study": "Python Programming",
                "learning_type": "online_course",
                "start_date": date(2023, 1, 10),
                "end_date": date(2023, 5, 20),
                "hours_completed": 120,
                "description": "Intensive Python programming bootcamp covering web development, data science, automation, and GUI development.",
                "certificate_url": "https://udemy.com/certificate/sample-python",
                "career_relevance": 5,
                "learning_intensity": 5,
            },
            {
                "degree": "Django for Beginners",
                "institution": "Django Software Foundation",
                "platform": "Official Documentation + Tutorial",
                "field_of_study": "Web Development",
                "learning_type": "self_study",
                "start_date": date(2023, 6, 1),
                "end_date": date(2023, 8, 15),
                "hours_completed": 80,
                "description": "Self-directed learning of Django web framework through official documentation, tutorials, and building practice projects.",
                "career_relevance": 5,
                "learning_intensity": 4,
            },
            {
                "degree": "JavaScript Algorithms and Data Structures",
                "institution": "freeCodeCamp",
                "platform": "freeCodeCamp",
                "field_of_study": "JavaScript Programming",
                "learning_type": "online_course",
                "start_date": date(2023, 9, 1),
                "end_date": date(2023, 11, 30),
                "hours_completed": 60,
                "description": "Comprehensive JavaScript course covering ES6, algorithms, data structures, and functional programming.",
                "certificate_url": "https://freecodecamp.org/certification/sample-js",
                "career_relevance": 4,
                "learning_intensity": 3,
            },
            {
                "degree": "Git and GitHub Complete Course",
                "institution": "GitHub",
                "platform": "GitHub Skills",
                "field_of_study": "Version Control",
                "learning_type": "online_course",
                "start_date": date(2023, 3, 1),
                "end_date": date(2023, 3, 15),
                "hours_completed": 20,
                "description": "Version control fundamentals, branching strategies, collaboration workflows, and GitHub Actions.",
                "certificate_url": "https://github.com/skills/sample-completion",
                "career_relevance": 5,
                "learning_intensity": 2,
            },
            {
                "degree": "LLM Engineering with Python",
                "institution": "Udemy",
                "platform": "Udemy",
                "field_of_study": "AI/Machine Learning",
                "learning_type": "online_course",
                "start_date": date(2024, 11, 1),
                "end_date": None,  # Currently taking
                "hours_completed": 25,
                "description": "Advanced course on Large Language Model engineering, prompt engineering, and AI application development.",
                "is_current": True,
                "career_relevance": 5,
                "learning_intensity": 4,
            },
        ]

        created_count = 0
        for edu_data in education_data:
            if count and created_count >= count:
                break

            education, created = Education.objects.get_or_create(
                degree=edu_data["degree"],
                institution=edu_data["institution"],
                defaults=edu_data,
            )

            if created:
                created_count += 1
                self.stdout.write(f"  Created: {education.degree}")

        self.stdout.write(f"Created {created_count} core education entries.")

    def create_additional_courses(self):
        """Create additional learning courses and certifications"""
        self.stdout.write("Creating additional courses...")

        additional_courses = [
            {
                "degree": "SQL for Data Science",
                "institution": "Coursera",
                "platform": "Coursera",
                "field_of_study": "Database Management",
                "learning_type": "online_course",
                "start_date": date(2023, 4, 1),
                "end_date": date(2023, 5, 15),
                "hours_completed": 40,
                "description": "Database fundamentals, SQL queries, joins, and data analysis techniques.",
                "certificate_url": "https://coursera.org/verify/sample-sql",
                "career_relevance": 4,
                "learning_intensity": 3,
            },
            {
                "degree": "Responsive Web Design",
                "institution": "freeCodeCamp",
                "platform": "freeCodeCamp",
                "field_of_study": "Web Design",
                "learning_type": "certification",
                "start_date": date(2023, 2, 1),
                "end_date": date(2023, 3, 30),
                "hours_completed": 35,
                "description": "HTML5, CSS3, responsive design principles, and accessibility standards.",
                "certificate_url": "https://freecodecamp.org/certification/sample-responsive",
                "career_relevance": 4,
                "learning_intensity": 3,
            },
            {
                "degree": "API Development with FastAPI",
                "institution": "Self-Study",
                "platform": "Documentation + YouTube",
                "field_of_study": "API Development",
                "learning_type": "self_study",
                "start_date": date(2024, 3, 1),
                "end_date": date(2024, 4, 20),
                "hours_completed": 30,
                "description": "Modern API development with FastAPI, automatic documentation, and async programming.",
                "career_relevance": 4,
                "learning_intensity": 3,
            },
        ]

        created_count = 0
        for course_data in additional_courses:
            education, created = Education.objects.get_or_create(
                degree=course_data["degree"],
                institution=course_data["institution"],
                defaults=course_data,
            )

            if created:
                created_count += 1
                self.stdout.write(f"  Created: {education.degree}")

        self.stdout.write(f"Created {created_count} additional courses.")

    def create_core_experience(self, count=None):
        """Create work experience entries"""
        self.stdout.write("Creating experience entries...")

        experience_data = [
            {
                "company": "Industrial Safety Solutions LLC",
                "position": "Environmental Health & Safety Specialist",
                "location": "Alabama, US",
                "start_date": date(2018, 6, 1),
                "end_date": date(2022, 7, 31),
                "description": """Led comprehensive EHS compliance programs for manufacturing facilities. 
                
**Key Responsibilities:**
• Developed and implemented safety protocols and environmental compliance programs
• Conducted risk assessments and regulatory audits across multiple facility locations
• Created data tracking systems for incident reporting and compliance metrics
• Trained staff on safety procedures and regulatory requirements
• Analyzed complex datasets to identify safety trends and improvement opportunities

**Technical Skills Developed:**
• Advanced Excel for data analysis and reporting
• Database management for compliance tracking
• Process documentation and systematic thinking
• Problem-solving and analytical reasoning
• Project management and cross-functional collaboration

**Transferable Skills to Software Development:**
• Analytical thinking and attention to detail
• Process optimization and systematic approach
• Data analysis and pattern recognition
• Documentation and technical writing
• Risk assessment and quality assurance mindset""",
                "is_current": False,
            },
            {
                "company": "Freelance/Personal Projects",
                "position": "Python Developer & Learning Journey",
                "location": "Remote",
                "start_date": date(2022, 8, 1),
                "end_date": None,
                "description": """Self-directed transition from EHS to software development through intensive learning and project development.

**Learning Approach:**
• Completed 500+ hours of structured programming courses
• Built 15+ personal projects demonstrating progressive skill development
• Maintained consistent learning schedule with daily coding practice
• Documented learning journey through technical blog posts and project documentation

**Technical Projects:**
• Portfolio website with Django backend and modern frontend
• Data analysis tools for personal project tracking
• Web scraping and automation scripts
• Database-driven applications with user authentication
• RESTful API development and integration

**Professional Development:**
• Developed strong problem-solving abilities through debugging complex issues
• Learned to work with modern development tools and workflows
• Built understanding of software architecture and design patterns
• Gained experience with version control, testing, and deployment practices

**Current Focus:**
• Advanced Python development and framework mastery
• Learning AI/ML engineering and LLM applications
• Building portfolio-ready applications for professional opportunities""",
                "is_current": True,
            },
            {
                "company": "Various Contract Projects",
                "position": "EHS Consultant",
                "location": "Alabama, US",
                "start_date": date(2020, 1, 1),
                "end_date": date(2022, 12, 31),
                "description": """Provided specialized EHS consulting services while transitioning to software development.

**Consulting Services:**
• Environmental compliance assessments for small to medium businesses
• Safety program development and implementation
• Regulatory training and staff development programs
• Incident investigation and root cause analysis

**Business & Technical Skills:**
• Client relationship management and technical communication
• Project planning and timeline management
• Rapid learning of new regulatory frameworks and industry standards
• Data collection, analysis, and reporting for compliance documentation

**Transition Period Highlights:**
• Maintained professional EHS work while learning programming
• Applied analytical skills from EHS work to software problem-solving
• Developed time management skills balancing consulting and learning
• Built foundation for career transition through consistent skill development""",
                "is_current": False,
            },
        ]

        created_count = 0
        for exp_data in experience_data:
            if count and created_count >= count:
                break

            experience, created = Experience.objects.get_or_create(
                company=exp_data["company"],
                position=exp_data["position"],
                defaults=exp_data,
            )

            if created:
                created_count += 1
                self.stdout.write(
                    f"  Created: {experience.position} at {experience.company}"
                )

        self.stdout.write(f"Created {created_count} experience entries.")

    def create_education_skill_connections(self):
        """Create EducationSkillDevelopment relationships"""
        self.stdout.write("Creating education-skill connections...")

        # Define skill connections for each course
        skill_connections = {
            "CS50: Introduction to Computer Science": [
                ("Python", 0, 3, "foundation", 4),
                ("Algorithms", 0, 3, "foundation", 4),
                ("Data Structures", 0, 2, "introduction", 3),
                ("C Programming", 0, 2, "introduction", 2),
                ("Problem Solving", 1, 4, "foundation", 4),
            ],
            "100 Days of Code: Complete Python Pro Bootcamp": [
                ("Python", 3, 5, "mastery", 4),
                ("Web Development", 0, 3, "foundation", 3),
                ("Django", 0, 2, "introduction", 2),
                ("Flask", 0, 3, "practical", 3),
                ("API Development", 0, 2, "introduction", 2),
                ("Data Science", 0, 2, "introduction", 2),
            ],
            "Django for Beginners": [
                ("Django", 2, 4, "practical", 4),
                ("Web Development", 3, 4, "advanced", 4),
                ("HTML/CSS", 2, 4, "practical", 3),
                ("Database Design", 1, 3, "foundation", 3),
                ("Python", 4, 5, "advanced", 3),
            ],
            "JavaScript Algorithms and Data Structures": [
                ("JavaScript", 0, 4, "foundation", 4),
                ("Algorithms", 2, 4, "practical", 4),
                ("Data Structures", 2, 4, "practical", 4),
                ("Problem Solving", 3, 4, "advanced", 3),
            ],
            "Git and GitHub Complete Course": [
                ("Git/GitHub", 0, 4, "practical", 4),
                ("Version Control", 0, 4, "foundation", 4),
                ("Collaboration", 1, 3, "practical", 3),
            ],
            "SQL for Data Science": [
                ("SQL", 0, 4, "practical", 4),
                ("Database Design", 2, 4, "practical", 3),
                ("Data Analysis", 1, 3, "foundation", 3),
            ],
            "Responsive Web Design": [
                ("HTML/CSS", 1, 4, "practical", 4),
                ("Web Development", 1, 3, "foundation", 3),
                ("UI/UX Design", 0, 2, "introduction", 2),
            ],
            "LLM Engineering with Python": [
                ("Python", 4, 5, "mastery", 3),
                ("AI/Machine Learning", 0, 3, "foundation", 4),
                ("API Development", 2, 4, "advanced", 3),
            ],
        }

        created_count = 0
        for education in Education.objects.all():
            if education.degree in skill_connections:
                for (
                    skill_name,
                    prof_before,
                    prof_after,
                    focus,
                    importance,
                ) in skill_connections[education.degree]:
                    try:
                        skill = Skill.objects.get(name=skill_name)
                        relationship, created = (
                            EducationSkillDevelopment.objects.get_or_create(
                                education=education,
                                skill=skill,
                                defaults={
                                    "proficiency_before": prof_before,
                                    "proficiency_after": prof_after,
                                    "learning_focus": focus,
                                    "importance_in_curriculum": importance,
                                    "learning_notes": f"Developed through {education.degree} coursework and projects.",
                                },
                            )
                        )

                        if created:
                            created_count += 1
                            self.stdout.write(
                                f"  Connected {skill_name} to {education.degree}"
                            )

                    except Skill.DoesNotExist:
                        self.stdout.write(
                            f"  Warning: Skill '{skill_name}' not found, skipping..."
                        )

        self.stdout.write(f"Created {created_count} education-skill connections.")

    def create_learning_milestones(self):
        """Create learning milestones for systems"""
        self.stdout.write("Creating learning milestones...")

        milestone_templates = [
            {
                "milestone_type": "first_time",
                "title": "First Successful Django Deployment",
                "description": "Successfully deployed first Django application to production using Heroku. Learned about environment variables, static file serving, and database configuration.",
                "difficulty_level": 4,
                "confidence_boost": 4,
                "days_ago": 180,
            },
            {
                "milestone_type": "breakthrough",
                "title": "Understanding Django ORM Relationships",
                "description": "Major breakthrough in understanding foreign keys, many-to-many relationships, and complex database queries. This unlocked advanced model design patterns.",
                "difficulty_level": 5,
                "confidence_boost": 5,
                "days_ago": 120,
            },
            {
                "milestone_type": "debugging",
                "title": "Solved Complex JavaScript Async Issue",
                "description": "Spent 3 days debugging a complex asynchronous JavaScript problem with API calls. Finally understood promises, async/await, and error handling.",
                "difficulty_level": 4,
                "confidence_boost": 4,
                "days_ago": 90,
            },
            {
                "milestone_type": "completion",
                "title": "Portfolio Website Launch",
                "description": "Completed and launched personal portfolio website with Django backend, custom admin system, and responsive frontend. First major full-stack project.",
                "difficulty_level": 4,
                "confidence_boost": 5,
                "days_ago": 60,
            },
            {
                "milestone_type": "teaching",
                "title": "Helped Fellow Learner with Python Problem",
                "description": "Successfully helped another developer solve a complex Python algorithm problem on a coding forum. Realized I could explain concepts clearly.",
                "difficulty_level": 3,
                "confidence_boost": 4,
                "days_ago": 30,
            },
        ]

        created_count = 0
        systems = list(SystemModule.objects.all())

        for i, milestone_data in enumerate(milestone_templates):
            if i < len(systems):
                system = systems[i]
                milestone_date = timezone.now() - timedelta(
                    days=milestone_data["days_ago"]
                )

                milestone, created = LearningMilestone.objects.get_or_create(
                    system=system,
                    title=milestone_data["title"],
                    defaults={
                        "milestone_type": milestone_data["milestone_type"],
                        "description": milestone_data["description"],
                        "date_achieved": milestone_date,
                        "difficulty_level": milestone_data["difficulty_level"],
                        "confidence_boost": milestone_data["confidence_boost"],
                    },
                )

                if created:
                    created_count += 1
                    self.stdout.write(f"  Created milestone: {milestone.title}")

        self.stdout.write(f"Created {created_count} learning milestones.")

    def create_sample_analytics(self, days=90):
        """Create sample portfolio analytics data"""
        self.stdout.write(f"Creating sample analytics for {days} days...")

        created_count = 0
        for i in range(days):
            analytics_date = date.today() - timedelta(days=i)

            # Skip if already exists
            if PortfolioAnalytics.objects.filter(date=analytics_date).exists():
                continue

            # Generate realistic learning data
            weekday = analytics_date.weekday()
            is_weekend = weekday in [5, 6]

            # More learning on weekends and early in journey
            base_hours = (
                random.uniform(2.0, 6.0) if is_weekend else random.uniform(1.0, 4.0)
            )

            # Adjust for learning progression (more hours earlier in journey)
            if i > 60:  # More intensive learning 60+ days ago
                base_hours *= 1.5

            # Some days have no learning (realistic)
            if random.random() < 0.15:  # 15% chance of no learning
                base_hours = 0

            skills_practiced = random.randint(1, 4) if base_hours > 0 else 0
            projects_worked = 1 if base_hours > 2 else 0
            entries_written = (
                1 if random.random() < 0.1 and base_hours > 0 else 0
            )  # 10% chance
            milestones = (
                1 if random.random() < 0.02 and base_hours > 0 else 0
            )  # 2% chance

            analytics = PortfolioAnalytics.objects.create(
                date=analytics_date,
                learning_hours_logged=round(base_hours, 1),
                datalog_entries_written=entries_written,
                skills_practiced=skills_practiced,
                projects_worked_on=projects_worked,
                milestones_achieved=milestones,
                # Visitor metrics (simulated)
                unique_visitors=random.randint(0, 15) if random.random() < 0.3 else 0,
                page_views=random.randint(0, 50) if random.random() < 0.3 else 0,
            )

            created_count += 1

        self.stdout.write(f"Created {created_count} analytics entries.")

    def display_summary(self):
        """Display summary of created data"""
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS("📊 SAMPLE DATA SUMMARY"))
        self.stdout.write("=" * 50)

        # Education summary
        education_count = Education.objects.count()
        courses_completed = Education.objects.filter(end_date__isnull=False).count()
        current_courses = Education.objects.filter(is_current=True).count()
        total_hours = (
            Education.objects.aggregate(total=Sum("hours_completed"))["total"] or 0
        )

        self.stdout.write(f"📚 Education: {education_count} entries")
        self.stdout.write(f"   - Completed: {courses_completed}")
        self.stdout.write(f"   - Current: {current_courses}")
        self.stdout.write(f"   - Total Hours: {total_hours}")

        # Experience summary
        experience_count = Experience.objects.count()
        self.stdout.write(f"💼 Experience: {experience_count} entries")

        # Skill connections
        skill_connections = EducationSkillDevelopment.objects.count()
        self.stdout.write(f"🔗 Education-Skill Connections: {skill_connections}")

        # Analytics summary
        analytics_count = PortfolioAnalytics.objects.count()
        total_learning_hours = (
            PortfolioAnalytics.objects.aggregate(total=Sum("learning_hours_logged"))[
                "total"
            ]
            or 0
        )

        self.stdout.write(f"📈 Analytics Entries: {analytics_count}")
        self.stdout.write(f"   - Total Learning Hours: {total_learning_hours:.1f}")

        # Milestones
        milestones_count = LearningMilestone.objects.count()
        self.stdout.write(f"🏆 Learning Milestones: {milestones_count}")

        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("🚀 Ready to test your dynamic learning journey!")
        self.stdout.write("Run: python manage.py generate_learning_analytics")
        self.stdout.write("=" * 50)
