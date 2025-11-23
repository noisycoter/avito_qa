import pytest
import requests
import time

# 1. Создать объявление (POST /api/1/item)

def test_post_001_successful_creation(create_ad, seller_id):
    """POST-001: Успешное создание объявления"""
    ad_name = f"Test Ad {time.time()}"
    ad_data = create_ad(name=ad_name, price=1000)
    
    assert "id" in ad_data
    assert ad_data["sellerId"] == seller_id
    assert ad_data["name"] == ad_name
    assert ad_data["price"] == 1000
    assert "statistics" in ad_data
    assert ad_data["statistics"]["likes"] == 10
    assert "createdAt" in ad_data

def test_post_002_create_second_ad_same_seller(create_ad, seller_id):
    """POST-002: Создание второго объявления для того же продавца"""
    ad1 = create_ad(name="Ad 1 for Seller", price=100)
    ad2 = create_ad(name="Ad 2 for Seller", price=200)
    
    assert ad1["id"] != ad2["id"]
    assert ad1["sellerId"] == seller_id
    assert ad2["sellerId"] == seller_id

def test_post_003_invalid_seller_id_type(base_url, session):
    """POST-003: Невалидный sellerID (строка вместо числа)"""
    payload = {
        "sellerID": "invalid_id",
        "name": "Invalid Seller Test",
        "price": 1000,
        "statistics": {"likes": 0, "viewCount": 0, "contacts": 0}
    }
    response = session.post(f"{base_url}/item", json=payload)
    assert response.status_code == 400
    assert "result" in response.json() and "status" in response.json()

def test_post_004_missing_required_field_name(base_url, session, seller_id):
    """POST-004: Отсутствие обязательного поля (name)"""
    payload = {
        "sellerID": seller_id,
        "price": 1000,
        "statistics": {"likes": 0, "viewCount": 0, "contacts": 0}
    }
    response = session.post(f"{base_url}/item", json=payload)
    assert response.status_code == 400
    assert "result" in response.json() and "status" in response.json()

def test_post_005_invalid_price_type(base_url, session, seller_id):
    """POST-005: Невалидный тип данных для price (строка)"""
    payload = {
        "sellerID": seller_id,
        "name": "Invalid Price Test",
        "price": "ten",
        "statistics": {"likes": 0, "viewCount": 0, "contacts": 0}
    }
    response = session.post(f"{base_url}/item", json=payload)
    assert response.status_code == 400
    assert "result" in response.json() and "status" in response.json()

# 2. Получить объявление по его идентификатору (GET /api/1/item/:id)

@pytest.fixture(scope="function")
def created_ad_id(create_ad):
    """Фикстура для создания объявления и возврата его ID."""
    ad_data = create_ad(name="Ad for GET test", price=500)
    return ad_data["id"]

def test_get_id_001_successful_get(base_url, session, created_ad_id, seller_id):
    """GET-ID-001: Успешное получение существующего объявления"""
    response = session.get(f"{base_url}/item/{created_ad_id}")
    assert response.status_code == 200
    ad_data = response.json()
    assert isinstance(ad_data, list)
    assert len(ad_data) == 1
    ad_data = ad_data[0]
    assert ad_data["id"] == created_ad_id
    assert ad_data["sellerId"] == seller_id
    assert ad_data["name"] == "Ad for GET test"
    assert ad_data["price"] == 500

def test_get_id_002_non_existent_ad(base_url, session, non_existent_id):
    """GET-ID-002: Получение несуществующего объявления"""
    response = session.get(f"{base_url}/item/{non_existent_id}")
    assert response.status_code == 404

def test_get_id_003_invalid_id_format(base_url, session):
    """GET-ID-003: Невалидный формат id (если формат ID строго типизирован)"""
    response = session.get(f"{base_url}/item/!!!")
    assert response.status_code == 400 or response.status_code == 404

# 3. Получить все объявления по идентификатору продавца (GET /api/1/:sellerID/item) -

@pytest.fixture(scope="function")
def seller_with_two_ads(create_ad, seller_id):
    """Фикстура для создания двух объявлений для одного продавца."""
    ad1 = create_ad(name="Seller Ad 1", price=10)
    ad2 = create_ad(name="Seller Ad 2", price=20)
    return seller_id, [ad1, ad2]

def test_get_seller_001_successful_get_all(base_url, session, seller_with_two_ads):
    """GET-SELLER-001: Успешное получение всех объявлений продавца"""
    seller_id, ads = seller_with_two_ads
    response = session.get(f"{base_url}/{seller_id}/item")
    assert response.status_code == 200
    response_ads = response.json()

    assert len(response_ads) >= 2
    
    created_ids = {ad["id"] for ad in ads}
    response_ids = {ad["id"] for ad in response_ads}

    assert created_ids.issubset(response_ids)

    for ad in response_ads:
        assert ad["sellerId"] == seller_id

def test_get_seller_002_seller_with_no_ads(base_url, session, unique_new_seller_id):
    """GET-SELLER-002: Получение объявлений для продавца без объявлений"""
    response = session.get(f"{base_url}/{unique_new_seller_id}/item")
    assert response.status_code == 200
    assert response.json() == []

def test_get_seller_003_invalid_seller_id_type(base_url, session):
    """GET-SELLER-003: Невалидный sellerID (строка вместо числа)"""
    response = session.get(f"{base_url}/invalid_seller/item")
    assert response.status_code == 400
    assert "result" in response.json() and "status" in response.json()

# 4. Получить статистику по item id (GET /api/1/statistic/:id)

@pytest.fixture(scope="function")
def ad_with_stats(create_ad):
    """Фикстура для создания объявления с известной статистикой."""
    stats = {"likes": 42, "viewCount": 100, "contacts": 15}
    ad_data = create_ad(name="Ad for Stats test", price=999, likes=stats["likes"], view_count=stats["viewCount"], contacts=stats["contacts"])
    return ad_data["id"], stats

def test_get_stats_001_successful_get(base_url, session, ad_with_stats):
    """GET-STATS-001: Успешное получение статистики по существующему объявлению"""
    ad_id, expected_stats = ad_with_stats
    response = session.get(f"{base_url}/statistic/{ad_id}")
    assert response.status_code == 200

    response_stats_list = response.json()
    assert isinstance(response_stats_list, list)
    assert len(response_stats_list) > 0

    found = False
    for stats in response_stats_list:
        if (stats.get("likes") == expected_stats["likes"] and
            stats.get("viewCount") == expected_stats["viewCount"] and
            stats.get("contacts") == expected_stats["contacts"]):
            found = True
            break
    
    assert found, f"Expected stats {expected_stats} not found in response {response_stats_list}"

def test_get_stats_002_non_existent_ad(base_url, session, non_existent_id):
    response = session.get(f"{base_url}/statistic/{non_existent_id}")
    assert response.status_code == 404

def test_get_stats_003_stats_structure(base_url, session, ad_with_stats):
    ad_id, _ = ad_with_stats
    response = session.get(f"{base_url}/statistic/{ad_id}")
    assert response.status_code == 200
    
    response_stats_list = response.json()
    assert isinstance(response_stats_list, list)
    assert len(response_stats_list) > 0

    stats = response_stats_list[0]
    assert "likes" in stats
    assert "viewCount" in stats
    assert "contacts" in stats
    assert isinstance(stats["likes"], int)
    assert isinstance(stats["viewCount"], int)
    assert isinstance(stats["contacts"], int)
