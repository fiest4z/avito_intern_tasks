"""E2E tests — multi-step scenarios combining create and read operations."""

import allure
import pytest
import requests

from conftest import extract_item_id, generate_item_data, generate_seller_id


@allure.epic("API Объявлений")
@allure.feature("E2E сценарии")
class TestE2E:
    @pytest.mark.e2e
    @allure.title("TC-E2E-001: Создание → Получение по ID → Проверка данных")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_create_then_get_by_id(self, base_url):
        sid = generate_seller_id()
        data = generate_item_data(name="E2E Item by ID", price=7777, seller_id=sid)

        with allure.step("1. Создать объявление"):
            create_resp = requests.post(f"{base_url}/api/1/item", json=data, timeout=10)
            assert create_resp.status_code == 200
            item_id = extract_item_id(create_resp.json())
            assert item_id is not None

        with allure.step("2. Получить объявление по ID"):
            get_resp = requests.get(f"{base_url}/api/1/item/{item_id}", timeout=10)
            assert get_resp.status_code == 200
            body = get_resp.json()
            item = body[0] if isinstance(body, list) else body

        with allure.step("3. Проверить совпадение данных"):
            assert item["name"] == data["name"]
            assert item["price"] == data["price"]
            assert item["sellerId"] == data["sellerId"]

    @pytest.mark.e2e
    @allure.title("TC-E2E-002: Создание → Получение по sellerId")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_create_then_get_by_seller(self, base_url):
        sid = generate_seller_id()
        data = generate_item_data(name="E2E Seller Item", seller_id=sid)

        with allure.step("1. Создать объявление"):
            create_resp = requests.post(f"{base_url}/api/1/item", json=data, timeout=10)
            assert create_resp.status_code == 200
            item_id = extract_item_id(create_resp.json())

        with allure.step("2. Получить объявления продавца"):
            get_resp = requests.get(f"{base_url}/api/1/{sid}/item", timeout=10)
            assert get_resp.status_code == 200

        with allure.step("3. Проверить что объявление в списке"):
            returned_ids = [item["id"] for item in get_resp.json()]
            assert item_id in returned_ids

    @pytest.mark.e2e
    @allure.title("TC-E2E-003: Создание → Статистика → Проверка значений")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_then_get_statistic(self, base_url):
        sid = generate_seller_id()
        data = generate_item_data(name="E2E Stat", seller_id=sid, contacts=42, likes=15, view_count=999)

        with allure.step("1. Создать объявление"):
            create_resp = requests.post(f"{base_url}/api/1/item", json=data, timeout=10)
            assert create_resp.status_code == 200
            item_id = extract_item_id(create_resp.json())

        with allure.step("2. Получить статистику"):
            stat_resp = requests.get(f"{base_url}/api/1/statistic/{item_id}", timeout=10)
            assert stat_resp.status_code == 200
            body = stat_resp.json()
            stats = body[0] if isinstance(body, list) else body

        with allure.step("3. Проверить совпадение"):
            assert stats["contacts"] == data["statistics"]["contacts"]
            assert stats["likes"] == data["statistics"]["likes"]
            assert stats["viewCount"] == data["statistics"]["viewCount"]

    @pytest.mark.e2e
    @allure.title("TC-E2E-004: Создание нескольких → Все у продавца")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_multiple_then_get_by_seller(self, base_url):
        sid = generate_seller_id()
        created_ids = []
        for i in range(3):
            data = generate_item_data(name=f"Multi #{i}", seller_id=sid, price=100 * (i + 1))
            resp = requests.post(f"{base_url}/api/1/item", json=data, timeout=10)
            assert resp.status_code == 200
            created_ids.append(extract_item_id(resp.json()))

        get_resp = requests.get(f"{base_url}/api/1/{sid}/item", timeout=10)
        assert get_resp.status_code == 200
        returned_ids = [item["id"] for item in get_resp.json()]
        for cid in created_ids:
            assert cid in returned_ids

    @pytest.mark.e2e
    @allure.title("TC-E2E-005: GET item и GET statistic согласованы")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_item_and_statistic_consistent(self, base_url):
        sid = generate_seller_id()
        data = generate_item_data(name="Consistency", seller_id=sid, contacts=5, likes=3, view_count=50)

        create_resp = requests.post(f"{base_url}/api/1/item", json=data, timeout=10)
        assert create_resp.status_code == 200
        item_id = extract_item_id(create_resp.json())

        item_resp = requests.get(f"{base_url}/api/1/item/{item_id}", timeout=10)
        assert item_resp.status_code == 200
        item_body = item_resp.json()
        item = item_body[0] if isinstance(item_body, list) else item_body
        item_stats = item.get("statistics", {})

        stat_resp = requests.get(f"{base_url}/api/1/statistic/{item_id}", timeout=10)
        assert stat_resp.status_code == 200
        stat_body = stat_resp.json()
        stats = stat_body[0] if isinstance(stat_body, list) else stat_body

        assert item_stats.get("likes") == stats["likes"]
        assert item_stats.get("viewCount") == stats["viewCount"]
        assert item_stats.get("contacts") == stats["contacts"]
