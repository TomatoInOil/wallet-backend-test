from decimal import Decimal
from uuid import uuid4

from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import UUIDField

User = get_user_model()


class Wallet(models.Model):
    id = UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
    )
    balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(0)],
    )
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="wallet",
    )

    def __str__(self):
        return f"Кошелек {self.id}; Баланс: {self.balance}"


class OperationType(models.TextChoices):
    DEPOSIT = "DEPOSIT", "Пополнение"
    WITHDRAW = "WITHDRAW", "Снятие"


class Operation(models.Model):
    id = UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    operation_type = models.CharField(
        max_length=8,
        choices=OperationType.choices,
        default=OperationType.DEPOSIT,
    )
    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name="operations",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return f"Операция {self.id}; {self.operation_type}; {self.amount}"

    class Meta:
        ordering = ["-created_at"]
