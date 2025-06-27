import os
from django.shortcuts import render
from django.conf import settings


class MaintenanceMiddleware:
    """
    Middleware to enable maintenance mode by creating a maintenance file.
    """
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check if maintenance mode is enabled
        maintenance_file = os.path.join(settings.BASE_DIR, 'MAINTENANCE_MODE')

        if os.path.exists(maintenance_file):
            # Allow access to admin and specific URLs during maintenance
            allowed_paths = [
                '/admin/',
                '/aura-admin/',
                # Allow emergency contact
                '/communication/',
                # Allow profile viewing
                '/developer-profile/',
            ]

            if not any(request.path.startswith(path) for path in allowed_paths):
                return render(request, 'errors/maintenance.html', status=503)
        
        response = self.get_response(request)
        return response
