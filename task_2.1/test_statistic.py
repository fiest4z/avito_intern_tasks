"""
Postman contract:
  Response 200: array [{ likes, viewCount, contacts }]
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
@allure.feature("Статистика объявления")
@allure.story("Позитивные сценарии")
class TestStatisticPositive:
    """Positive test cases for item statistics."""

    @pytest.mark.positive
    @allure.title("TC-STAT-001: Получение статистики существующего объявления")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_statistic(self, base_url, created_item):
        item_id = created_item["item_id"]

        with allure.step(f"GET /api/1/statistic/{item_id}"):
            response = requests.get(f"{base_url}/api/1/statistic/{item_id}", timeout=10)

        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        body = response.json()

        with allure.step("Проверить структуру ответа"):
            # Postman shows response as array of { likes, viewCount, contacts }
            stats = body[0] if isinstance(body, list) else body
            for field in ("contacts", "likes", "viewCount"):
                assert field in stats, f"Missing statistics field: {field}"

    @pytest.mark.positive
    @allure.title("TC-STAT-002: Значения статистики соответствуют переданным при создании")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_statistic_values_match(self, base_url, created_item):
        item_id = created_item["item_id"]
        req_stats = created_item["request_data"]["statistics"]

        response = requests.get(f"{base_url}/api/1/statistic/{item_id}", timeout=10)
        assert response.status_code == 200
        body = response.json()
        stats = body[0] if isinstance(body, list) else body

        with allure.step("Проверить contacts"):
            assert stats["contacts"] == req_stats["contacts"], f"contacts: {stats['contacts']} != {req_stats['contacts']}"

        with allure.step("Проверить likes"):
            assert stats["likes"] == req_stats["likes"], f"likes: {stats['likes']} != {req_stats['likes']}"

        with allure.step("Проверить viewCount"):
            assert stats["viewCount"] == req_stats["viewCount"], f"viewCount: {stats['viewCount']} != {req_stats['viewCount']}"


# ---------------------------------------------------------------------------
# Negative tests
# ---------------------------------------------------------------------------


@allure.epic("API Объявлений")
@allure.feature("Статистика объявления")
@allure.story("Негативные сценарии")
class TestStatisticNegative:
    """Negative test cases for item statistics."""

    @pytest.mark.negative
    @allure.title("TC-STAT-101: Статистика несуществующего объявления — 404")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_statistic_nonexistent_item(self, base_url):
        fake_id = str(uuid.uuid4())
        response = requests.get(f"{base_url}/api/1/statistic/{fake_id}", timeout=10)
        assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"

    @pytest.mark.negative
    @allure.title("TC-STAT-102: Невалидный формат ID")
    @allure.severity(allure.severity_level.NORMAL)
    def test_statistic_invalid_id(self, base_url):
        response = requests.get(f"{base_url}/api/1/statistic/!!invalid!!", timeout=10)
        assert response.status_code in (400, 404), f"Expected 400/404, got {response.status_code}: {response.text}"


# ---------------------------------------------------------------------------
# Corner cases
# ---------------------------------------------------------------------------


@allure.epic("API Объявлений")
@allure.feature("Статистика объявления")
@allure.story("Корнер-кейсы")
class TestStatisticCorner:
    """Corner test cases for item statistics."""

    @pytest.mark.corner
    @allure.title("TC-STAT-201: Идемпотентность GET статистики")
    @allure.severity(allure.severity_level.NORMAL)
    def test_statistic_idempotent(self, base_url, created_item):
        item_id = created_item["item_id"]

        resp1 = requests.get(f"{base_url}/api/1/statistic/{item_id}", timeout=10)
        resp2 = requests.get(f"{base_url}/api/1/statistic/{item_id}", timeout=10)

        assert resp1.status_code == 200
        assert resp2.status_code == 200
        assert resp1.json() == resp2.json(), "Repeated GET should return identical statistics"
