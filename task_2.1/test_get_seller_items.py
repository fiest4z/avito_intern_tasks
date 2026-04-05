import allure
import pytest
import requests

from conftest import extract_item_id, generate_item_data, generate_seller_id


@allure.epic("API Объявлений")
@allure.feature("Получение объявлений продавца")
@allure.story("Позитивные сценарии")
class TestGetSellerItemsPositive:
    @pytest.mark.positive
    @allure.title("TC-SEL-001: Получение объявлений существующего продавца")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_seller_items(self, base_url, created_item):
        seller_id = created_item["request_data"]["sellerId"]
        response = requests.get(f"{base_url}/api/1/{seller_id}/item", timeout=10)
        assert response.status_code == 200
        body = response.json()
        assert isinstance(body, list)
        assert len(body) >= 1

    @pytest.mark.positive
    @allure.title("TC-SEL-002: Все объявления принадлежат запрошенному продавцу")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_seller_items_belong_to_seller(self, base_url, seller_id):
        for i in range(3):
            data = generate_item_data(name=f"Seller item {i}", seller_id=seller_id)
            resp = requests.post(f"{base_url}/api/1/item", json=data, timeout=10)
            assert resp.status_code == 200
        response = requests.get(f"{base_url}/api/1/{seller_id}/item", timeout=10)
        assert response.status_code == 200
        for item in response.json():
            assert item["sellerId"] == seller_id

    @pytest.mark.positive
    @allure.title("TC-SEL-003: Все созданные объявления присутствуют в ответе")
    @allure.severity(allure.severity_level.NORMAL)
    def test_all_created_items_returned(self, base_url):
        sid = generate_seller_id()
        created_ids = []
        for i in range(3):
            data = generate_item_data(name=f"Check item {i}", seller_id=sid)
            resp = requests.post(f"{base_url}/api/1/item", json=data, timeout=10)
            assert resp.status_code == 200
            item_id = extract_item_id(resp.json())
            assert item_id is not None
            created_ids.append(item_id)
        response = requests.get(f"{base_url}/api/1/{sid}/item", timeout=10)
        assert response.status_code == 200
        returned_ids = [item["id"] for item in response.json()]
        for cid in created_ids:
            assert cid in returned_ids, f"Created item {cid} not found"

    @pytest.mark.positive
    @allure.title("TC-SEL-004: Каждый элемент содержит все ожидаемые поля")
    @allure.severity(allure.severity_level.NORMAL)
    def test_seller_items_structure(self, base_url, created_item):
        seller_id = created_item["request_data"]["sellerId"]
        response = requests.get(f"{base_url}/api/1/{seller_id}/item", timeout=10)
        assert response.status_code == 200
        for item in response.json():
            for field in ("id", "sellerId", "name", "price", "statistics", "createdAt"):
                assert field in item, f"Missing '{field}'"


@allure.epic("API Объявлений")
@allure.feature("Получение объявлений продавца")
@allure.story("Негативные сценарии")
class TestGetSellerItemsNegative:
    @pytest.mark.negative
    @allure.title("TC-SEL-101: Несуществующий продавец")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_items_nonexistent_seller(self, base_url):
        unique_sid = generate_seller_id()
        response = requests.get(f"{base_url}/api/1/{unique_sid}/item", timeout=10)
        if response.status_code == 200:
            assert isinstance(response.json(), list)
        else:
            assert response.status_code == 404

    @pytest.mark.negative
    @allure.title("TC-SEL-102: Невалидный sellerId (строка)")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_items_string_seller_id(self, base_url):
        response = requests.get(f"{base_url}/api/1/abc/item", timeout=10)
        assert response.status_code == 400

    @pytest.mark.negative
    @allure.title("TC-SEL-103: sellerId = 0")
    @allure.severity(allure.severity_level.MINOR)
    def test_get_items_zero_seller_id(self, base_url):
        response = requests.get(f"{base_url}/api/1/0/item", timeout=10)
        assert response.status_code in (200, 400)

    @pytest.mark.negative
    @allure.title("TC-SEL-104: Отрицательный sellerId — BUG: сервер возвращает 200")
    @allure.severity(allure.severity_level.MINOR)
    def test_get_items_negative_seller_id(self, base_url):
        """BUG-005: API returns 200 with items for sellerId=-1 instead of 400."""
        response = requests.get(f"{base_url}/api/1/-1/item", timeout=10)
        assert response.status_code == 400, f"Expected 400 for negative sellerId, got {response.status_code}"


@allure.epic("API Объявлений")
@allure.feature("Получение объявлений продавца")
@allure.story("Корнер-кейсы")
class TestGetSellerItemsCorner:
    @pytest.mark.corner
    @allure.title("TC-SEL-201: Идемпотентность GET")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_seller_items_idempotent(self, base_url, created_item):
        seller_id = created_item["request_data"]["sellerId"]
        resp1 = requests.get(f"{base_url}/api/1/{seller_id}/item", timeout=10)
        resp2 = requests.get(f"{base_url}/api/1/{seller_id}/item", timeout=10)
        assert resp1.status_code == 200
        assert resp2.status_code == 200
        assert resp1.json() == resp2.json()
