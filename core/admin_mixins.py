"""
Reusable CSV Import Functionality for Django Admin
Add to any ModelAdmin to enable CSV imports via admin interface
"""

"""
NOTE TO SELF ON CSV IMPORTS IN PROD: Add data files to /data folder and push to main for version control. 
ALSO -- csv file import names. Import skips all lines if I use the 2025.10.23 date prefix on file name.
Just use char for models.
"""

import csv
import io
from django import forms
from django.contrib import admin, messages
from django.shortcuts import render, redirect
from django.urls import path
from django.utils.text import slugify
from datetime import datetime


class CSVImportForm(forms.Form):
    """Form for uploading CSV files"""
    csv_file = forms.FileField(
        label="CSV File",
        help_text="Upload a CSV file to import data"
    )
    update_existing = forms.BooleanField(
        required=False,
        initial=False,
        label="Update Existing Records",
        help_text="If checked, existing records will be updated. Otherwise, they'll be skipped."
    )


class CSVImportMixin:
    """
    Mixin to add CSV import functionality to any ModelAdmin
    
    Usage:
        class SkillAdmin(CSVImportMixin, admin.ModelAdmin):
            csv_import_fields = ['name', 'category', 'description', ...]
            csv_required_fields = ['name', 'category']
            pass
    """

    csv_import_fields = []  # Define in subclass
    csv_required_fields = []  # Define in subclass
    change_list_template = "admin/csv_import_changelist.html"

    def get_urls(self):
        """Add custom URL for CSV import"""
        urls = super().get_urls()
        custom_urls = [
            path('import-csv/', self.admin_site.admin_view(self.import_csv), name=f'{self.model._meta.app_label}_{self.model._meta.model_name}_import_csv'),
        ]
        return custom_urls + urls
    
    def import_csv(self, request):
        """Handle CSV import."""
        if request.method == "POST":
            form = CSVImportForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = request.FILES["csv_file"]
                update_existing = form.cleaned_data['update_existing']

                # Process the CSV
                results = self.process_csv(csv_file, update_existing)

                # Show results
                if results['errors'] > 0:
                    messages.warning(
                        request,
                        f"Import completed with errors. Created: {results['created']}, "
                        f"Updated: {results['updated']}, Skipped: {results['skipped']}, "
                        f"Errors: {results['errors']}"
                    )
                else:
                    messages.success(
                        request,
                        f"Successfully imported! Created: {results['created']}, "
                        f"Updated: {results['updated']}, Skipped: {results['skipped']}"
                    )
                
                return redirect("..")
        else:
            form = CSVImportForm()
        
        context = {
            'form': form,
            'opts': self.model._meta,
            'has_view_permission': self.has_view_permission(request)
        }
        return render(request, "admin/csv_import.html", context)
    
    def process_csv(self, csv_file, update_existing):
        """Process the CSV file and import data"""

        created_count = 0
        updated_count = 0
        skipped_count = 0
        error_count = 0

        # Decode the file
        decoded_file = csv_file.read().decode('utf-8')
        io_string = io.StringIO(decoded_file)
        reader = csv.DictReader(io_string)

        for row_num, row in enumerate(reader, start=2):
            try:
                # Prepare the data
                data = self.prepare_row_data(row)

                if not data:
                    skipped_count += 1
                    continue

                # Get or create the object
                lookup_field = self.get_lookup_field()
                lookup_value = data.get(lookup_field)

                if not lookup_value:
                    error_count += 1
                    continue

                obj, created = self.model.objects.get_or_create(
                    **{lookup_field: lookup_value},
                    defaults=data
                )

                if created:
                    created_count += 1
                elif update_existing:
                    for key, value in data.items():
                        setattr(obj, key, value)
                        obj.save()
                        updated_count += 1
                else:
                    skipped_count += 1

            except Exception as e:
                error_count += 1
                print(f"Error on row {row_num}: {str(e)}")

        return {
            'created': created_count,
            'updated': updated_count,
            'skipped': skipped_count,
            'errors': error_count,
        }
    
    def prepare_row_data(self, row):
        """
        Prepare row data for import - override in subclass for custom logic
        Default implementation handles common fields
        """
        data = {}

        # Get name/title (most models have one or the other)
        name = row.get('name', '').strip() or row.get('title', '').strip()
        if not name:
            return None
        
        data['name'] = name

        # Auto-generate slug if not provided
        if 'slug' not in row or not row['slug'].strip():
            data['slug'] = slugify(name)
        else:
            data['slug'] = row['slug'].strip()
        
        # Process other fields based on csv_import_fields
        for field in self.csv_import_fields:
            # Already handled
            if field in ['name', 'slug']:
                continue

            value = row.get(field, '').strip()

            if not value:
                continue

            # Type conversion based on common patterns
            if field.startswith('is_') or field in ['is_featured', 'is_published', 'is_complete']:
                data[field] = self.parse_boolean(value)
            elif field in ['proficiency', 'display_order']:
                data[field] = self.parse_int(value)
            elif field in ['years_experience']:
                data[field] = self.parse_float(value)
            elif field in ['last_used', 'published_date']:
                data[field] = self.parse_date(value)
            else:
                data[field] = value

        return data
    
    def get_lookup_field(self):
        """Override to change lookup field (default: slug)"""
        return 'slug'
    
    # Helper parsing methods
    def parse_boolean(self, value):
        """Convert various bool representations to Python bool"""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            value = value.strip().upper()
            return value in ['TRUE', '1', 'YES', 'Y']
        return False
    
    def parse_int(self, value, default=0):
        """Parse int w fallback"""
        try:
            return int(value.strip()) if value.strip() else default
        except (ValueError, AttributeError):
            return default
        
    def parse_float(self, value, default=0.0):
        """Parse float w fallback"""
        try:
            return float(value.strip()) if value.strip() else default
        except(ValueError, AttributeError):
            return default
    
    def parse_date(self, value):
        """Parse date string to date object"""
        if not value or not value.strip():
            return None
        try:
            return datetime.strptime(value.strip(), '%Y-%m-%d').date()
        except ValueError:
            try:
                return datetime.strptime(value.strip(), '%m/%d/%Y').date()
            except ValueError:
                return None


# Model-specific mixins for custom logic


class SkillCSVImportMixin(CSVImportMixin):
    """Skill-specific CSV import logic"""
    csv_import_fields = [
        'name',
        'slug',
        'category',
        'description',
        'proficiency',
        'icon',
        'color',
        'display_order',
        'years_experience',
        'is_featured',
        'last_used',
        'is_currently_learning',
        'is_certified'
    ]
    csv_required_fields = ['name', 'category']


class TechnologyCSVImportMixin(CSVImportMixin):
    """Technology-specific CSV import logic"""
    csv_import_fields = [
        'name',
        'slug',
        'description',
        'category',
        'icon',
        'color'
    ]
    csv_required_fields = ['name']


class CategoryCSVImportMixin(CSVImportMixin):
    """Category-specific CSV import logic"""
    csv_import_fields = [
        'name',
        'slug',
        'code',
        'description',
        'color',
        'icon'
    ]
    csv_required_fields = ['name', 'code']

    def prepare_row_data(self, row):
        data = super().prepare_row_data(row)
        if data and 'code' in row:
            data['code'] = row['code'].strip().upper()[:2]
        return data


class TagCSVImportMixin(CSVImportMixin):
    """Tag-specific CSV import logic"""
    csv_import_fields = [
        'name',
        'slug'
    ]
    csv_required_fields = ['name']


class SeriesCSVImportMixin(CSVImportMixin):
    """Series-spcific CSV import logic"""
    csv_import_fields = [
        'title',
        'slug',
        'description',
        'difficulty_level',
        'is_complete',
        'is_featured'
    ]
    csv_required_fields = ['title']

    def prepare_row_data(self, row):
        # Series uses 'title' instead of 'name'
        data = {}
        title = row.get('title', '').strip()
        if not title:
            return None
        
        data['title'] = title
        data['slug'] = slugify(title)

        # Process other fields
        for field in ['description', 'difficulty_level']:
            if field in row and row[field].strip():
                data[field] = row[field].strip()

        # Booleans
        for field in ['is_complete', 'is_featured']:
            if field in row:
                data[field] = self.parse_boolean(row[field])
        
        return data


class SystemTypeCSVImportMixin(CSVImportMixin):
    """SystemType-specific CSV import logic"""
    csv_import_fields = [
        'name',
        'slug',
        'description',
        'icon',
        'color',
        'display_order'
    ]
    csv_required_fields = ['name']
