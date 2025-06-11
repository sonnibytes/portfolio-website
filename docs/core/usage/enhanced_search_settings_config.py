# settings.py - Additional settings for enhanced search functionality

# Search Configuration
SEARCH_CONFIG = {
    "MIN_QUERY_LENGTH": 2,
    "MAX_SUGGESTIONS": 8,
    "DEBOUNCE_DELAY": 300,  # milliseconds
    "ENABLE_SEARCH_ANALYTICS": True,
    "CACHE_SUGGESTIONS": True,
    "CACHE_TIMEOUT": 300,  # 5 minutes
    "HIGHLIGHT_MATCHES": True,
    "ENABLE_AUTOCOMPLETE": True,
}

# Pagination settings
POSTS_PER_PAGE = 12
SEARCH_RESULTS_PER_PAGE = 12

# Cache configuration for search (if using Redis/Memcached)
if "default" in CACHES:
    CACHES["search"] = {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "search-cache",
        "TIMEOUT": 300,
        "OPTIONS": {
            "MAX_ENTRIES": 1000,
        },
    }

# Logging configuration for search
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "search_file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": "logs/search.log",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "blog.search": {
            "handlers": ["search_file"],
            "level": "INFO",
            "propagate": True,
        },
    },
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
    },
}

# Search indexing settings (for future full-text search)
SEARCH_INDEX_CONFIG = {
    "ENABLE_FULL_TEXT_SEARCH": False,  # Set to True when ready for PostgreSQL full-text
    "INDEX_FIELDS": ["title", "content", "excerpt"],
    "SEARCH_WEIGHTS": {
        "title": "A",
        "excerpt": "B",
        "content": "C",
        "tags": "D",
    },
}

# Rate limiting for search API (if needed)
SEARCH_RATE_LIMITS = {
    "SUGGESTIONS_PER_MINUTE": 60,
    "SEARCH_PER_MINUTE": 30,
    "EXPORT_PER_HOUR": 5,  # For search export functionality
}
