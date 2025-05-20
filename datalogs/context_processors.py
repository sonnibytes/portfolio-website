# blog/context_processors.py

# from datalogs.models import DataLog, Category


# def blog_context(request):
#     """
#     Add blog-related context variables to all templates.
#     """
#     return {
#         "categories": Category.objects.all(),
#         "total_logs_count": DataLog.objects.filter(status="published").count(),
#     }
