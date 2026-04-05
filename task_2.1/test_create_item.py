"""Tests for POST /api/1/item — Create an advertisement.

Real API behavior discovered:
  - Response: {"status": "Сохранили объявление - <uuid>"}  (NOT {"id": ...})
  - price=0 returns 400 (rejected)
  - Negative price, negative sellerId, sellerId=0 all return 200 (BUGS)
"""

import allure
import pytest
import requests

from conftest import extract_item_id, generate_item_data


@allure.epic("API Объявлений")
@allure.feature("Создание объявления")
@allure.story("Позитивные сценарии")
class TestCreateItemPositive:
    @pytest.mark.positive
    @allure.title("TC-CR-001: Создание объявления с валидными данными")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_item_valid(self, base_url, item_data):
        with allure.step("Отправить POST /api/1/item"):
            response = requests.post(f"{base_url}/api/1/item", json=item_data, timeout=10)

        with allure.step("Проверить статус код 200"):
            assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

        with allure.step("Проверить что в ответе есть UUID объявления"):
            body = response.json()
            item_id = extract_item_id(body)
            assert item_id is not None, f"Could not extract item ID from: {body}"
            allure.attach(str(item_id), name="Created item ID", attachment_type=allure.attachment_type.TEXT)

    @pytest.mark.positive
    @allure.title("TC-CR-002: Ответ содержит поле status с UUID")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_item_response_has_status(self, base_url, item_data):
        response = requests.post(f"{base_url}/api/1/item", json=item_data, timeout=10)
        assert response.status_code == 200
        body = response.json()
        assert "status" in body, f"Response must contain 'status': {body}"

    @pytest.mark.positive
    @allure.title("TC-CR-003: Несколько объявлений получают уникальные ID")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_multiple_items_unique_ids(self, base_url, seller_id):
        ids = []
        for i in range(3):
            data = generate_item_data(name=f"Item {i}", seller_id=seller_id)
            with allure.step(f"Создать объявление #{i + 1}"):
                resp = requests.post(f"{base_url}/api/1/item", json=data, timeout=10)
                assert resp.status_code == 200
                item_id = extract_item_id(resp.json())
                assert item_id is not None
                ids.append(item_id)

        with allure.step("Проверить уникальность ID"):
            assert len(set(ids)) == 3, f"All IDs must be unique, got: {ids}"

    @pytest.mark.positive
    @allure.title("TC-CR-004: Создание объявления с большой ценой")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_item_large_price(self, base_url, seller_id):
        data = generate_item_data(price=999_999_999, seller_id=seller_id)
        response = requests.post(f"{base_url}/api/1/item", json=data, timeout=10)
        assert response.status_code == 200

    @pytest.mark.positive
    @pytest.mark.corner
    @allure.title("TC-CR-005: POST не идемпотентен — дубли создают разные объявления")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_item_not_idempotent(self, base_url, item_data):
        resp1 = requests.post(f"{base_url}/api/1/item", json=item_data, timeout=10)
        resp2 = requests.post(f"{base_url}/api/1/item", json=item_data, timeout=10)
        assert resp1.status_code == 200
        assert resp2.status_code == 200
        id1 = extract_item_id(resp1.json())
        id2 = extract_item_id(resp2.json())
        assert id1 != id2, "Duplicate POST must create items with different IDs"

    @pytest.mark.positive
    @allure.title("TC-CR-006: Создание объявления с длинным именем (500 символов)")
    @allure.severity(allure.severity_level.MINOR)
    def test_create_item_long_name(self, base_url, seller_id):
        data = generate_item_data(name="A" * 500, seller_id=seller_id)
        response = requests.post(f"{base_url}/api/1/item", json=data, timeout=10)
        assert response.status_code == 200


@allure.epic("API Объявлений")
@allure.feature("Создание объявления")
@allure.story("Негативные сценарии")
class TestCreateItemNegative:
    @pytest.mark.negative
    @allure.title("TC-CR-101: Создание без поля name")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_item_missing_name(self, base_url, seller_id):
        data = {"price": 100, "sellerId": seller_id, "statistics": {"contacts": 1, "likes": 0, "viewCount": 0}}
        response = requests.post(f"{base_url}/api/1/item", json=data, timeout=10)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"

    @pytest.mark.negative
    @allure.title("TC-CR-102: Создание без поля price")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_item_missing_price(self, base_url, seller_id):
        data = {"name": "Item", "sellerId": seller_id, "statistics": {"contacts": 1, "likes": 0, "viewCount": 0}}
        response = requests.post(f"{base_url}/api/1/item", json=data, timeout=10)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"

    @pytest.mark.negative
    @allure.title("TC-CR-103: Создание без поля sellerId")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_item_missing_seller_id(self, base_url):
        data = {"name": "Item", "price": 100, "statistics": {"contacts": 1, "likes": 0, "viewCount": 0}}
        response = requests.post(f"{base_url}/api/1/item", json=data, timeout=10)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"

    @pytest.mark.negative
    @allure.title("TC-CR-104: Создание с отрицательной ценой — BUG: сервер принимает (200)")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_item_negative_price(self, base_url, seller_id):
        """BUG-002: API accepts negative price with 200 instead of returning 400."""
        data = generate_item_data(price=-100, seller_id=seller_id)
        response = requests.post(f"{base_url}/api/1/item", json=data, timeout=10)
        assert response.status_code == 400, f"Expected 400 for negative price, got {response.status_code}"

    @pytest.mark.negative
    @allure.title("TC-CR-105: Создание с sellerId строкой")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_item_seller_id_string(self, base_url):
        data = {"name": "Item", "price": 100, "sellerId": "abc", "statistics": {"contacts": 1, "likes": 0, "viewCount": 0}}
        response = requests.post(f"{base_url}/api/1/item", json=data, timeout=10)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"

    @pytest.mark.negative
    @allure.title("TC-CR-106: Создание с price строкой")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_item_price_string(self, base_url, seller_id):
        data = {"name": "Item", "price": "бесплатно", "sellerId": seller_id, "statistics": {"contacts": 1, "likes": 0, "viewCount": 0}}
        response = requests.post(f"{base_url}/api/1/item", json=data, timeout=10)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"

    @pytest.mark.negative
    @allure.title("TC-CR-107: Создание с пустым телом запроса")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_item_empty_body(self, base_url):
        response = requests.post(f"{base_url}/api/1/item", json={}, timeout=10)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"

    @pytest.mark.negative
    @allure.title("TC-CR-108: Создание с невалидным JSON")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_item_invalid_json(self, base_url):
        response = requests.post(
            f"{base_url}/api/1/item",
            data="{invalid json}",
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"

    @pytest.mark.negative
    @allure.title("TC-CR-109: Создание с пустым name")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_item_empty_name(self, base_url, seller_id):
        data = generate_item_data(name="", seller_id=seller_id)
        response = requests.post(f"{base_url}/api/1/item", json=data, timeout=10)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"

    @pytest.mark.negative
    @allure.title("TC-CR-110: Создание с sellerId = 0 — BUG: сервер принимает (200)")
    @allure.severity(allure.severity_level.MINOR)
    def test_create_item_seller_id_zero(self, base_url):
        """BUG-003: API accepts sellerId=0 with 200 instead of returning 400."""
        data = generate_item_data(seller_id=0)
        response = requests.post(f"{base_url}/api/1/item", json=data, timeout=10)
        assert response.status_code == 400, f"Expected 400 for sellerId=0, got {response.status_code}"

    @pytest.mark.negative
    @allure.title("TC-CR-111: Создание с отрицательным sellerId — BUG: сервер принимает (200)")
    @allure.severity(allure.severity_level.MINOR)
    def test_create_item_negative_seller_id(self, base_url):
        """BUG-004: API accepts negative sellerId with 200 instead of returning 400."""
        data = generate_item_data(seller_id=-1)
        response = requests.post(f"{base_url}/api/1/item", json=data, timeout=10)
        assert response.status_code == 400, f"Expected 400 for negative sellerId, got {response.status_code}"

    @pytest.mark.negative
    @allure.title("TC-CR-112: Создание с price = 0 — сервер отклоняет (400)")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_item_zero_price(self, base_url, seller_id):
        """API rejects price=0 with 400."""
        data = generate_item_data(price=0, seller_id=seller_id)
        response = requests.post(f"{base_url}/api/1/item", json=data, timeout=10)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"


@allure.epic("API Объявлений")
@allure.feature("Создание объявления")
@allure.story("Корнер-кейсы")
class TestCreateItemCorner:
    @pytest.mark.corner
    @allure.title("TC-CR-201: Дополнительные поля игнорируются")
    @allure.severity(allure.severity_level.MINOR)
    def test_create_item_extra_fields(self, base_url, seller_id):
        data = generate_item_data(seller_id=seller_id)
        data["extraField"] = "should be ignored"
        response = requests.post(f"{base_url}/api/1/item", json=data, timeout=10)
        assert response.status_code == 200

    @pytest.mark.corner
    @allure.title("TC-CR-202: XSS-payload в name")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_item_xss_name(self, base_url, seller_id):
        data = generate_item_data(name="<script>alert('xss')</script>", seller_id=seller_id)
        response = requests.post(f"{base_url}/api/1/item", json=data, timeout=10)
        assert response.status_code == 200

    @pytest.mark.corner
    @allure.title("TC-CR-203: Дробная цена (price = 99.99)")
    @allure.severity(allure.severity_level.MINOR)
    def test_create_item_float_price(self, base_url, seller_id):
        data = {"name": "Float", "price": 99.99, "sellerId": seller_id, "statistics": {"contacts": 1, "likes": 0, "viewCount": 0}}
        response = requests.post(f"{base_url}/api/1/item", json=data, timeout=10)
        assert response.status_code in (200, 400), f"Unexpected status {response.status_code}"

    @pytest.mark.corner
    @allure.title("TC-CR-204: Unicode-символы в name")
    @allure.severity(allure.severity_level.MINOR)
    def test_create_item_unicode_name(self, base_url, seller_id):
        data = generate_item_data(name="テスト 🎉 Ñ äöü Привет", seller_id=seller_id)
        response = requests.post(f"{base_url}/api/1/item", json=data, timeout=10)
        assert response.status_code == 200

    @pytest.mark.corner
    @allure.title("TC-CR-205: Неправильный Content-Type")
    @allure.severity(allure.severity_level.MINOR)
    def test_create_item_wrong_content_type(self, base_url, seller_id):
        data = generate_item_data(seller_id=seller_id)
        response = requests.post(
            f"{base_url}/api/1/item",
            data=str(data),
            headers={"Content-Type": "text/plain"},
            timeout=10,
        )
        assert response.status_code in (400, 415), f"Expected 400/415, got {response.status_code}"
