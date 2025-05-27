from decimal import Decimal

from rest_framework.exceptions import ValidationError

from apps.wallets.models import Wallet


class WalletService:
    """Сервис для операций с балансом кошелька."""

    @staticmethod
    def deposit(wallet: Wallet, amount: Decimal) -> Wallet:
        """
        Пополнить кошелёк на указанную сумму
        без внесения изменений в БД.
        """
        wallet.balance += amount
        return wallet

    @staticmethod
    def withdraw(wallet: Wallet, amount: Decimal) -> Wallet:
        """
        Снять средства с кошелька на указанную сумму
        без внесения изменений в БД.
        """
        if wallet.balance < amount:
            raise ValidationError({"amount": "Недостаточно средств"})
        wallet.balance -= amount
        return wallet
