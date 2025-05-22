from django.apps import AppConfig


class WalletsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.wallets"

    def ready(self):
        from decimal import ROUND_HALF_UP, getcontext

        getcontext().prec = 28
        getcontext().rounding = ROUND_HALF_UP
