from .base import *  # noqa

ALLOWED_HOSTS = ["backend"]
CSRF_TRUSTED_ORIGINS = ("http://127.0.0.1", "https://127.0.0.1")

DATABASES = {
    "default": {
        "ENGINE": os.getenv(
            "DB_ENGINE",
            default="django.db.backends.postgresql_psycopg2",
        ),
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT"),
    }
}
