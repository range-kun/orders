import pytest

from src.orders.routes import CATEGORIES_PREFIX


async def test_delete_category_not_found(client):
    response = client.delete(f"{CATEGORIES_PREFIX}/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "No rows found for table categories with next filters: {'id': 999}"}


async def test_delete_category_success(client, load_fixtures):
    response = client.delete(f"{CATEGORIES_PREFIX}/2")
    assert response.status_code == 204


def test_create_category_success(client, test_data_for_categories):
    insert_category = test_data_for_categories[0]
    response = client.post(CATEGORIES_PREFIX, json=test_data_for_categories[0])

    assert response.status_code == 201
    created_category = response.json()
    assert created_category["name"] == insert_category["name"]
    assert created_category["description"] == insert_category["description"]
    assert created_category["id"] == insert_category["id"]


@pytest.mark.parametrize(
    "category_data_for_creation, expected_status_code, expected_detail",
    [
        (
            {"name": "", "description": "This is short name field."},
            422,
            {
                "ctx": {"min_length": 1},
                "input": "",
                "loc": ["body", "name"],
                "msg": "String should have at least 1 characters",
                "type": "string_too_short",
                "url": "https://errors.pydantic.dev/2.4/v/string_too_short",
            },
        ),
        (
            {"description": "This is an invalid category."},
            422,
            {
                "type": "missing",
                "loc": ["body", "name"],
                "msg": "Field required",
                "input": {"description": "This is an invalid category."},
                "url": "https://errors.pydantic.dev/2.4/v/missing",
            },
        ),
    ],
)
async def test_create_category_validation_error(
    client, category_data_for_creation, expected_status_code, expected_detail
):
    response = client.post(CATEGORIES_PREFIX, json=category_data_for_creation)
    detail = response.json()["detail"][0]

    assert response.status_code == expected_status_code
    assert detail == expected_detail


async def test_get_category_success(client, test_data_for_categories):
    insert_category = test_data_for_categories[0]
    response_create = client.post(CATEGORIES_PREFIX, json=insert_category)
    created_category = response_create.json()
    category_id = created_category["id"]

    response = client.get(f"{CATEGORIES_PREFIX}/{category_id}")

    assert response.status_code == 200
    fetched_category = response.json()
    assert fetched_category == created_category


async def test_get_category_not_found(client):
    response = client.get("/categories/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "No rows found for table categories with next filters: {'id': 999}"}
