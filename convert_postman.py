
import json
from pathlib import Path

output_file = (
    Path(__file__).parent
    / "postman"
    / "Asset-Register-API.postman_collection.json"
)

base_url = "{{baseUrl}}"

collection = {
    "info": {
        "name": "Asset Register API",
        "description": "Flask Asset Register API using SQLite and SQLAlchemy.",
        "schema": (
            "https://schema.getpostman.com/json/collection/v2.1.0/"
            "collection.json"
        ),
    },
    "variable": [
        {
            "key": "baseUrl",
            "value": "http://127.0.0.1:5000",
        },
        {
            "key": "assetId",
            "value": "4",
        },
    ],
    "item": [
        {
            "name": "Create Asset",
            "request": {
                "method": "POST",
                "header": [
                    {"key": "Content-Type", "value": "application/json"}
                ],
                "url": base_url + "/assets",
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "asset_name": "HP EliteBook Laptop",
                        "asset_tag": "AST-008",
                        "category": "IT Equipment",
                        "location": "Finance Department",
                        "purchase_date": "2026-10-28",
                        "purchase_cost": 72000
                    }, indent=2),
                    "options": {"raw": {"language": "json"}},
                },
            },
        },
        {
            "name": "Get All Active Assets",
            "request": {
                "method": "GET",
                "header": [],
                "url": base_url + "/assets",
            },
        },
        {
            "name": "Filter Assets by Type and Tag",
            "request": {
                "method": "GET",
                "header": [],
                "url": {
                    "raw": base_url + "/assets?type=IT%20Equipment&tag=Office",
                    "host": ["{{baseUrl}}"],
                    "path": ["assets"],
                    "query": [
                        {"key": "type", "value": "IT Equipment"},
                        {"key": "tag", "value": "Office"},
                    ],
                },
            },
        },
        {
            "name": "Filter Assets by Tag",
            "request": {
                "method": "GET",
                "header": [],
                "url": base_url + "/assets?tag=Office",
            },
        },
        {
            "name": "Get Asset by ID",
            "request": {
                "method": "GET",
                "header": [],
                "url": base_url + "/assets/{{assetId}}",
            },
        },
        {
            "name": "Update Asset",
            "request": {
                "method": "PUT",
                "header": [
                    {"key": "Content-Type", "value": "application/json"}
                ],
                "url": base_url + "/assets/{{assetId}}",
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "location": "IT Department",
                        "purchase_cost": 73000
                    }, indent=2),
                    "options": {"raw": {"language": "json"}},
                },
            },
        },
        {
            "name": "Add Asset Tags",
            "request": {
                "method": "POST",
                "header": [
                    {"key": "Content-Type", "value": "application/json"}
                ],
                "url": base_url + "/assets/{{assetId}}/tags",
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "tags": ["Office", "Laptop", "Finance"]
                    }, indent=2),
                    "options": {"raw": {"language": "json"}},
                },
            },
        },
        {
            "name": "Deactivate Asset",
            "request": {
                "method": "DELETE",
                "header": [],
                "url": base_url + "/assets/{{assetId}}",
            },
        },
    ],
}

output_file.parent.mkdir(parents=True, exist_ok=True)
output_file.write_text(
    json.dumps(collection, indent=2),
    encoding="utf-8",
)

print(f"Collection created: {output_file}")
print(f"Requests included: {len(collection['item'])}")
