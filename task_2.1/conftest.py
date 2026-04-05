"""Fixtures and helpers for Avito QA API tests.

Real API response for POST /api/1/item:
  {"status": "Сохранили объявление - <uuid>"}

The item ID (UUID) is extracted from the status string.
"""

import random
import re
import uuid

import allure
import pytest
import requests

BASE_URL = "https://qa-internship.avito.com"

UUID_PATTERN = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")


def extract_item_id(response_body: dict) -> str | None:
    """Extract item UUID from the API create response.

    The API returns {"status": "Сохранили объявление - <uuid>"}.
    Falls back to body["id"] if present (in case API changes).
    """
    if "id" in response_body:
        return response_body["id"]
    status = response_body.get("status", "")
    match = UUID_PATTERN.search(status)
    return match.group(0) if match else None


def generate_seller_id() -> int:
    """Generate a unique sellerId in the recommended range 111111–999999."""
    return random.randint(111111, 999999)


def generate_item_data(
    name: str = "Test Item",
    price: int = 5000,
    seller_id: int | None = None,
    contacts: int = 10,
    likes: int = 5,
    view_count: int = 100,
) -> dict:
    """Generate a valid item payload for POST /api/1/item."""
    return {
        "name": name,
        "price": price,
        "sellerId": seller_id or generate_seller_id(),
        "statistics": {
            "contacts": contacts,
            "likes": likes,
            "viewCount": view_count,
        },
    }


@pytest.fixture
def base_url() -> str:
    return BASE_URL


@pytest.fixture
def seller_id() -> int:
    return generate_seller_id()


@pytest.fixture
def item_data(seller_id: int) -> dict:
    return generate_item_data(seller_id=seller_id)


@pytest.fixture
def created_item(base_url: str, item_data: dict) -> dict:
    """Create an item via API and return {request_data, response_body, item_id}."""
    with allure.step("Создание объявления (fixture)"):
        response = requests.post(f"{base_url}/api/1/item", json=item_data, timeout=10)
        assert response.status_code == 200, f"Failed to create item: {response.status_code} {response.text}"
        body = response.json()
        item_id = extract_item_id(body)
        assert item_id is not None, f"Could not extract item ID from response: {body}"
        return {
            "request_data": item_data,
            "response_body": body,
            "item_id": item_id,
        }


@pytest.fixture
def unique_test_id() -> str:
    return str(uuid.uuid4())
