[![Test and Lint](https://github.com/TomatoInOil/wallet-backend-test/actions/workflows/tests.yml/badge.svg)](https://github.com/TomatoInOil/wallet-backend-test/actions/workflows/tests.yml) [![Deploy](https://github.com/TomatoInOil/wallet-backend-test/actions/workflows/deploy.yml/badge.svg)](https://github.com/TomatoInOil/wallet-backend-test/actions/workflows/deploy.yml)
# Wallet Service
Простое _REST_-приложение на _Django_ для управления балансом кошельков. Поддерживает операции пополнения и снятия средств, с учётом конкурентного доступа. Система контейнеризована с использованием _Docker_ и _docker-compose_.

📦 Стек технологий  
- Python 3.11+
- Poetry - используется для управления зависимостями
- Django + Django REST Framework
- PostgreSQL
- Docker + Docker Compose
- Grafana + Grafana Alloy + Loki + Prometheus - используются для мониторинга метрик приложения (например, частоты запросов, ошибок) и сбора логов для отладки
- Nginx

## Запуск проекта
### local
1. Клонировать репозиторий
```shell
git clone https://github.com/TomatoInOil/wallet-backend-test.git
cd wallet-backend-test/
```
2. Установить зависимости
```shell
poetry install
```
3. Активировать виртуальное окружение
```shell
poetry env activate
>>> 'C:\Users\***\AppData\Local\pypoetry\Cache\virtualenvs\wallet-backend-test-***-py3.12\Scripts\activate'
```
```shell
source 'C:\Users\***\AppData\Local\pypoetry\Cache\virtualenvs\wallet-backend-test-***-py3.12\Scripts\activate'
```
4. Создать файл `.env` и заполнить его по образцу `.env.example`
5. Перейти в src директорию
```shell
cd src/
```
6. Применить миграции
```shell
python manage.py migrate
```
7. Создать супер-пользователя (optional)
```shell
python manage.py createsuperuser
```
8. Наполнить БД пробными данными (optional)
```shell
python manage.py loaddata fixtures/wallets_data.json
```
9. Запустить dev-сервер
```shell
python manage.py runserver
```
После запуска будут доступны:  
Документация API
- swagger-ui: http://127.0.0.1:8000/api/v1/schema/swagger-ui/  
- redoc: http://127.0.0.1:8000/api/v1/schema/redoc/

Админ-панель http://127.0.0.1:8000/admin/
### docker
1. Клонировать репозиторий
```shell
git clone https://github.com/TomatoInOil/wallet-backend-test.git
cd wallet-backend-test/
```
2. Создать и заполнить `.env` файл по образцу `.env.example`
3. Перейти в директорию infra/
```shell
cd infra/
```
4. Поднять docker compose
```shell
docker compose --env-file ../.env up -d
```
5. Создать супер-пользователя (optional)
```shell
docker exec -it backend python manage.py createsuperuser
```
6. Загрузить пробные данные (optional)
```shell
docker exec backend python manage.py loaddata fixtures/wallets_data.json
```
После запуска будут доступны:  
Документация API
- swagger-ui: http://localhost/api/v1/schema/swagger-ui/
- redoc: http://localhost/api/v1/schema/redoc/

Админ-панель http://localhost/admin/  
Grafana http://localhost:3000/

## 🔌 API эндпоинты
1. Изменение баланса
```
POST /api/v1/wallets/<wallet_uuid>/operation/
```
Тело запроса:
```JSON
{
  "operation_type": "DEPOSIT", // или "WITHDRAW"
  "amount": "1000"
}
```
Пример ответа (201):
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "operation_type": "DEPOSIT",
  "amount": "1000.00"
}
```
2. Получение баланса
```
GET /api/v1/wallets/<wallet_uuid>/
```
Пример ответа (200):
```JSON
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "balance": "20.00"
}
```
## Тестирование
1. Запуск линтеров
```shell
pre-commit run --all-files
```
> [!NOTE]
> Для автоматического запуска линтеров при коммитах нужно выполнить `pre-commit install`
2. Запуск unit-тестов
```shell
cd src/
python manage.py test
```
## Grafana
- Логин и пароль задаются переменными окружения
  - `GF_SECURITY_ADMIN_USER`
  - `GF_SECURITY_ADMIN_PASSWORD`
- Для отображения метрик _Prometheus_ использую шаблон _Dashboard_ [a Django Prometheus](https://grafana.com/grafana/dashboards/9528-django-prometheus/)
  - Его можно импортировать с помощью ID `9528`
- Можно добавить на него панель для логов
  - Data source: _Loki_  
  - query: `{platform="docker", service_name="backend"}`  
  - Visualization: _Logs_  
- Или посмотреть их подробнее в разделе drilldown > logs
