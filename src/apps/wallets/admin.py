from django.contrib import admin

from .models import Wallet, Operation


class OperationInline(admin.TabularInline):
    model = Operation
    extra = 1
    fields = ("operation_type", "amount", "created_at")
    readonly_fields = ("created_at",)


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "balance")
    inlines = [OperationInline]


@admin.register(Operation)
class OperationAdmin(admin.ModelAdmin):
    list_display = ("id", "wallet", "operation_type", "amount", "created_at")
    list_filter = ("operation_type",)
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"
