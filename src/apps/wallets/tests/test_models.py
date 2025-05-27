from datetime import timedelta
from decimal import Decimal
from uuid import UUID

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from apps.wallets.models import Operation, OperationType, Wallet

TEST_PASSWORD = "testpass"
TEST_USERNAME = "testuser"


class WalletModelTest(TestCase):
    INITIAL_BALANCE = Decimal("1000.00")
    TEST_VALID_AMOUNT = Decimal("50.00")

    def setUp(self):
        self.wallet = Wallet.objects.create(balance=self.INITIAL_BALANCE)

    def test_wallet_creation(self):
        """Кошелек был создан корректно."""
        self.assertIsInstance(self.wallet.id, UUID)
        self.assertEqual(self.wallet.balance, self.INITIAL_BALANCE)
        expected = (
            f"Кошелек {self.wallet.id}; Баланс: {str(self.INITIAL_BALANCE)}"
        )
        self.assertEqual(str(self.wallet), expected)

    def test_wallet_balance_cannot_be_negative(self):
        """Баланс не может быть отрицательным."""
        with self.assertRaises(ValidationError):
            wallet = Wallet(balance=Decimal("-1.00"))
            wallet.full_clean()

    def test_operations_deleted_with_wallet(self):
        """Удаление кошелька удаляет связанные операции."""
        Operation.objects.create(
            amount=self.TEST_VALID_AMOUNT,
            operation_type=OperationType.DEPOSIT,
            wallet=self.wallet,
        )
        self.assertNotEqual(Operation.objects.count(), 0)

        self.wallet.delete()
        self.assertEqual(Operation.objects.count(), 0)


class OperationModelTest(TestCase):
    INITIAL_BALANCE = Decimal("1000.00")
    TEST_VALID_AMOUNT = Decimal("50.00")
    INVALID_OPERATION_TYPE = "INVALID_OPERATION_TYPE"

    def setUp(self):
        self.wallet = Wallet.objects.create(balance=self.INITIAL_BALANCE)
        self.operation = Operation.objects.create(
            amount=self.TEST_VALID_AMOUNT,
            operation_type=OperationType.DEPOSIT,
            wallet=self.wallet,
        )

    def test_operation_creation(self):
        """Проверка, что операция была создана корректно."""
        self.assertIsInstance(self.operation.id, UUID)
        self.assertEqual(self.operation.amount, self.TEST_VALID_AMOUNT)
        self.assertEqual(self.operation.operation_type, OperationType.DEPOSIT)
        self.assertEqual(self.operation.wallet, self.wallet)
        self.assertIsNotNone(self.operation.created_at)

        expected_str = (
            f"Операция {self.operation.id};"
            f" {OperationType.DEPOSIT};"
            f" {str(self.TEST_VALID_AMOUNT)}"
        )
        self.assertEqual(str(self.operation), expected_str)

    def test_operation_amount_validation(self):
        """Сумма операции должна быть не меньше 0.01."""
        invalids_amounts = (Decimal("0.00"), Decimal("-1.00"))
        for amount in invalids_amounts:
            with self.subTest(amount=amount):
                with self.assertRaises(ValidationError):
                    operation = Operation(
                        amount=amount,
                        operation_type=OperationType.DEPOSIT,
                        wallet=self.wallet,
                    )
                    operation.full_clean()

    def test_correct_operation_type(self):
        """Проверяет валидные типы операций."""
        for operation_type in OperationType.names:
            with self.subTest(operation_type=operation_type):
                valid_operation = Operation(
                    amount=self.TEST_VALID_AMOUNT,
                    operation_type=operation_type,
                    wallet=self.wallet,
                )
                valid_operation.full_clean()

    def test_incorrect_operation_type(self):
        """Нельзя создать операцию с невалидным типом операции."""
        with self.assertRaises(ValidationError):
            invalid_operation = Operation(
                amount=self.TEST_VALID_AMOUNT,
                operation_type=self.INVALID_OPERATION_TYPE,
                wallet=self.wallet,
            )
            invalid_operation.full_clean()

    def test_operation_ordering(self):
        """Проверка сортировки операций по времени создания."""
        now = timezone.now()
        ops = [
            Operation(
                amount=self.TEST_VALID_AMOUNT,
                operation_type=OperationType.DEPOSIT,
                wallet=self.wallet,
                created_at=now - timedelta(seconds=i),
            )
            for i in range(6)
        ]
        Operation.objects.bulk_create(ops)

        operations = Operation.objects.all()
        self.assertTrue(
            all(
                operations[i].created_at >= operations[i + 1].created_at
                for i in range(len(operations) - 1)
            )
        )

    def test_operation_wallet_relation(self):
        """Проверка связи операции с кошельком."""
        self.assertEqual(self.operation.wallet, self.wallet)
        self.assertIn(self.operation, self.wallet.operations.all())

    def test_operation_without_wallet(self):
        """Нельзя создать операцию без связанного кошелька."""
        with self.assertRaises(IntegrityError):
            Operation.objects.create(
                amount=self.TEST_VALID_AMOUNT,
                operation_type=OperationType.DEPOSIT,
                wallet=None,
            )
