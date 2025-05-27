import uuid
from decimal import Decimal

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from apps.wallets.models import OperationType, Wallet


class WalletViewsTest(APITestCase):
    INITIAL_BALANCE_STR = "100.00"
    INITIAL_BALANCE = Decimal(INITIAL_BALANCE_STR)

    def setUp(self):
        self.wallet = Wallet.objects.create(balance=self.INITIAL_BALANCE)
        self.wallet_url = reverse(
            "wallet-detail", kwargs={"wallet_id": self.wallet.id}
        )

    def test_get_wallet(self):
        """Проверка получения информации о кошельке."""
        response = self.client.get(self.wallet_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.wallet.id))
        self.assertEqual(response.data["balance"], self.INITIAL_BALANCE_STR)

    def test_get_nonexistent_wallet_returns_404(self):
        """Проверка запроса несуществующего кошелька."""
        non_existent_wallet_url = reverse(
            "wallet-detail", kwargs={"wallet_id": (uuid.uuid4())}
        )
        response = self.client.get(non_existent_wallet_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class OperationViewsTest(APITestCase):
    INITIAL_BALANCE_STR = "100.00"
    INITIAL_BALANCE = Decimal(INITIAL_BALANCE_STR)

    def setUp(self):
        self.wallet = Wallet.objects.create(balance=self.INITIAL_BALANCE)
        self.operation_url = reverse(
            "operation-list", kwargs={"wallet_id": self.wallet.id}
        )

    def test_create_deposit_operation(self):
        """Проверка создания операции пополнения."""
        data = {
            "operation_type": OperationType.DEPOSIT,
            "amount": "50.00",
        }
        response = self.client.post(self.operation_url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)
        self.assertEqual(
            response.data["operation_type"], OperationType.DEPOSIT
        )
        self.assertEqual(Decimal(response.data["amount"]), Decimal("50.00"))

        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal("150.00"))

    def test_create_withdraw_operation(self):
        """Проверка создания операции снятия."""
        data = {
            "operation_type": OperationType.WITHDRAW,
            "amount": "30.00",
        }
        response = self.client.post(self.operation_url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)
        self.assertEqual(
            response.data["operation_type"], OperationType.WITHDRAW
        )
        self.assertEqual(Decimal(response.data["amount"]), Decimal("30.00"))

        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal("70.00"))

    def test_withdraw_more_than_balance(self):
        """Проверка попытки снять больше, чем есть на счету."""
        data = {
            "operation_type": OperationType.WITHDRAW,
            "amount": "200.00",
        }
        response = self.client.post(self.operation_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("amount", response.data)

        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal("100.00"))

    def test_validating_operation_type(self):
        """Проверка валидации типа операции."""
        operation_types = {
            OperationType.DEPOSIT: status.HTTP_201_CREATED,
            OperationType.WITHDRAW: status.HTTP_201_CREATED,
            "INVALID_OPERATION_TYPE": status.HTTP_400_BAD_REQUEST,
        }
        for operation_type, expected_status_code in operation_types.items():
            data = {
                "operation_type": operation_type,
                "amount": "10.00",
            }
            response = self.client.post(self.operation_url, data)

            self.assertEqual(response.status_code, expected_status_code)
            self.assertIn("operation_type", response.data)

    def test_validating_amount(self):
        """Проверка валидации суммы."""
        invalid_amounts = ("0.00", "-1.00")
        for amount in invalid_amounts:
            with self.subTest(amount=amount):
                data = {
                    "operation_type": OperationType.DEPOSIT,
                    "amount": amount,
                }
                response = self.client.post(self.operation_url, data)

                self.assertEqual(
                    response.status_code, status.HTTP_400_BAD_REQUEST
                )
                self.assertIn("amount", response.data)

    def test_nonexistent_wallet(self):
        """Проверка работы с несуществующим кошельком."""
        non_existent_wallet_operation_url = reverse(
            "operation-list", kwargs={"wallet_id": (uuid.uuid4())}
        )
        response = self.client.post(non_existent_wallet_operation_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
