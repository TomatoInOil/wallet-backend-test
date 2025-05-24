from .base import *  # noqa

ALLOWED_HOSTS = ["backend"]
CSRF_TRUSTED_ORIGINS = (
    f"http://{os.getenv('DOMAIN')}",
    f"https://{os.getenv('DOMAIN')}",
)

DATABASES = {
    "default": {
        "ENGINE": os.getenv(
            "DB_ENGINE",
            default="django.db.backends.postgresql",
        ),
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT"),
    }
}
