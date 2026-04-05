import time

import allure
import pytest
import requests

from conftest import generate_item_data, generate_seller_id

# ---------------------------------------------------------------------------
# Non-functional tests
# ---------------------------------------------------------------------------


@allure.epic("API Объявлений")
@allure.feature("Нефункциональные проверки")
class TestNonFunctional:
    """Non-functional test cases."""

    @pytest.mark.nonfunctional
    @allure.title("TC-NF-001: Время ответа на создание < 3 секунд")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_response_time(self, base_url, seller_id):
        data = generate_item_data(seller_id=seller_id)

        start = time.monotonic()
        response = requests.post(f"{base_url}/api/1/item", json=data, timeout=10)
        elapsed = time.monotonic() - start

        assert response.status_code == 200
        allure.attach(f"{elapsed:.3f}s", name="Response time", attachment_type=allure.attachment_type.TEXT)
        assert elapsed < 3.0, f"Response time {elapsed:.3f}s exceeds 3s threshold"

    @pytest.mark.nonfunctional
    @allure.title("TC-NF-002: Время ответа на GET < 1 секунды")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_response_time(self, base_url, created_item):
        item_id = created_item["item_id"]

        start = time.monotonic()
        response = requests.get(f"{base_url}/api/1/item/{item_id}", timeout=10)
        elapsed = time.monotonic() - start

        assert response.status_code == 200
        allure.attach(f"{elapsed:.3f}s", name="Response time", attachment_type=allure.attachment_type.TEXT)
        assert elapsed < 1.0, f"Response time {elapsed:.3f}s exceeds 1s threshold"

    @pytest.mark.nonfunctional
    @allure.title("TC-NF-003: PUT на /api/1/item — 405 Method Not Allowed")
    @allure.severity(allure.severity_level.MINOR)
    def test_put_method_not_allowed(self, base_url):
        data = generate_item_data(seller_id=generate_seller_id())
        response = requests.put(f"{base_url}/api/1/item", json=data, timeout=10)
        assert response.status_code == 405, f"Expected 405, got {response.status_code}: {response.text}"

    @pytest.mark.nonfunctional
    @allure.title("TC-NF-004: DELETE на /api/1/item/{id} — 405 Method Not Allowed")
    @allure.severity(allure.severity_level.MINOR)
    def test_delete_method_not_allowed(self, base_url, created_item):
        item_id = created_item["item_id"]
        response = requests.delete(f"{base_url}/api/1/item/{item_id}", timeout=10)
        assert response.status_code == 405, f"Expected 405, got {response.status_code}: {response.text}"

    @pytest.mark.nonfunctional
    @allure.title("TC-NF-005: Content-Type ответа — application/json")
    @allure.severity(allure.severity_level.NORMAL)
    def test_response_content_type(self, base_url, created_item):
        item_id = created_item["item_id"]
        response = requests.get(f"{base_url}/api/1/item/{item_id}", timeout=10)
        assert response.status_code == 200
        content_type = response.headers.get("Content-Type", "")
        assert "application/json" in content_type, f"Expected application/json, got: {content_type}"
