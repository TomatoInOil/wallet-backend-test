from decimal import Decimal

from django.test import TestCase
from rest_framework.exceptions import ValidationError

from apps.wallets.models import Wallet
from apps.wallets.wallet_service import WalletService


class TestWalletService(TestCase):
    INITIAL_BALANCE = Decimal("100.00")

    def setUp(self):
        self.wallet = Wallet.objects.create(balance=self.INITIAL_BALANCE)

    def test_deposit_positive_amount(self):
        """Проверка пополнения кошелька на положительную сумму."""
        updated_wallet = WalletService.deposit(self.wallet, Decimal("50.00"))
        self.assertEqual(updated_wallet.balance, Decimal("150.00"))

        self.wallet.refresh_from_db()
        self.assertEqual(
            self.wallet.balance,
            Decimal("100.00"),
            msg="Изменения не должны были сохраниться в БД.",
        )

    def test_withdraw_sufficient_funds(self):
        """Проверка списания при достаточном балансе."""
        updated_wallet = WalletService.withdraw(self.wallet, Decimal("30.00"))
        self.assertEqual(updated_wallet.balance, Decimal("70.00"))

        self.wallet.refresh_from_db()
        self.assertEqual(
            self.wallet.balance,
            Decimal("100.00"),
            msg="Изменения не должны были сохраниться в БД.",
        )

    def test_withdraw_insufficient_funds(self):
        """Проверка ошибки при недостаточном балансе."""
        with self.assertRaisesRegex(ValidationError, r"Недостаточно средств"):
            WalletService.withdraw(
                self.wallet, self.INITIAL_BALANCE + Decimal("50.00")
            )
