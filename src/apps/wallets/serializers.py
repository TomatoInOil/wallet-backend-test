from rest_framework import serializers

from .models import Operation, Wallet


class OperationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operation
        fields = ("id", "operation_type", "amount")
        read_only_fields = ("id",)


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ("id", "balance")
