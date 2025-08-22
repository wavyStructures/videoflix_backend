from .settings import *

# --- Override for local runserver development ---

# Use SQLite for maximum simplicity:
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

DEBUG = True
