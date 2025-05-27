from django.db import transaction
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Operation, OperationType, Wallet
from .serializers import OperationSerializer, WalletSerializer
from .wallet_service import WalletService


class WalletView(RetrieveAPIView):
    """Получение информации о кошельке."""

    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    lookup_url_kwarg = "wallet_id"


class OperationCreateView(APIView):
    """Обработка пополнения или снятия средств с кошелька."""

    @extend_schema(
        request=OperationSerializer,
        responses={201: OperationSerializer},
    )
    @transaction.atomic
    def post(self, request, wallet_id):
        try:
            wallet = Wallet.objects.select_for_update().get(id=wallet_id)
        except Wallet.DoesNotExist:
            raise NotFound()

        serializer = OperationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        operation_type = serializer.validated_data["operation_type"]
        amount = serializer.validated_data["amount"]

        if operation_type == OperationType.WITHDRAW:
            WalletService.withdraw(wallet, amount)
        elif operation_type == OperationType.DEPOSIT:
            WalletService.deposit(wallet, amount)
        else:
            ValidationError(
                {
                    "operation_type": (
                        "Недопустимое значение operation_type."
                        f" Допустимы {OperationType.WITHDRAW},"
                        f" {OperationType.DEPOSIT}."
                    )
                }
            )
        wallet.save()

        operation = Operation.objects.create(
            wallet=wallet,
            amount=amount,
            operation_type=operation_type,
        )
        response_serializer = OperationSerializer(operation)

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )
