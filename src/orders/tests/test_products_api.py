import pytest
from fastapi.encoders import jsonable_encoder

from src.orders.routes import PRODUCTS_PREFIX


async def test_delete_products_not_found(client):
    response = client.delete(f"{PRODUCTS_PREFIX}/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "No rows found for table products with next filters: {'id': 999}"}


@pytest.mark.usefixtures("load_fixtures")
async def test_delete_product_success(client):
    response = client.delete(f"{PRODUCTS_PREFIX}/2")
    assert response.status_code == 204


@pytest.mark.usefixtures("load_fixtures")
def test_get_product_success(client, test_data_for_products):
    insert_product = jsonable_encoder(test_data_for_products[0])
    response = client.get(f"{PRODUCTS_PREFIX}/{insert_product['id']}")

    assert response.status_code == 200

    fetched_product = response.json()
    assert insert_product["name"] == fetched_product["name"]
    assert insert_product["description"] == fetched_product["description"]
    assert insert_product["price"] == float(fetched_product["price"])
    assert insert_product["created"] == fetched_product["created"]
    assert insert_product["category_id"] == fetched_product["category"]["id"]


async def test_get_product_not_found(client):
    response = client.get(f"{PRODUCTS_PREFIX}/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "No rows found for table products with next filters: {'id': 999}"}


@pytest.mark.usefixtures("load_categories")
async def test_create_product_success(client, test_data_for_products, load_categories):
    insert_product = jsonable_encoder(test_data_for_products[0])
    response_create = client.post(PRODUCTS_PREFIX, json=insert_product)
    assert response_create.status_code == 201

    created_product = response_create.json()
    product_id = created_product["id"]

    response_get = client.get(f"{PRODUCTS_PREFIX}/{product_id}")
    fetched_product = response_get.json()
    assert created_product["name"] == fetched_product["name"]
    assert created_product["description"] == fetched_product["description"]
    assert created_product["price"] == fetched_product["price"]
    assert created_product["created"] == fetched_product["created"]
    assert created_product["category_id"] == fetched_product["category"]["id"]


@pytest.mark.parametrize(
    "product_data_for_creation, expected_status_code, expected_detail",
    [
        (
            {"name": "", "description": "string", "price": -12, "category_id": 0},
            422,
            [
                {
                    "type": "string_too_short",
                    "loc": ["body", "name"],
                    "msg": "String should have at least 1 characters",
                    "input": "",
                    "ctx": {"min_length": 1},
                    "url": "https://errors.pydantic.dev/2.4/v/string_too_short",
                },
                {
                    "type": "value_error",
                    "loc": ["body", "price"],
                    "msg": "Value error, Should be positive value",
                    "input": -12,
                    "ctx": {"error": {}},
                    "url": "https://errors.pydantic.dev/2.4/v/value_error",
                },
            ],
        ),
        (
            {"description": "This is an invalid data."},
            422,
            [
                {
                    "type": "missing",
                    "loc": ["body", "name"],
                    "msg": "Field required",
                    "input": {"description": "This is an invalid data."},
                    "url": "https://errors.pydantic.dev/2.4/v/missing",
                },
                {
                    "type": "missing",
                    "loc": ["body", "price"],
                    "msg": "Field required",
                    "input": {"description": "This is an invalid data."},
                    "url": "https://errors.pydantic.dev/2.4/v/missing",
                },
                {
                    "type": "missing",
                    "loc": ["body", "category_id"],
                    "msg": "Field required",
                    "input": {"description": "This is an invalid data."},
                    "url": "https://errors.pydantic.dev/2.4/v/missing",
                },
            ],
        ),
        (
            {"name": "dsfsd", "description": "string", "price": 12, "category_id": 0},
            400,
            "Category with id 0 not exists",
        ),
    ],
)
async def test_create_product_validation_error(
    client, product_data_for_creation, expected_status_code, expected_detail
):
    response = client.post(PRODUCTS_PREFIX, json=product_data_for_creation)
    detail = response.json()["detail"]

    assert response.status_code == expected_status_code
    assert detail == expected_detail


@pytest.mark.usefixtures("load_fixtures")
async def test_update_product_success(client, test_data_for_products):
    new_updated_product = jsonable_encoder(test_data_for_products[0])
    product_path = f"{PRODUCTS_PREFIX}/{new_updated_product['id']}"
    new_updated_product["name"] = "New Shiny Name"
    response_update = client.put(product_path, json=new_updated_product)
    updated_product = response_update.json()

    fetched_product = client.get(product_path).json()

    assert response_update.status_code == 200
    assert updated_product["name"] == fetched_product["name"]
    assert updated_product["description"] == fetched_product["description"]
    assert updated_product["price"] == fetched_product["price"]
    assert updated_product["created"] == fetched_product["created"]
    assert updated_product["category_id"] == fetched_product["category"]["id"]


async def test_update_not_existing_object(client, test_data_for_products):
    new_updated_product = jsonable_encoder(test_data_for_products[0])
    response_update = client.put(f"{PRODUCTS_PREFIX}/999", json=new_updated_product)
    data = response_update.json()

    assert response_update.status_code == 404
    assert data == {"detail": "No rows found for table products with next filters: {'id': 999}"}


@pytest.mark.usefixtures("load_fixtures")
def test_update_not_existing_category(client, test_data_for_products):
    new_updated_product = jsonable_encoder(test_data_for_products[0])
    new_updated_product["category_id"] = 123
    response_update = client.put(f"{PRODUCTS_PREFIX}/{new_updated_product['id']}", json=new_updated_product)
    data = response_update.json()

    assert response_update.status_code == 400
    assert data == {"detail": "Category with id 123 not exists"}


@pytest.mark.usefixtures("load_fixtures")
def test_update_validation_error(client):
    invalid_data = {"description": "invalid data", "name": ""}
    response_update = client.put(f"{PRODUCTS_PREFIX}/1", json=invalid_data)

    assert response_update.status_code == 422
    data = response_update.json()["detail"]

    failed_data = [
        {
            "type": "string_too_short",
            "loc": ["body", "name"],
            "msg": "String should have at least 1 characters",
            "input": "",
            "ctx": {"min_length": 1},
            "url": "https://errors.pydantic.dev/2.4/v/string_too_short",
        },
        {
            "type": "missing",
            "loc": ["body", "price"],
            "msg": "Field required",
            "input": {"description": "invalid data", "name": ""},
            "url": "https://errors.pydantic.dev/2.4/v/missing",
        },
        {
            "type": "missing",
            "loc": ["body", "category_id"],
            "msg": "Field required",
            "input": {"description": "invalid data", "name": ""},
            "url": "https://errors.pydantic.dev/2.4/v/missing",
        },
    ]
    assert failed_data == data
