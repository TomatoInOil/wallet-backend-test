from django.urls import path

from .views import OperationCreateView, WalletView

urlpatterns = [
    path(
        "v1/wallets/<uuid:wallet_id>/",
        WalletView.as_view(),
        name="wallet-detail",
    ),
    path(
        "v1/wallets/<uuid:wallet_id>/operation/",
        OperationCreateView.as_view(),
        name="operation-list",
    ),
]
