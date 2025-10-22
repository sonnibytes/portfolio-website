# core/management/commands/import_foundation_data.py
"""
Django Management Command for Importing Level 1 Foundation Data from CSV
Usage: python manage.py import_foundation_data <model_name> <csv_file_path>
"""

import csv
import sys
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError, CommandParser
from django.core.exceptions import FieldError
from django.contrib.auth.models import User
from django.db import transaction
from django.utils.text import slugify
from django.utils import timezone

from core.models import Skill, CorePage, SocialLink, Contact
from projects.models import Technology, SystemType
from blog.models import Category, Tag, Series


class Command(BaseCommand):
    help = "Import Level 1 foundation data from CSV files"

    # Model mapping
    MODELS = {
        'skill': Skill,
        'skills': Skill,
        'corepage': CorePage,
        'corepages': CorePage,
        'sociallink': SocialLink,
        'sociallinks': SocialLink,
        'contact': Contact,
        'contacts': Contact,
        'technology': Technology,
        'technologies': Technology,
        'systemtype': SystemType,
        'systemtypes': SystemType,
        'category': Category,
        'categories': Category,
        'tag': Tag,
        'tags': Tag,
        'series': Series,
    }

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            'model',
            type=str,
            help='Model name to import (skill, technology, category, etc.)'
        )
        parser.add_argument(
            'csv_file',
            type=str,
            help='Path to CSV file'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Validate without actually importing'
        )
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing records instead of skipping them'
        )
    
    def handle(self, *args, **options):
        model_name = options['model'].lower()
        csv_file = options['csv_file']
        dry_run = options['dry_run']
        update_existing = options['update']

        # Validate model name
        if model_name not in self.MODELS:
            self.stdout.write(self.style.ERROR(
                f"Unknown model: {model_name}"
            ))
            self.stdout.write("Available models:")
            for key in sorted(set(self.MODELS.values()), key=lambda x: x.__name__):
                self.stdout.write(f"  - {key.__name__.lower()}")
            return
        
        model_class = self.MODELS[model_name]

        self.stdout.write(self.style.SUCCESS(
            f"\n{'='*60}\n"
            f"CSV IMPORT: {model_class.__name__}\n"
            f"{'='*60}"
        ))
        self.stdout.write(f"File: {csv_file}")
        self.stdout.write(f"Mode: {'DRY RUN' if dry_run else 'LIVE IMPORT'}")
        self.stdout.write(f"Update existing: {update_existing}\n")

        # Import based on model
        try:
            self.import_data(csv_file, dry_run, update_existing, model=model_class)
            # if model_class == Skill:
            #     self.import_skills(csv_file, dry_run, update_existing)
            # elif model_class == CorePage:
            #     self.import_corepages(csv_file, dry_run, update_existing)
            # elif model_class == SocialLink:
            #     self.import_sociallinks(csv_file, dry_run, update_existing)
            # elif model_class == Contact:
            #     self.import_contacts(csv_file, dry_run, update_existing)
            # elif model_class == Technology:
            #     self.import_technologies(csv_file, dry_run, update_existing)
            # elif model_class == SystemType:
            #     self.import_systemtypes(csv_file, dry_run, update_existing)
            # elif model_class == Category:
            #     self.import_categories(csv_file, dry_run, update_existing)
            # elif model_class == Tag:
            #     self.import_tags(csv_file, dry_run, update_existing)
            # elif model_class == Series:
            #     self.import_series(csv_file, dry_run, update_existing)
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\nERROR: {str(e)}"))
            raise
    
    def parse_boolean(self, value):
        """Convert various bool representations to Python bool"""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            value = value.strip().upper()
            if value in ['TRUE', '1', 'YES', 'Y']:
                return True
            if value in ['FALSE', '0', 'NO', 'N', '']:
                return False
        return False
    
    def parse_date(self, value):
        """Parse date string to date object"""
        if not value or value.strip() == '':
            return None
        try:
            return datetime.strptime(value.strip(), '%Y-%m-%d').date()
        except ValueError:
            try:
                return datetime.strptime(value.strip(), '%m/%d/%Y').date()
            except ValueError:
                self.stdout.write(self.style.WARNING(
                    f"Could not parse date: {value}, skipping"
                ))
                return None
    
    def parse_float(self, value, default=0.0):
        """Parse float with fallback"""
        if not value or value.strip() == '':
            return default
        try:
            return float(value.strip())
        except ValueError:
            return default
        
    def parse_int(self, value, default =0):
        """Parse int w fallback"""
        if not value or value.strip() == '':
            return default
        try:
            return int(value.strip())
        except ValueError:
            return default
    

    def import_data(self, csv_file, dry_run, update_existing, model):
        """Import data from CSV"""
        created_count = 0
        updated_count = 0
        skipped_count = 0
        error_count = 0

        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row_num, row in enumerate(reader, start=2):
                try:
                    name = row.get('name', '').strip()

                    if not name:
                        name = row.get('title', '').strip()

                    if not name:
                        self.stdout.write(self.style.WARNING(
                            f"Row {row_num}: Skipping - no name provided: {name}"
                        ))
                        skipped_count += 1
                        continue

                    if 'Category' in str(model):
                        code = row.get('code', '').strip()

                        if not code:
                            self.stdout.write(self.style.WARNING(
                                f"Row {row_num}: Skipping - code required"
                            ))
                            skipped_count += 1
                            continue

                    if 'SocialLink' in str(model):
                        url = row.get('url', '').strip()

                        if not url:
                            self.stdout.write(self.style.WARNING(
                                f"Row {row_num}: Skipping - url required"
                            ))
                            skipped_count += 1
                            continue
                    
                    if 'Contact' in str(model):
                        email = row.get('email', '').strip()

                        if not email:
                            self.stdout.write(self.style.WARNING(
                                f"Row {row_num}: Skipping - email required"
                            ))
                            skipped_count += 1
                            continue

                    # Check if exists - special treatment for social links (no slug)
                    try:
                        slug = row.get('slug', '').strip() or slugify(name)
                        existing = model.objects.filter(slug=slug).first()
                    except FieldError:
                        existing = model.objects.filter(name=name).first()

                    if existing and not update_existing:
                        self.stdout.write(self.style.WARNING(
                            f"Row {row_num}: {model} '{name}' already exists, skipping"
                        ))
                        skipped_count += 1
                        continue

                    # Prepare Data
                    if 'Skill' in str(model):
                        data = self.prep_skills(row, name, slug)
                    elif 'Technology' in str(model):
                        data = self.prep_technologies(row, name, slug)
                    elif 'Category' in str(model):
                        data = self.prep_categories(row, name, code, slug)
                    elif 'Tag' in str(model):
                        data = self.prep_tags(name, slug)
                    elif 'Series' in str(model):
                        data = self.prep_series(row, name, slug)
                    elif 'SystemType' in str(model):
                        data = self.prep_systemtypes(row, name, slug)
                    elif 'CorePage' in str(model):
                        data = self.prep_corepages(row, name, slug)
                    elif 'SocialLink' in str(model):
                        data = self.prep_sociallinks(row, name, url)
                    elif 'Contact' in str(model):
                        data = self.prep_contacts(row, name, email)
                    

                    if dry_run:
                        self.stdout.write(self.style.SUCCESS(
                            f"Row {row_num}: Would {'update' if existing else 'create'} {model}: {name}"
                        ))
                        if existing:
                            updated_count += 1
                        else:
                            created_count += 1
                    else:
                        if existing:
                            for key, value in data.items():
                                setattr(existing, key, value)
                            existing.save()
                            self.stdout.write(self.style.SUCCESS(
                                f"Row {row_num}: Updated {model}: {name}"
                            ))
                            updated_count += 1
                        else:
                            model.objects.create(**data)
                            self.stdout.write(self.style.SUCCESS(
                                f"Row {row_num}: Created {model}: {name}"
                            ))
                            created_count += 1
                
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f"Row {row_num}: Error processing {row.get('name', 'unknown')}: {str(e)}"
                    ))
                    error_count += 1

        self.print_summary(model, created_count, updated_count, skipped_count, error_count)
    
    
    def prep_skills(self, row, name, slug):
        """Skill-specific data prep"""
        
        # Prepare data
        skill_data = {
            'name': name,
            'slug': slug,
            'category': row.get('category', 'technical_concept').strip(),
            'description': row.get('description', '').strip(),
            'proficiency': self.parse_int(row.get('proficiency', '1'), 1),
            'icon': row.get('icon', '').strip(),
            'color': row.get('color', '#00f0ff').strip(),
            'display_order': self.parse_int(row.get('display_order', '0')),
            'years_experience': self.parse_float(row.get('years_experience', '0')),
            'is_featured': self.parse_boolean(row.get('is_featured', 'FALSE')),
            'last_used': self.parse_date(row.get('last_used', '')),
            'is_currently_learning': self.parse_boolean(row.get('is_currently_learning', 'FALSE')),
            'is_certified': self.parse_boolean(row.get('is_certified', 'FALSE')),
        }

        return skill_data  
    
    def prep_technologies(self, row, name, slug):
        """Technology-specific data prep"""

        tech_data = {
            'name': name,
            'slug': slug,
            'description': row.get('description', '').strip(),
            'category': row.get('category', 'other').strip(),
            'icon': row.get('icon', '').strip(),
            'color': row.get('color', '#00f0ff').strip(),
        }

        return tech_data
    
    def prep_categories(self, row, name, code, slug):
        """Category-specific data prep"""

        cat_data = {
            'name': name,
            'slug': slug,
            'code': code.upper()[:2],
            'description': row.get('description', '').strip(),
            'color': row.get('color', '#00f0ff').strip(),
            'icon': row.get('icon', '').strip(),
        }

        return cat_data
    
    def prep_tags(self, name, slug):
        """Tag-specific data prep"""

        tag_data = {
            'name': name,
            'slug': slug,
        }

        return tag_data
    
    def prep_series(self, row, name, slug):
        """Series-specific data prep"""

        series_data = {
            'title': name,
            'slug': slug,
            'description': row.get('description', '').strip(),
            'difficulty_level': row.get('difficulty_level', 'intermediate').strip(),
            'is_complete': self.parse_boolean(row.get('is_complete', 'FALSE')),
            'is_featured': self.parse_boolean(row.get('is_featured', 'FALSE')),
        }

        return series_data
    
    def prep_systemtypes(self, row, name, slug):
        """System Type-specific data prep"""

        type_data = {
            'name': name,
            'slug': slug,
            'description': row.get('description', '').strip(),
            'icon': row.get('icon', '').strip(),
            'color': row.get('color', '#00f0ff').strip(),
            'display_order': self.parse_int(row.get('display_order', '0')),
        }

        return type_data
    
    def prep_sociallinks(self, row, name, url):
        """SocialLink-specific data prep"""

        links = {
            'name': name,
            'url': url,
            'handle': row.get('handle', '').strip(),
            'icon': row.get('icon', '').strip(),
            'display_order': self.parse_int(row.get('display_order', '0')),
            'category': row.get('category', 'other').strip(),
            'color': row.get('color', '#60a5fa').strip(),
        }

        return links
    
    def prep_corepages(self, row, name, slug):
        """CorePage-specific data prep"""

        page = {
            'title': name,
            'slug': slug,
            'content': row.get('content', '').strip(),
            'meta_description': row.get('meta_desccription', '')[:160].strip(),
            'is_published': self.parse_boolean(row.get('is_published', 'TRUE')),
        }

        return page
    
    def prep_contacts(self, row, name, email):
        """Contact-specific data prep"""

        contact = {
            'name': name,
            'email': email,
            'subject': row.get('subject', '').strip(),
            'message': row.get('message', '').strip(),
            'inquiry_category': row.get('inquiry_category', 'other').strip(),
            'priority': row.get('priority', 'normal').strip(),
            'is_read': self.parse_boolean(row.get('is_read', 'FALSE')),
            'response_sent': self.parse_boolean(row.get('response_sent', 'FALSE')),
        }

        return contact

    def print_summary(self, model, created, updated, skipped, errors):
        """Print import summary"""
        self.stdout.write(self.style.SUCCESS(
            f"\n{'='*60}\n"
            f"IMPORT SUMMARY\n"
            f"MODEL: {model}\n"
            f"{'='*60}"
        ))
        self.stdout.write(f"Created: {created}")
        self.stdout.write(f"Updated: {updated}")
        self.stdout.write(f"Skipped: {skipped}")
        if errors > 0:
            self.stdout.write(self.style.ERROR(f"Errors: {errors}"))
        else:
            self.stdout.write(f"Errors: {errors}")
        self.stdout.write(f"{'='*60}\n")