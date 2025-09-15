"""
Core Admin URL Configuration
Main admin dashboard and global admin functionality
*NEW* Full CRUD Ops for Core Models
Version 4.0 - Add Core Models CRUD Ops
"""

from django.urls import path, include
from django.views.generic import TemplateView
from .admin_views import (
    MainAdminDashboardView,
    # Core Dashboard
    CoreAdminDashboardView,
    # Core Page Management
    CorePageListAdminView,
    CorePageCreateAdminView,
    CorePageUpdateAdminView,
    CorePageDeleteAdminView,
    # Skill Management
    SkillListAdminView,
    SkillCreateAdminView,
    SkillUpdateAdminView,
    SkillDeleteAdminView,
    SkillToggleFeaturedView,
    SkillToggleLearningView,
    # Education Management
    EducationListAdminView,
    EducationCreateAdminView,
    EducationUpdateAdminView,
    EducationDeleteAdminView,
    # Education-Skill Development Management
    EducationSkillListAdminView,
    EducationSkillCreateAdminView,
    EducationSkillUpdateAdminView,
    EducationSkillDeleteAdminView,
    # Experience Management
    ExperienceListAdminView,
    ExperienceCreateAdminView,
    ExperienceUpdateAdminView,
    ExperienceDeleteAdminView,
    # Contact Management
    ContactListAdminView,
    ContactCreateAdminView,
    ContactUpdateAdminView,
    ContactDeleteAdminView,
    ContactMarkReadView,
    ContactMarkResponseSentView,
    # Social Link Management
    SocialLinkListAdminView,
    SocialLinkCreateAdminView,
    SocialLinkUpdateAdminView,
    SocialLinkDeleteAdminView,
    # Portfolio Analytics Management
    PortfolioAnalyticsListAdminView,
    PortfolioAnalyticsCreateAdminView,
    PortfolioAnalyticsUpdateAdminView,
    PortfolioAnalyticsDeleteAdminView,
    AnalyticsChartDataView,
    # SkillTechnologyRelation Management
    SkillTechnologyRelationListAdminView,
    SkillTechnologyRelationCreateAdminView,
    SkillTechnologyRelationUpdateAdminView,
    SkillTechnologyRelationDeleteAdminView,

    test_admin_styles,

    # New Enhanced Views
    ProfessionalDevelopmentDashboardView,
    SkillDemonstrationView,
    SkillTechnologyMatrixView,
    EnhancedSkillCreateView,
    ProfessionalGrowthTimelineView,
    QuickSkillTechConnectionView
)

app_name = "admin"

urlpatterns = [
    # Main admin dashboard
    path("", MainAdminDashboardView.as_view(), name="dashboard"),

    # Core app-specific admin
    path("core/", CoreAdminDashboardView.as_view(), name="core_dashboard"),

    # Testing Styles
    path("test-admin/", test_admin_styles, name="test-admin"),
    
    # ===================
    # CORE PAGE MANAGEMENT
    # ===================
    
    path("pages/", CorePageListAdminView.as_view(), name="corepage_list"),
    path("pages/create/", CorePageCreateAdminView.as_view(), name="corepage_create"),
    path("pages/<int:pk>/edit/", CorePageUpdateAdminView.as_view(), name="corepage_update"),
    path("pages/<int:pk>/delete/", CorePageDeleteAdminView.as_view(), name="corepage_delete"),
    
    # ===================
    # SKILL MANAGEMENT
    # ===================
    
    path("skills/", SkillListAdminView.as_view(), name="skill_list"),
    path("skills/create/", SkillCreateAdminView.as_view(), name="skill_create"),
    path("skills/<int:pk>/edit/", SkillUpdateAdminView.as_view(), name="skill_update"),
    path("skills/<int:pk>/delete/", SkillDeleteAdminView.as_view(), name="skill_delete"),
    
    # Skill AJAX functionality
    path("skills/<int:pk>/toggle-featured/", SkillToggleFeaturedView.as_view(), name="skill_toggle_featured"),
    path("skills/<int:pk>/toggle-learning/", SkillToggleLearningView.as_view(), name="skill_toggle_learning"),
    
    # ===================
    # EDUCATION MANAGEMENT
    # ===================
    
    path("education/", EducationListAdminView.as_view(), name="education_list"),
    path("education/create/", EducationCreateAdminView.as_view(), name="education_create"),
    path("education/<int:pk>/edit/", EducationUpdateAdminView.as_view(), name="education_update"),
    path("education/<int:pk>/delete/", EducationDeleteAdminView.as_view(), name="education_delete"),
    
    # ===================
    # EDUCATION-SKILL DEVELOPMENT MANAGEMENT
    # ===================
    
    path("education-skills/", EducationSkillListAdminView.as_view(), name="education_skill_list"),
    path("education-skills/create/", EducationSkillCreateAdminView.as_view(), name="education_skill_create"),
    path("education-skills/<int:pk>/edit/", EducationSkillUpdateAdminView.as_view(), name="education_skill_update"),
    path("education-skills/<int:pk>/delete/", EducationSkillDeleteAdminView.as_view(), name="education_skill_delete"),
    
    # ===================
    # EXPERIENCE MANAGEMENT
    # ===================
    
    path("experience/", ExperienceListAdminView.as_view(), name="experience_list"),
    path("experience/create/", ExperienceCreateAdminView.as_view(), name="experience_create"),
    path("experience/<int:pk>/edit/", ExperienceUpdateAdminView.as_view(), name="experience_update"),
    path("experience/<int:pk>/delete/", ExperienceDeleteAdminView.as_view(), name="experience_delete"),
    
    # ===================
    # CONTACT MANAGEMENT
    # ===================
    
    path("contacts/", ContactListAdminView.as_view(), name="contact_list"),
    path("contacts/create/", ContactCreateAdminView.as_view(), name="contact_create"),
    path("contacts/<int:pk>/edit/", ContactUpdateAdminView.as_view(), name="contact_update"),
    path("contacts/<int:pk>/delete/", ContactDeleteAdminView.as_view(), name="contact_delete"),
    
    # Contact AJAX functionality
    path("contacts/<int:pk>/mark-read/", ContactMarkReadView.as_view(), name="contact_mark_read"),
    path("contacts/<int:pk>/mark-response-sent/", ContactMarkResponseSentView.as_view(), name="contact_mark_response_sent"),
    
    # ===================
    # SOCIAL LINK MANAGEMENT
    # ===================
    
    path("social-links/", SocialLinkListAdminView.as_view(), name="sociallink_list"),
    path("social-links/create/", SocialLinkCreateAdminView.as_view(), name="sociallink_create"),
    path("social-links/<int:pk>/edit/", SocialLinkUpdateAdminView.as_view(), name="sociallink_update"),
    path("social-links/<int:pk>/delete/", SocialLinkDeleteAdminView.as_view(), name="sociallink_delete"),
    
    # ===================
    # PORTFOLIO ANALYTICS MANAGEMENT
    # ===================
    
    path("analytics/", PortfolioAnalyticsListAdminView.as_view(), name="analytics_list"),
    path("analytics/create/", PortfolioAnalyticsCreateAdminView.as_view(), name="analytics_create"),
    path("analytics/<int:pk>/edit/", PortfolioAnalyticsUpdateAdminView.as_view(), name="analytics_update"),
    path("analytics/<int:pk>/delete/", PortfolioAnalyticsDeleteAdminView.as_view(), name="analytics_delete"),
    
    # Analytics AJAX functionality
    path("analytics/chart-data/", AnalyticsChartDataView.as_view(), name="analytics_chart_data"),

    # ===================
    # SKILL-TECHNOLOGY RELATIONSHIP MANAGEMENT
    # ===================

    path("skill-tech-relations/", SkillTechnologyRelationListAdminView.as_view(), name="skill_tech_relation_list"),
    path("skill-tech-relations/create/", SkillTechnologyRelationCreateAdminView.as_view(), name="skill_tech_relation_create"),
    path("skill-tech-relations/<int:pk>/edit/", SkillTechnologyRelationUpdateAdminView.as_view(), name="skill_tech_relation_update"),
    path("skill-tech-relations/<int:pk>/delete/", SkillTechnologyRelationDeleteAdminView.as_view(), name="skill_tech_relation_delete"),

    # ===================
    # EDUCATION-SKILL DEVELOPMENT MANAGEMENT
    # ===================

    path("education-skills/", EducationSkillListAdminView.as_view(), name="education_skill_list"),
    path("education-skills/create/", EducationSkillCreateAdminView.as_view(), name="education_skill_create"),
    path("education-skills/<int:pk>/edit/", EducationSkillUpdateAdminView.as_view(), name="education_skill_update"),
    path("education-skills/<int:pk>/delete/", EducationSkillDeleteAdminView.as_view(), name="education_skill_delete"),


    # ===================
    # NEW ENHANCEMENT VIEWS TO TEST
    # ===================
    path("professional-development/", ProfessionalDevelopmentDashboardView.as_view(), name="professional_dashboard"),
    path("skills/<int:pk>/demonstration/", SkillDemonstrationView.as_view(), name="skill_demonstration"),
    path("skills/matrix/", SkillTechnologyMatrixView.as_view(), name="skill_tech_matrix"),
    path("skills/create-enhanced/", EnhancedSkillCreateView.as_view(), name="skill_create_enhanced"),
    path("growth-timeline/", ProfessionalGrowthTimelineView.as_view(), name="growth_timeline"),

    # AJAX Endpoints
    path("api/quick-connection/", QuickSkillTechConnectionView.as_view(), name="quick_skill_tech_connection"),

    # ===================
    # APP ADMIN INCLUDES
    # ===================

    # Blog admin
    path("blog/", include("blog.admin_urls", namespace="blog")),
    # Projects/Systems admin
    path("projects/", include("projects.admin_urls", namespace="projects")),
]
