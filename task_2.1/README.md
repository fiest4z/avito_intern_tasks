API-тесты для микросервиса объявлений Avito

Описание

Автоматизированные тесты для API микросервиса объявлений (`https://qa-internship.avito.com`), покрывающие 4 эндпоинта:

| Метод | Эндпоинт | Описание |

| POST | `/api/1/item` | Создать объявление |
| GET | `/api/1/item/{id}` | Получить объявление по ID |
| GET | `/api/1/{sellerId}/item` | Получить все объявления продавца |
| GET | `/api/1/statistic/{id}` | Получить статистику объявления |

Структура проекта

```
avito-api-tests/
├── conftest.py              # Фикстуры и вспомогательные функции
├── test_create_item.py      # Тесты создания объявлений
├── test_get_item.py         # Тесты получения объявления по ID
├── test_get_seller_items.py # Тесты получения объявлений продавца
├── test_statistic.py        # Тесты статистики
├── test_e2e.py              # E2E-сценарии
├── test_nonfunctional.py    # Нефункциональные проверки
├── requirements.txt         # Зависимости Python
├── pyproject.toml           # Конфигурация pytest, ruff
├── TESTCASES.md             # Описание тест-кейсов
├── BUGS.md                  # Баг-репорты
└── README.md                # Эта инструкция
```

Установка

Требования

- Python 3.10+
- pip

Создание виртуального окружения, установка зависимостей

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Запуск тестов

Все тесты

```bash
pytest -v
```

По категориям (с использованием маркеров)

```bash
# Только позитивные
pytest -v -m positive

# Только негативные
pytest -v -m negative

# Корнер-кейсы
pytest -v -m corner

# E2E-сценарии
pytest -v -m e2e

# Нефункциональные
pytest -v -m nonfunctional
```

По модулям

```bash
pytest test_create_item.py -v
pytest test_get_item.py -v
pytest test_get_seller_items.py -v
pytest test_statistic.py -v
pytest test_e2e.py -v
pytest test_nonfunctional.py -v
```

Allure-отчёты

Установка Allure CLI
Allure требует Java (JDK 8+). Установка на Ubuntu:

1. Установить Java (если не установлена)
```bash
sudo apt update
sudo apt install -y default-jre


2. Скачать и установить Allure
ALLURE_VERSION=2.30.0
wget -q https://github.com/allure-framework/allure2/releases/download/${ALLURE_VERSION}/allure-${ALLURE_VERSION}.tgz
tar -xzf allure-${ALLURE_VERSION}.tgz
sudo mv allure-${ALLURE_VERSION} /opt/allure
sudo ln -sf /opt/allure/bin/allure /usr/local/bin/allure

3. Проверить установку
allure --version


macOS (через Homebrew)
brew install allure

Через npm (кроссплатформенно)
npm install -g allure-commandline
```


Запуск тестов с сохранением результатов Allure

```bash
pytest -v --alluredir=allure-results
```

Генерация и просмотр отчёта

```bash
allure serve allure-results
```

Или сгенерировать статический отчёт:

```bash
allure generate allure-results -o allure-report --clean
allure open allure-report
```

Линтер и форматтер

Проект использует   Ruff   (конфигурация в `pyproject.toml`).

Проверка кода

```bash
ruff check .
```

Автоматическое исправление

```bash
ruff check . --fix
```

Форматирование

```bash
ruff format .
```

Особенности тестов

- Каждый тест независим - создаёт свои данные через фикстуры.
- `sellerId` генерируется случайно в диапазоне `111111–999999` для изоляции от других тестировщиков.
- E2E-тесты проверяют полные цепочки: создание → чтение → верификация.
- Allure-шаги, заголовки и вложения интегрированы во все тесты.
- Нефункциональные тесты проверяют время ответа, HTTP-методы и заголовки.
