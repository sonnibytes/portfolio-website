# NOTE TO SELF: Was using this to get a clear idea of what request.resolver_match was returning so I could dial in
# the 'active' status of the aura-aedmin pages for the projects and blogs app. 
# Currently, 'active' pages for the Core app work as expected (easy since that's the core aura-admin setup)
# but when visiting any aura-admin pages for projects, all projects links on sidebar show as 'active' - same w blog app.
# Need to tweak if statements for request.resolver_match in admin_base.html to address this

from django.test import RequestFactory
from django.urls import resolve
from django.http import HttpRequest

path = '/aura-admin/core/'

# 1. Simulate request object
factory = RequestFactory()
request = factory.get(path)

# 2. Manually resolve the url and assign it to resolver_match
# This step simulates the URL resolution process that django performs
# before a view is called

try:
    resolved_url = resolve(request.path)
    request.resolver_match = resolved_url
except Exception as e:
    print(f"Error resolving URL: {e}")
    # Handle cases where the URL might not resolve (e.g., 404)
    # You might want to create a dummy ResolverMatch if you want to proceed
    # with a non-existent URL for demonstration purposes.

# 3. Access attributes of resolver_match
if hasattr(request, 'resolver_match') and request.resolver_match:
    print(f"View function: {request.resolver_match.func}")
    print(f"URL name: {request.resolver_match.url_name}")
    print(f"Arguments: {request.resolver_match.args}")
    print(f"Keyword arguments: {request.resolver_match.kwargs}")
    print(f"Namespace: {request.resolver_match.namespace}")
    print(f"App names: {request.resolver_match.app_names}")
else:
    print("request.resolver_match is not set (URL might not have resolved).")