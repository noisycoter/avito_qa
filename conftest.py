import pytest
import requests
import random
import time
from datetime import datetime

BASE_URL = "https://qa-internship.avito.com/api/1"
UNIQUE_SELLER_ID = random.randint(111111, 999999)

@pytest.fixture(scope="session")
def base_url():
    return BASE_URL

@pytest.fixture(scope="session")
def seller_id():
    return UNIQUE_SELLER_ID

@pytest.fixture(scope="session")
def session():
    return requests.Session()

@pytest.fixture(scope="function")
def create_ad(session, base_url, seller_id):
    
    created_ads = []

    def _create_ad(name, price, likes=10, view_count=50, contacts=5):
        payload = {
            "sellerID": seller_id,
            "name": name,
            "price": price,
            "statistics": {
                "likes": likes,
                "viewCount": view_count,
                "contacts": contacts
            }
        }
        response = session.post(f"{base_url}/item", json=payload)
        assert response.status_code == 200

        response_text = response.json().get("status", "")
        ad_id = response_text.split(" - ")[-1]

        ad_data = {
            "id": ad_id,
            "sellerId": seller_id,
            "name": name,
            "price": price,
            "statistics": {
                "likes": likes,
                "viewCount": view_count,
                "contacts": contacts
            },
            "createdAt": datetime.now().isoformat()
        }
        created_ads.append(ad_data)
        return ad_data

    yield _create_ad

@pytest.fixture(scope="function")
def non_existent_id():
    return "nonExistentID_1234567890"

@pytest.fixture(scope="function")
def unique_new_seller_id():
    return random.randint(900000, 999999)
