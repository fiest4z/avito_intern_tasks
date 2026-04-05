"""
Postman contract:
  Response 200: array of items [{ id, sellerId, name, price, statistics: {...}, createdAt }]
  Response 400: { result: { messages, message }, status }
  Response 404: { result, status }
"""

import uuid

import allure
import pytest
import requests

# ---------------------------------------------------------------------------
# Positive tests
# ---------------------------------------------------------------------------


@allure.epic("API Объявлений")
@allure.feature("Получение объявления по ID")
@allure.story("Позитивные сценарии")
class TestGetItemPositive:
    """Positive test cases for getting an item by ID."""

    @pytest.mark.positive
    @allure.title("TC-GET-001: Получение существующего объявления — статус 200")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_existing_item(self, base_url, created_item):
        item_id = created_item["item_id"]

        with allure.step(f"GET /api/1/item/{item_id}"):
            response = requests.get(f"{base_url}/api/1/item/{item_id}", timeout=10)

        with allure.step("Проверить статус 200"):
            assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

        with allure.step("Проверить структуру ответа"):
            body = response.json()
            # Postman shows response as array, but single item may be returned as object
            item = body[0] if isinstance(body, list) else body
            for field in ("id", "name", "price", "sellerId"):
                assert field in item, f"Missing field: {field}"

    @pytest.mark.positive
    @allure.title("TC-GET-002: Данные объявления совпадают с данными при создании")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_item_data_matches(self, base_url, created_item):
        item_id = created_item["item_id"]
        req = created_item["request_data"]

        response = requests.get(f"{base_url}/api/1/item/{item_id}", timeout=10)
        assert response.status_code == 200
        body = response.json()
        item = body[0] if isinstance(body, list) else body

        with allure.step("Проверить name"):
            assert item["name"] == req["name"], f"Name mismatch: {item['name']} != {req['name']}"

        with allure.step("Проверить price"):
            assert item["price"] == req["price"], f"Price mismatch: {item['price']} != {req['price']}"

        with allure.step("Проверить sellerId"):
            assert item["sellerId"] == req["sellerId"], f"SellerId mismatch: {item['sellerId']} != {req['sellerId']}"

    @pytest.mark.positive
    @allure.title("TC-GET-003: Ответ содержит вложенный объект statistics")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_item_has_statistics(self, base_url, created_item):
        item_id = created_item["item_id"]

        response = requests.get(f"{base_url}/api/1/item/{item_id}", timeout=10)
        assert response.status_code == 200
        body = response.json()
        item = body[0] if isinstance(body, list) else body

        with allure.step("Проверить наличие statistics"):
            assert "statistics" in item, f"Missing 'statistics': {item}"
            stats = item["statistics"]
            for field in ("contacts", "likes", "viewCount"):
                assert field in stats, f"Missing statistics.{field}: {stats}"

    @pytest.mark.positive
    @allure.title("TC-GET-004: Ответ содержит поле createdAt")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_item_has_created_at(self, base_url, created_item):
        item_id = created_item["item_id"]

        response = requests.get(f"{base_url}/api/1/item/{item_id}", timeout=10)
        assert response.status_code == 200
        body = response.json()
        item = body[0] if isinstance(body, list) else body

        with allure.step("Проверить наличие createdAt"):
            assert "createdAt" in item, f"Missing 'createdAt': {item}"


# ---------------------------------------------------------------------------
# Negative tests
# ---------------------------------------------------------------------------


@allure.epic("API Объявлений")
@allure.feature("Получение объявления по ID")
@allure.story("Негативные сценарии")
class TestGetItemNegative:
    """Negative test cases for getting an item by ID."""

    @pytest.mark.negative
    @allure.title("TC-GET-101: Получение несуществующего объявления — 404")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_nonexistent_item(self, base_url):
        fake_id = str(uuid.uuid4())
        response = requests.get(f"{base_url}/api/1/item/{fake_id}", timeout=10)
        assert response.status_code == 404, f"Expected 404 for non-existent item, got {response.status_code}: {response.text}"

    @pytest.mark.negative
    @allure.title("TC-GET-102: Невалидный формат ID")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_item_invalid_id(self, base_url):
        response = requests.get(f"{base_url}/api/1/item/!!invalid!!", timeout=10)
        assert response.status_code in (400, 404), f"Expected 400/404 for invalid ID, got {response.status_code}: {response.text}"

    @pytest.mark.negative
    @allure.title("TC-GET-103: Пустой ID в пути")
    @allure.severity(allure.severity_level.MINOR)
    def test_get_item_empty_id(self, base_url):
        response = requests.get(f"{base_url}/api/1/item/", timeout=10)
        assert response.status_code in (400, 404, 405), f"Expected error for empty ID, got {response.status_code}"


# ---------------------------------------------------------------------------
# Corner cases
# ---------------------------------------------------------------------------


@allure.epic("API Объявлений")
@allure.feature("Получение объявления по ID")
@allure.story("Корнер-кейсы")
class TestGetItemCorner:
    """Corner test cases for getting an item by ID."""

    @pytest.mark.corner
    @allure.title("TC-GET-201: Идемпотентность GET — два запроса дают одинаковый ответ")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_item_idempotent(self, base_url, created_item):
        item_id = created_item["item_id"]

        resp1 = requests.get(f"{base_url}/api/1/item/{item_id}", timeout=10)
        resp2 = requests.get(f"{base_url}/api/1/item/{item_id}", timeout=10)

        assert resp1.status_code == 200
        assert resp2.status_code == 200
        assert resp1.json() == resp2.json(), "Repeated GET should return identical results"
