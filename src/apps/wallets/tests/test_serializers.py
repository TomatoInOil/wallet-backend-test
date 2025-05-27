import uuid
from decimal import Decimal

from rest_framework.test import APITestCase

from apps.wallets.models import Operation, Wallet
from apps.wallets.serializers import OperationSerializer, WalletSerializer


class WalletSerializersTest(APITestCase):
    INITIAL_BALANCE_STR = "1000.00"
    INITIAL_BALANCE = Decimal(INITIAL_BALANCE_STR)

    def setUp(self):
        self.wallet_attributes = {
            "balance": self.INITIAL_BALANCE,
        }
        self.wallet = Wallet.objects.create(
            **self.wallet_attributes,
        )
        self.serializer_data = {
            "id": uuid.uuid4(),
            "balance": self.INITIAL_BALANCE_STR,
        }
        self.serializer = WalletSerializer(
            instance=self.wallet,
        )

    def test_contains_expected_fields(self):
        """Проверка, что сериализатор обладает нужными полями."""
        data = self.serializer.data
        self.assertEqual(set(data.keys()), {"id", "balance"})

    def test_balance_field_content(self):
        """Проверка, что данные поля balance сериализуются правильно."""
        data = self.serializer.data
        self.assertEqual(data["balance"], self.INITIAL_BALANCE_STR)

    def test_id_field_content(self):
        """Проверка, что данные поля id сериализуются правильно."""
        _check_id_serialize(self, self.serializer.data)

    def test_balance_lower_bound(self):
        """Проверка валидации поля balance на неотрицательность."""
        self.serializer_data["balance"] = "-0.01"
        serializer = WalletSerializer(data=self.serializer_data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors), {"balance"})

    def test_str_data_correctly_saves_as_decimal(self):
        """Проверяет, что вводимые данные корректно преобразуются в decimal."""
        self.serializer_data["balance"] = "25.67"
        serializer = WalletSerializer(data=self.serializer_data)
        serializer.is_valid()
        new_wallet = serializer.save()
        new_wallet.refresh_from_db()
        self.assertEqual(new_wallet.balance, Decimal("25.67"))


class OperationSerializersTest(APITestCase):
    VALID_AMOUNT_STR = "1000.00"
    VALID_AMOUNT = Decimal(VALID_AMOUNT_STR)
    WITHDRAW_OPERATION_TYPE = "WITHDRAW"
    DEPOSIT_OPERATION_TYPE = "DEPOSIT"
    INVALID_OPERATION_TYPE = "INVALID_OPERATION_TYPE"
    INITIAL_BALANCE = Decimal("1000.00")

    def setUp(self):
        self.operation_attributes = {
            "operation_type": self.DEPOSIT_OPERATION_TYPE,
            "amount": self.VALID_AMOUNT,
        }
        self.wallet = Wallet.objects.create(
            balance=self.INITIAL_BALANCE,
        )
        self.operation = Operation.objects.create(
            **self.operation_attributes,
            wallet=self.wallet,
        )
        self.serializer_data = {
            "id": "84a617e4-7344-4e69-84ad-50172a4ac0d8",
            "operation_type": self.DEPOSIT_OPERATION_TYPE,
            "amount": self.VALID_AMOUNT_STR,
        }
        self.serializer = OperationSerializer(
            instance=self.operation,
        )

    def test_contains_expected_fields(self):
        """Проверка, что сериализатор обладает нужными полями."""
        data = self.serializer.data
        self.assertEqual(set(data.keys()), {"id", "operation_type", "amount"})

    def test_operation_type_field_content(self):
        """Проверка, что данные поля operation_type сериализуются правильно."""
        data = self.serializer.data
        self.assertEqual(data["operation_type"], self.DEPOSIT_OPERATION_TYPE)

    def test_amount_field_content(self):
        """Проверка, что данные поля amount сериализуются правильно."""
        data = self.serializer.data
        self.assertEqual(data["amount"], self.VALID_AMOUNT_STR)

    def test_id_field_content(self):
        """Проверка, что данные поля id сериализуются правильно."""
        _check_id_serialize(self, self.serializer.data)

    def test_amount_lower_bound(self):
        """Проверка валидации поля amount на положительность."""
        invalid_amounts = ("-1.00", "0.00")
        for amount in invalid_amounts:
            with self.subTest(ampunt=amount):
                self.serializer_data["amount"] = amount
                serializer = OperationSerializer(data=self.serializer_data)
                self.assertFalse(serializer.is_valid())
                self.assertEqual(set(serializer.errors), {"amount"})

    def test_operation_type_must_be_in_choices(self):
        """Operation_type принимает только допустимые значения."""
        self.operation_attributes["operation_type"] = (
            self.INVALID_OPERATION_TYPE
        )
        serializer = OperationSerializer(
            instance=self.operation, data=self.operation_attributes
        )
        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors.keys()), {"operation_type"})

    def test_operation_type_validation_with_valid_values(self):
        """Проверяет, что operation_type принимает допустимые значения."""
        valid_operation_types = (
            self.DEPOSIT_OPERATION_TYPE,
            self.WITHDRAW_OPERATION_TYPE,
        )
        for operation_type in valid_operation_types:
            with self.subTest(operation_type=operation_type):
                self.operation_attributes["operation_type"] = operation_type
                serializer = OperationSerializer(
                    instance=self.operation, data=self.operation_attributes
                )
                self.assertTrue(serializer.is_valid())
                self.assertNotEqual(
                    set(serializer.errors.keys()), {"operation_type"}
                )


def _check_id_serialize(
    test_cls_instance: APITestCase, serializer_data: dict
) -> None:
    test_cls_instance.assertIsInstance(serializer_data["id"], str)
    try:
        uuid.UUID(serializer_data["id"], version=4)
    except ValueError:
        test_cls_instance.fail(
            f"Значение поля 'id' не является корректным UUID."
            f" Получено: {serializer_data['id']}"
        )
