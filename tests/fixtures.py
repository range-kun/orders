from datetime import datetime

test_categories = [
    {
        "id": 1,
        "name": "Category A",
        "description": "This is category A.",
    },
    {
        "id": 2,
        "name": "Category B",
        "description": "Category B description goes here.",
    },
    {
        "id": 3,
        "name": "Category C",
        "description": "Description for category C.",
    },
]

test_products = [
    {
        "id": 1,
        "name": "Product 1",
        "description": "Description for Product 1.",
        "price": 29.99,
        "created": datetime(2023, 10, 23, 12, 0, 0),
        "category_id": 1,
    },
    {
        "id": 2,
        "name": "Product 2",
        "description": "Description for Product 2.",
        "price": 49.99,
        "created": datetime(2023, 10, 23, 13, 0, 0),
        "category_id": 2,
    },
    {
        "id": 3,
        "name": "Product 3",
        "description": "Description for Product 3.",
        "price": 39.99,
        "created": datetime(2023, 10, 23, 14, 0, 0),
        "category_id": 3,
    },
]


auth_user = {"id": 1, "is_active": True}
