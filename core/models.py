from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
from django.utils import timezone
from django.db.models import Count, Avg, Sum, Q
from dateutil.relativedelta import relativedelta

from datetime import date, timedelta
from projects.models import SystemSkillGain, Technology, SystemModule, LearningMilestone
from blog.models import Post


class CorePage(models.Model):
    """Model for static pages like privacy policy, etc."""

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200)
    content = MarkdownxField()
    meta_description = models.CharField(
        max_length=160,
        help_text="SEO meta description")
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("core:page", args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def rendered_content(self):
        """Return content as rendered HTML."""
        return markdownify(self.content)


class Skill(models.Model):
    """Dev skills with proficiency values for visualization."""

    CATEGORY_CHOICES = (
        ("technical_concept", "Technical Concept"),
        ("methodology", "Methodology/Process"),
        ('soft_skill', 'Soft Skill'),
        ('domain_knowledge', 'Domain Knowledge'),
        ("other", "Other"),
    )

    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True, max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='technical_concept')
    description = models.TextField(blank=True)
    proficiency = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)],
        help_text="Skill level from 1-5"
    )
    icon = models.CharField(max_length=50, blank=True, help_text="Font Awesome icon name (e.g., fa-python)")
    color = models.CharField(max_length=7, default="#00f0ff", help_text="Hex color code")
    display_order = models.PositiveIntegerField(default=0)

    # Technology Relationship
    related_technology = models.OneToOneField('projects.Technology', on_delete=models.SET_NULL, null=True, blank=True, related_name='skill_profile', help_text="Link to corresponding technology in projects app")

    # Experience Tracking
    years_experience = models.FloatField(default=0.0, help_text="Years of experience with this skill")

    # Featured Status
    is_featured = models.BooleanField(default=False, help_text="Display prominently on homepage")

    # Recency Tracking
    last_used = models.DateField(null=True, blank=True, help_text="When skill last used professionally")

    # Learning Status
    is_currently_learning = models.BooleanField(default=False, help_text="Currently improving this skill")

    # Skill Validation
    is_certified = models.BooleanField(default=False, help_text="Have certification in this skill")

    # ===== New Skill -> Technology Relationship =====
    related_technologies = models.ManyToManyField(
        'projects.Technology',
        through='SkillTechnologyRelation',
        blank=True,
        related_name='related_skills',
        help_text='Technologies commonly used with this skill'
    )

    class Meta:
        ordering = ['category', 'display_order']

    def __str__(self):
        # Enhanced w mastery level
        mastery = self.get_mastery_level().title()
        system_count = self.get_systems_count()
        if system_count > 0:
            return f"{self.name} ({mastery} - {system_count} systems)"
        return f"{self.name} ({self.get_proficiency_percentage():.0f}%)"

    def get_absolute_url(self):
        return reverse("core:skill", args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_experience_level(self):
        """Return experiience level based on years"""
        if self.years_experience >= 5:
            return "Expert"
        elif self.years_experience >= 3:
            return "Advanced"
        elif self.years_experience >= 1:
            return "Intermediate"
        else:
            return "Beginner"

    def is_recent(self):
        """Check if skill was used recently (within 2 years)"""
        if not self.last_used:
            # Assume recent if no set date
            return True
        years_since = (date.today() - self.last_used).days / 365
        return years_since <= 2

    def get_proficiency_percentage(self):
        """Convert 1-5 scale to percentage"""
        return (self.proficiency / 5) * 100

    # ================= LEARNING-FOCUSED METHODS =================

    def get_learning_progression(self):
        """
        Get learning progression of this skill across projects/systems
        Shows how skill is developed over time
        """
        gains = SystemSkillGain.objects.filter(
            skill=self
        ).select_related('system').order_by('system__created_at')

        progression = []
        for gain in gains:
            progression.append({
                'system': gain.system.title,
                'system_slug': gain.system.slug,
                'date': gain.system.created_at,
                'proficiency_gained': gain.proficiency_gained,
                'proficiency_display': gain.get_proficiency_display_short(),
                'how_learned': gain.how_learned,
                'learning_stage': gain.system.get_learning_stage_display(),
                'color': gain.get_proficiency_color(),
            })
        return progression

    def get_systems_using_skill(self):
        """Get all systems where this skill was developed/used"""
        return SystemSkillGain.objects.filter(skill=self).select_related('system').order_by('-system__created_at')

    def get_systems_count(self):
        """Get count of systems using this skill"""
        return self.get_systems_using_skill().count()

    def get_latest_usage(self):
        """Get the most recent system that used this skill"""
        latest = self.get_systems_using_skill().first()
        return latest.system if latest else None

    def get_first_usage(self):
        """Get the first system that used this skill"""
        first = self.get_systems_using_skill().last()
        return first.system if first else None

    def get_skill_milestones(self):
        """Get learning milestones related to this skill"""
        return self.milestones.select_related('system').order_by('-date_achieved')

    def get_mastery_level(self):
        """
        Calculate mastery level based on project usage and proficiency
        Returns: beginner, intermediate, advanced, expert
        """
        system_count = self.get_systems_count()
        current_proficiency = self.proficiency

        # Mastery based on both usage frequency and proficiency level
        if system_count >= 5 and current_proficiency >= 4:
            return 'expert'
        elif system_count >= 3 and current_proficiency >= 3:
            return 'advanced'
        elif system_count >= 2 and current_proficiency >= 2:
            return 'intermediate'
        else:
            return 'beginner'

    def get_mastery_color(self):
        """Get color for mastery level"""
        mastery = self.get_mastery_level()
        colors = {
            "beginner": "#FFB74D",  # Orange
            "intermediate": "#81C784",  # Green
            "advanced": "#64B5F6",  # Blue
            "expert": "#FFD54F",  # Gold
        }
        return colors.get(mastery, "#81C784")

    def get_learning_velocity(self):
        """
        Calculate how quickly this skill was developed
        Projects/Systems using this skill per month
        """
        first_system = self.get_first_usage()
        latest_system = self.get_latest_usage()

        if not (first_system and latest_system):
            return 0

        # Calculate months between first and latest usage
        time_diff = latest_system.created_at - first_system.created_at
        months = max(time_diff.days / 30, 1)

        # Systems using this skill
        system_count = self.get_systems_count()

        return round(system_count / months, 2)

    def get_total_learning_time_estimate(self):
        """
        Estimate total time spent learning this skill across projects
        Based on actual_dev_hours in projects that used this skill
        """
        total_hours = 0

        for system_gain in self.get_systems_using_skill():
            system = system_gain.system
            if system.actual_dev_hours:
                # Assume skill was used for portion of project time
                # based on how many technologies were in the project
                tech_count = system.technologies.count()
                skill_portion = 1 / max(tech_count, 1)  # Divide time among technologies
                total_hours += system.actual_dev_hours * skill_portion
            elif system.estimated_dev_hours:
                # Fallback to estimated hours
                tech_count = system.technologies.count()
                skill_portion = 1 / max(tech_count, 1)
                total_hours += system.estimated_dev_hours * skill_portion

        return round(total_hours, 1)

    def has_breakthroughs(self):
        """Check if any systems/projects has breakthrough moments with this skill"""
        return self.get_systems_using_skill().exclude(how_learned__exact='').exists()

    def get_breakthrough_moments(self):
        """Get all breakthrough moments related to this skill"""
        breakthroughs = []

        for system_gain in self.get_systems_using_skill():
            if system_gain.how_learned:
                breakthroughs.append({
                    'system': system_gain.system.title,
                    'learning_story': system_gain.how_learned,
                    'date': system_gain.system.created_at,
                    'proficiency_gained': system_gain.get_proficiency_display_short(),
                })
        return breakthroughs

    def get_related_technologies(self):
        """
        Get technologies that were used alongside this skill
        Shows what this skill is commonly paired with
        """
        # Get all systems that used this skill
        systems_with_skill = [
            system_gain.system for system_gain in self.get_systems_using_skill()
        ]

        # Get technologies used in those systems
        related_techs = Technology.objects.filter(
            systems__in=systems_with_skill
        ).distinct().exclude(name=self.name)  # Exclude self if skill name matches tech name

        return related_techs

    def get_skill_summary_for_dashboard(self):
        """Get comprehensive skill summary for dashboard display"""
        return {
            'name': self.name,
            'category': self.get_category_display(),
            'proficiency': self.proficiency,
            'proficiency_percentage': self.get_proficiency_percentage(),
            'mastery_level': self.get_mastery_level(),
            'mastery_color': self.get_mastery_color(),
            'systems_count': self.get_systems_count(),
            'learning_velocity': self.get_learning_velocity(),
            'total_time_estimate': self.get_total_learning_time_estimate(),
            'has_milestones': self.get_skill_milestones().exists(),
            'is_featured': self.is_featured,
            'is_currently_learning': self.is_currently_learning,
            'years_experience': self.years_experience,
            'color': self.color,
            'icon': self.icon,
        }
    
    # ======================================
    # ENHANCED SKILL MODEL ADDITIONS
    # ======================================

    def get_learning_journey_summary(self):
        """Get comprehensive learning journey for this skill"""
        return {
            'name': self.name,
            'proficiency': self.proficiency,
            'mastery_level': self.get_mastery_level(),
            'systems_using': self.get_systems_count(),
            'education_sources': self.learned_through_education.count(),
            'first_learned': self.learned_through_education.order_by('education__start_date').first(),
            'learning_velocity': self.get_learning_velocity(),
            'recent_projects': [
                gain.system.title for gain in self.project_gains.order_by('-created_at')[:3]
            ],
            'learning_breakthroughs': self.get_breakthrough_moments()[:2],
        }

    def get_education_sources(self):
        """Get education sources where this skill was learned"""
        return self.learned_through_education.all()
    
    def get_project_application(self):
        """Get projects/systems where this skill was applied"""
        return [gain.system for gain in self.project_gains.all()]
    
    def get_learning_timeline_events(self):
        """Get chronological learning events for this skill"""
        events = []

        # Education events
        for edu in self.get_education_sources():
            events.append({
                'date': edu.start_date,
                'type': 'education_start',
                'title': f"Started learning in {edu.degree}",
                'source': edu.platform or edu.institution,
            })
            if edu.end_date:
                events.append({
                    'date': edu.end_date,
                    'type': 'education_complete',
                    'title': f"Completed {edu.degree}",
                    'source': edu.platform or edu.institution,
                })
        
        # Project applications
        for gain in self.project_gains.all():
            events.append({
                'date': gain.created_at.date(),
                'type': 'project_application',
                'title': f"Applied in {gain.system.title}",
                'proficiency': gain.get_proficiency_gained_display(),
            })
        
        # Sort chronologically
        events.sort(key=lambda x: x['date'])
        return events
    
    def get_mastery_progression_score(self):
        """Calculate mastery progression over time"""
        timeline = self.get_learning_timeline_events()
        if not timeline:
            return 0
        
        # Calculate progression based on timeline density and variety
        education_events = [e for e in timeline if 'education' in e['type']]
        project_events = [e for e in timeline if e['type'] == 'project_application']

        score = 0
        # Education foundation
        score += min(30, len(education_events) * 10)
        # Project/System Experience
        score += min(50, len(project_events) * 5)
        # Current proficiency
        score += min(20, self.proficiency * 4)

        return min(100, score)


class SkillTechnologyRelation(models.Model):
    """
    Through model for Skill ↔ Technology relationships
    Allows tracking strength of relationship and context
    """
    RELATIONSHIP_STRENGTH = [
        (1, 'Occasionally Used'),
        (2, 'Commonly Used'),
        (3, 'Essential Technology'),
        (4, 'Primary Implementation'),
    ]

    RELATIONSHIHP_TYPE = [
        ('implementation', 'Primary Implementation Tool'),
        ('supporting', 'Supporting Technology'),
        ('alternative', 'Alternative Implementation'),
        ('data_source', 'Data Source/Storage'),
        ('visualization', 'Visualization/Display'),
        ('deployment', 'Deployment/Infrastructure'),
    ]

    skill = models.ForeignKey('Skill', on_delete=models.CASCADE, related_name='technology_relations')
    technology = models.ForeignKey('projects.Technology', on_delete=models.CASCADE, related_name='skill_relations')

    # Relationship metadata
    strength = models.IntegerField(choices=RELATIONSHIP_STRENGTH, default=2, help_text='How essential is this technology for this skill?')
    relationship_type = models.CharField(max_length=20, choices=RELATIONSHIHP_TYPE, default='implementation')
    notes = models.TextField(blank=True, help_text='Context about how this technology relates to the skill')

    # Learning Context
    first_used_together = models.DateField(null=True, blank=True)
    last_used_together = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('skill', 'technology')
        verbose_name = "Skill-Technology Relation"
        verbose_name_plural = "Skill-Technology Relations"
    
    def __str__(self):
        return f"{self.skill.name} → {self.technology.name}"
    
    def get_strength_color(self):
        """Return color based on relationship strength"""
        colors = {
            1: '#6c757d',  # Gray - Occasional
            2: '#17a2b8',  # Teal - Common  
            3: '#28a745',  # Green - Essential
            4: '#007bff',  # Blue - Primary
        }
        return colors.get(self.strength, '#6c757d')


class Education(models.Model):
    """Enhanced Educational background with learning journey connections"""

    LEARNING_TYPE_CHOICES = [
        ('formal_degree', 'Formal Degree'),
        ('online_course', 'Online Course'),
        ('certification', 'Certification'),
        ('bootcamp', 'Bootcamp'),
        ('self_study', 'Self-Study'),
        ('workshop', 'Workshop'),
    ]

    # ========== BASIC INFO ==========
    institution = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=200)
    degree = models.CharField(max_length=100, help_text='Degree or course name')
    field_of_study = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    is_current = models.BooleanField(default=False)

    # ===== NEW LEARNING JOURNEY FIELDS =====

    learning_type = models.CharField(max_length=20, choices=LEARNING_TYPE_CHOICES, default='formal_degree')
    platform = models.CharField(max_length=100, blank=True, help_text="e.g., 'edX HarvardX', 'Udemy', 'University of Alabama'")
    certificate_url = models.URLField(blank=True, help_text='Link to certificate or completion proof')
    hours_completed = models.IntegerField(default=0, help_text="Total hours of instruction/study")
    
    # ========== SKILL CONNECTIONS ==========
    skills_learned = models.ManyToManyField(
        "Skill",
        through="EducationSkillDevelopment",
        related_name="learned_through_education",
        blank=True,
        help_text="Skills developed through this education",
    )

    # ========== PORTFOLIO INTEGRATION ==========

    related_systems = models.ManyToManyField(
        "projects.SystemModule",
        blank=True,
        related_name="education_background",
        help_text="Projects/Systems that applied knowledge from this education",
    )

    # ========== LEARNING METRICS ==========

    learning_intensity = models.IntegerField(
        choices=[(i, f'Level {i}') for i in range(1, 6)],
        default=3,
        help_text='Learning intensity/difficulty (1=Easy, 5=Very Intense)'
    )

    career_relevance = models.IntegerField(
        choices=[(i, f'{i} stars') for i in range(1, 6)],
        default=4,
        help_text='Relevance to software development career (1-5 stars)'
    )

    class Meta:
        ordering = ["-end_date", "-start_date"]
        verbose_name_plural = "Education"

    def __str__(self):
        return f"{self.degree} from {self.institution}"

    def get_absolute_url(self):
        return reverse("core:education", args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.degree} {self.institution}")
        super().save(*args, **kwargs)

    # ===== ENHANCED LEARNING JOURNEY METHODS =====

    def get_duration_months(self):
        """Calculate learning duration in months"""
        if not self.end_date or not self.start_date:
            return None
        return (self.end_date.year - self.start_date.year) * 12 + (self.end_date.month - self.start_date.month)
    
    def get_skills_gained_count(self):
        """Get count of skills learned"""
        return self.skills_learned.count()
    
    def get_projects_applied_count(self):
        """Get count of projects/systems that applied this education"""
        return self.related_systems.count()
    
    def get_learning_summary(self):
        """Get comprehensive learning summary"""
        return {
            'education_type': self.get_learning_type_display(),
            'platform': self.platform,
            'duration_months': self.get_duration_months(),
            'skills_gained': self.get_skills_gained_count(),
            'projects_applied': self.get_projects_applied_count(),
            'hours_completed': self.hours_completed,
            'career_relevance': self.career_relevance,
            'has_certificate': bool(self.certificate_url),
            'is_current': self.is_current,
        }


class EducationSkillDevelopment(models.Model):
    """Through model for Education ↔ Skill relationship w learning context"""

    LEARNING_FOCUS_CHOICES = [
        ('introduction', 'First Introduction'),
        ('foundation', 'Foundation Building'),
        ('practical', 'Practical Application'),
        ('advanced', 'Advanced Concepts'),
        ('mastery', 'Mastery Level'),
    ]
    
    IMPORTANCE_CHOICES = [
        (1, 'Minor Topic'),
        (2, 'Supporting Skill'),
        (3, 'Core Curriculum'),
        (4, 'Primary Focus'),
    ]

    education = models.ForeignKey(Education, on_delete=models.CASCADE)
    skill = models.ForeignKey('Skill', on_delete=models.CASCADE)

    # Learning progression in this education
    proficiency_before = models.IntegerField(
        choices=[(i, i) for i in range(0, 6)],
        default=0,
        help_text="Skill level before this course (0-5)"
    )

    proficiency_after = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)],
        default=1,
        help_text="Skill level after this course (1-5)",
    )

    # Learning context
    learning_focus = models.CharField(
        max_length=20,
        choices=LEARNING_FOCUS_CHOICES,
        default='foundation',
        help_text='Type of learning focus for this skill'
    )

    # Importance in course curriculum
    importance_level = models.IntegerField(
        choices=IMPORTANCE_CHOICES,
        default=3,
        help_text='How central was this skill to the course'
    )

    learning_notes = models.TextField(blank=True, help_text='Specific learning outcomes or notes')

    class Meta:
        unique_together = ('education', 'skill')
        verbose_name = 'Education Skill Development'
    
    def __str__(self):
        return f"{self.skill.name} in {self.education.degree}"
    
    def get_skill_improvement(self):
        """Calculate proficiency gained"""
        return self.proficiency_after - self.proficiency_before
    
    def get_improvement_color(self):
        """Color based on improvement level"""
        improvement = self.get_skill_improvement()
        if improvement >= 3:
            return "#4CAF50"  # Green - Major improvement
        elif improvement >= 2:
            return "#2196F3"  # Blue - Good improvement
        elif improvement >= 1:
            return "#FF9800"  # Orange - Some improvement
        else:
            return "#9E9E9E"  # Gray - Minimal improvement


class Experience(models.Model):
    """Work experience."""

    company = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=200)
    position = models.CharField(max_length=100)
    location = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    technologies = models.CharField(max_length=200, blank=True, help_text="Comma-separated list of technologies used")

    class Meta:
        ordering = ["-end_date", "-start_date"]

    def __str__(self):
        return f"{self.position} at {self.company}"

    def get_absolute_url(self):
        return reverse("core:experience", args=[self.slug])

    def get_technologies_list(self):
        """Return technologies as a list."""
        if self.technologies:
            return [tech.strip() for tech in self.technologies.split(",")]
        return []

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.position} {self.company}")
        super().save(*args, **kwargs)


class Contact(models.Model):
    """Model for contact form submissions."""

    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    # Tracking Metadata
    referrer_page = models.CharField(max_length=200, blank=True, help_text="Page the visitor came from")
    user_agent = models.TextField(blank=True, help_text="Browser/device info")
    ip_address = models.GenericIPAddressField(null=True, blank=True, help_text="Visitor IP address")

    # Response Tracking
    response_sent = models.BooleanField(default=False, help_text="Has response been sent")
    response_date = models.DateTimeField(null=True, blank=True, help_text="When response was sent")

    # Categorization
    inquiry_category = models.CharField(
        max_length=50,
        choices=[
            ('project', 'Project Inquiry'),
            ('hiring', 'Job/Hiring'),
            ('collaboration', 'Collaboration'),
            ('question', 'General Question'),
            ('feedback', 'Feedback'),
            ('other', 'Other'),
        ],
        default='other'
    )

    # Priority level
    priority = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low Priority'),
            ('normal', 'Normal Priority'),
            ('high', 'High Priority'),
            ('urgent', 'Urgent'),
        ],
        default='normal'
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Message from {self.name} - {self.created_at.strftime('%Y-%m-%d')}"

    def get_absolute_url(self):
        return reverse("core:contact_detail", args=[self.pk])

    def response_time_hours(self):
        """Calculate hours between submission and response"""
        if self.response_date and self.created_at:
            delta = self.response_date - self.created_at
            return delta.total_seconds() / 3600
        return None

    def mark_as_responded(self):
        """Mark contact as responded to"""
        self.response_sent = True
        self.response_date = timezone.now()
        self.save()


class SocialLink(models.Model):
    """Model for social media and external profile links."""

    CATEGORY_CHOICES = [
        ('professional', 'Professional & Coding-Centric'),
        ('community', 'Discussion & Community'),
        ('media', 'Media & Video'),
        ('chat', 'Messaging & Chat'),
        ('blog', 'Blogging & Content'),
        ('other', 'Other Socials')
    ]

    name = models.CharField(max_length=50)
    url = models.URLField()
    handle = models.CharField(max_length=100, blank=True)
    icon = models.CharField(
        max_length=50, blank=True, help_text="Font Awesome icon name (e.g., 'fa-github')"
    )
    display_order = models.PositiveIntegerField(default=0)

    # New SocialLink Category & Color
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    color = models.CharField(max_length=7, default="#60a5fa", help_text="Hex color for icon display (e.g., #00f0ff)")

    class Meta:
        ordering = ['display_order']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return self.url  # External URL, so just return the actual URL
    

class PortfolioAnalytics(models.Model):
    """
    Enhanced Portfolio Analytics with Learning Journey Focus
    Combines visitor metrics with learning progression tracking
    """
    # Date tracking
    date = models.DateField(unique=True)

    # ========== LEARNING JOURNEY METRICS ==========
    learning_hours_logged = models.FloatField(default=0.0, help_text='Hours spent learning/coding this day')
    datalog_entries_written = models.IntegerField(default=0, help_text='Learning documentation entries created')
    skills_practiced = models.IntegerField(default=0, help_text='Number of skills actively practiced')
    projects_worked_on = models.IntegerField(default=0, help_text='Number of projects/systems worked on')
    milestones_achieved = models.IntegerField(default=0, help_text='Learning milestones reached this day')

    # ========== VISITOR ENGAGEMENT METRICS ==========
    unique_visitors = models.IntegerField(default=0)
    page_views = models.IntegerField(default=0)

    # Content engagement metrics
    datalog_views = models.IntegerField(default=0)
    system_views = models.IntegerField(default=0)
    contact_form_submissions = models.IntegerField(default=0)
    github_clicks = models.IntegerField(default=0)
    resume_downloads = models.IntegerField(default=0)

    # ========== CONTENT PERFORMANCE ==========
    # Top performing content
    top_datalog = models.ForeignKey('blog.Post', null=True, blank=True, on_delete=models.SET_NULL, related_name='analytics_days_as_top')
    top_system = models.ForeignKey('projects.SystemModule', null=True, blank=True, on_delete=models.SET_NULL, related_name='analytics_days_as_top')

    # Geographic Data
    top_country = models.CharField(max_length=50, blank=True)
    top_city = models.CharField(max_length=50, blank=True)

    # ========== VISITOR CONTEXT ==========
    # Referrer Data
    top_referrer = models.CharField(max_length=200, blank=True)
    job_board_visits = models.IntegerField(default=0, help_text='Visits from job boards/career sites')
    bounce_rate = models.FloatField(default=0.0, help_text="Percentage of single-page sessions")
    avg_session_duration = models.IntegerField(default=0, help_text="Average session duration in seconds")
    organic_search_percentage = models.FloatField(default=0.0)

    class Meta:
        ordering = ['-date']
        verbose_name_plural = "Portfolio Analytics"

    def __str__(self):
        return f"Analytics for {self.date} ({self.unique_visitors} visitors, {self.learning_hours_logged}h learning)"

    def get_absolute_url(self):
        return reverse("core:analytics_detail", args=[self.date])

    def conversion_rate(self):
        """Calculate contact form conversion rate"""
        if self.unique_visitors > 0:
            return (self.contact_form_submissions / self.unique_visitors) * 100
        return 0.0

    def engagement_score(self):
        """Calculate overall engagement score"""
        base_score = 0
        if self.bounce_rate < 50:
            base_score += 25
        if self.avg_session_duration > 120:  # 2 minutes
            base_score += 25
        if self.datalog_views > self.page_views * 0.3:
            base_score += 25
        if self.contact_form_submissions > 0:
            base_score += 25
        return base_score

    # ========== ENHANCED LEARNING METHODS ==========

    def learning_engagement_score(self):
        """Calculate daily learning engagement (0-100)"""
        score = 0
        # 2+ hr learning
        if self.learning_hours_logged >= 2:
            score += 25
        # Documented learning
        if self.datalog_entries_written > 0:
            score += 25
        # Multiple skills practiced
        if self.skills_practiced >= 2:
            score += 25
        # Applied learning
        if self.projects_worked_on > 0:
            score += 25
        return score

    def hiring_interest_score(self):
        """Calculate hiring manager interest (0-100)"""
        if self.unique_visitors == 0:
            return 0
        
        score = 0
        if self.resume_downloads > 0:
            # Strong interest indicator
            score += 40
        if self.contact_form_submissions > 0:
            # Very strong interest
            score += 40
        if (self.datalog_views + self.system_views) >= self.unique_visitors:
            # Explored portfolio depth
            score += 20
        return min(100, score)
    
    @classmethod
    def get_learning_summary(cls, days=30):
        """Get learning summary for specified period"""
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)

        analytics = cls.objects.filter(date__range=[start_date, end_date])

        return {
            'total_learning_hours': analytics.aggregate(Sum('learning_hours_logged'))['learning_hours_logged__sum'] or 0,
            'total_entries_written': analytics.aggregate(Sum('datalog_entries_written'))['datalog_entries_written__sum'] or 0,
            'total_skills_practiced': analytics.aggregate(Sum('skills_practiced'))['skills_practiced__sum'] or 0,
            'total_projects_worked': analytics.aggregate(Sum('projects_worked_on'))['projects_worked_on__sum'] or 0,
            'total_milestones': analytics.aggregate(Sum('milestones_achieved'))['milestones_achieved__sum'] or 0,
            'avg_daily_hours': analytics.aggregate(Avg('learning_hours_logged'))['learning_hours_logged__avg'] or 0,
            'days_active': analytics.filter(learning_hours_logged__gt=0).count(),
            'consistency_rate': (analytics.filter(learning_hours_logged__gt=0).count() / days) * 100 if days > 0 else 0,
        }


# ======================================
# ENHANCED LEARNING JOURNEY MANAGER
# ======================================


class LearningJourneyManager:
    """
    Manager class for generating dynamic learning journey data
    Replaces hardcoded HomeView context with model-driven data
    """

    @staticmethod
    def get_journey_overview():
        """Get comprehensive learning journey overview"""

        # Find earliest learning date
        earliest_system = SystemModule.objects.filter(start_date__isnull=False).order_by('start_date').first()
        earliest_education = Education.objects.filter(learning_type__in=['online_course', 'certification']).order_by('start_date').first()

        start_date = None
        if earliest_system and earliest_education:
            start_date = min(earliest_system.start_date, earliest_education.start_date)
        elif earliest_system:
            start_date = earliest_system.start_date
        elif earliest_education:
            start_date = earliest_education.start_date
        
        if start_date:
            duration = relativedelta(date.today(), start_date)
            duration_text = f"{duration.years}+ Years" if duration.years > 0 else f"{duration.months} Months"
        else:
            duration_text = "2+ Years"  # Fallback
        
        return {
            'start_date': start_date.strftime("%B %Y") if start_date else "August 2022",
            'duration_years': duration_text,
            'courses_completed': Education.objects.filter(
                learning_type__in=['online_course', 'certification'],
                end_date__isnull=False
            ).count(),
            'learning_hours': PortfolioAnalytics.get_learning_summary(days=365)['total_learning_hours'],
            'certificates_earned': Education.objects.filter(certificate_url__isnull=False).exclude(certificate_url='').count(),
            'systems_built': SystemModule.objects.filter(status__in=['deployed', 'published']).count(),
            'skills_mastered': Skill.objects.filter(proficiency__gte=4).count(),
            'current_projects': SystemModule.objects.filter(status='in_development').count(),
        }
    
    @staticmethod
    def get_learning_highlights():
        """Generate learning highlights from Education model"""
        highlights = []

        # Get featured education entries
        education_entries = Education.objects.filter(
            learning_type__in=['online_course', 'certification'],
            career_relevance__gte=4
        ).order_by('-career_relevance', '-end_date')[:6]

        color_cycle = ["teal", "coral", "lavender", "mint", "yellow", "navy"]

        for i, edu in enumerate(education_entries):
            highlights.append({
                'title': edu.degree,
                'platform': edu.platform or edu.institution,
                'icon': 'fas fa-university' if edu.learning_type == 'formal_degree' else 'fas fa-certificate',
                'color': color_cycle[i % len(color_cycle)],
                'description': edu.description or f"Developed {edu.get_skills_gained_count()} technical skills",
                'badge': 'Completed' if edu.end_date else 'In Progress',
                'skills_count': edu.get_skills_gained_count(),
                'hours': edu.hours_completed,
                'certificate_url': edu.certificate_url,
            })
        
        return highlights

    @staticmethod
    def get_skill_progression():
        """Generate skill progression timeline"""

        # Get skills w progression data
        skills_with_gains = Skill.objects.filter(
            project_gains__isnull=False
        ).distinct().annotate(
            systems_count=Count('project_gains'),
            avg_proficiency=Avg('project_gains__proficiency_gained')
        ).order_by('-systems_count', '-avg_proficiency')[:8]

        progression = []
        for skill in skills_with_gains:
            skill_gains = SystemSkillGain.objects.filter(skill=skill).order_by('created_at')

            progression.append({
                'skill_name': skill.name,
                'category': skill.get_category_display(),
                'current_proficiency': skill.proficiency,
                'systems_using': skill.get_systems_count(),
                'learning_velocity': skill.get_learning_velocity(),
                'mastery_level': skill.get_mastery_level(),
                'color': skill.color,
                'icon': skill.icon,
                'timeline': [
                    {
                        'system': gain.system.title,
                        'proficiency_gained': gain.get_proficiency_gained_display(),
                        'date': gain.created_at,
                        'learning_context': gain.how_learned,
                    }
                    for gain in skill_gains[:3]  # Latest 3 gains
                ]
            })
        return progression
    
    @staticmethod
    def get_learning_timeline():
        """Generate chronological learning timeline"""
        timeline_events = []

        # Add education milestones
        for edu in Education.objects.filter(end_date__isnull=False).order_by('-end_date')[:5]:
            timeline_events.append({
                'date': edu.end_date,
                'type': 'education',
                'title': f"Completed {edu.degree}",
                'description': f"From {edu.platform or edu.institution}",
                'icon': 'fas fa-graduation_cap',
                'color': 'teal',
                'skills_gained': edu.get_skills_gained_count(),
            })
        
        # Add learning milestones
        for milestone in LearningMilestone.objects.order_by('-date_achieved')[:8]:
            timeline_events.append({
                'date': milestone.date_achieved.date(),
                'type': 'milestone',
                'title': milestone.title,
                'description': milestone.description[:100] + "..." if len(milestone.description) > 100 else milestone.description,
                'icon': 'fas fa-trophy' if milestone.milestone_type == 'breakthrough' else 'fas fa-star',
                'color': 'coral',
                'difficulty': milestone.difficulty_level,
                'confidence_boost': milestone.confidence_boost,
            })
        
        # Sort by date (most recent first)
        timeline_events.sort(key=lambda x: x['date'], reverse=True)

        return timeline_events[:10]
    
    @staticmethod
    def get_featured_systems():
        """Get featured projects/systems for learning showcase"""

        featured_systems = SystemModule.objects.filter(
            portfolio_ready=True,
            status__in=['deployed', 'published']
        ).select_related('system_type').prefetch_related('skills_developed')[:4]

        systems = []
        for system in featured_systems:
            learning_stats = system.get_development_stats_for_learning()

            systems.append({
                'title': system.title,
                'slug': system.slug,
                'description': system.excerpt,
                'learning_stage': system.get_learning_stage_display(),
                'skills_gained': system.get_skills_summary(),
                'complexity_score': learning_stats['complexity_score'],
                'portfolio_ready': system.portfolio_ready,
                'system_type': system.system_type.name if system.system_type else 'Project',
                'technologies': [tech.name for tech in system.technologies.all()[:4]],
                'learning_velocity': learning_stats['learning_velocity'],
                'completion_percent': learning_stats['completion_percent'],
            })
        return systems
