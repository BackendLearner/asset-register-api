import pytest
from exceptions import AssetNotFoundError
from routes import asset_repository


def test_create_asset(client):

    payload = {
        "asset_name": "Laptop",
        "asset_tag": "AST-001",
        "category": "IT",
        "location": "Pune",
        "purchase_date": "2026-11-18",
        "purchase_cost": 50000
    }

    response = client.post("/assets", json=payload)

    assert response.status_code == 201

    data = response.get_json()

    assert data["asset_name"] == "Laptop"
    assert data["asset_tag"] == "AST-001"
    assert data["category"] == "IT"
    assert data["location"] == "Pune"
    assert data["status"] == "Active"



def test_create_duplicate_asset_tag(client):

    payload = {
        "asset_name": "Laptop",
        "asset_tag": "AST-002",
        "category": "IT",
        "location": "Pune",
        "purchase_date": "2026-11-18",
        "purchase_cost": 50000
    }

    first_response = client.post("/assets", json=payload)

    assert first_response.status_code == 201

    second_response = client.post("/assets", json=payload)

    assert second_response.status_code == 409

    data = second_response.get_json()

    assert data["error"] == "DuplicateAssetError"   


def test_create_asset_missing_required_field(client):

    payload = {
        "asset_tag": "AST-003",
        "category": "IT",
        "location": "Pune"
    }

    response = client.post("/assets", json=payload)

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "AssetValidationError"
    assert data["message"] == "Validation failed"    


@pytest.mark.parametrize("purchase_cost", [-500, -100, -1])
def test_create_asset_negative_purchase_cost(client, purchase_cost):

    payload = {
        "asset_name": "Laptop",
        "asset_tag": "AST-004",
        "category": "IT",
        "location": "Pune",
        "purchase_date": "2026-11-18",
        "purchase_cost": purchase_cost
    }

    response = client.post("/assets", json=payload)

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "AssetValidationError"
    assert data["message"] == "Validation failed"

def test_get_all_assets(client):

    payload = {
        "asset_name": "Laptop",
        "asset_tag": "AST-005",
        "category": "IT",
        "location": "Pune",
        "purchase_cost": 50000
    }

    client.post("/assets", json=payload)

    response = client.get("/assets")

    assert response.status_code == 200

    data = response.get_json()

    assert len(data) == 1
    assert data[0]["asset_name"] == "Laptop"
    assert data[0]["asset_tag"] == "AST-005"

def test_filter_assets_by_category(client):

    client.post("/assets", json={
        "asset_name": "Laptop",
        "asset_tag": "AST-006",
        "category": "IT",
        "location": "Pune"
    })

    client.post("/assets", json={
        "asset_name": "Chair",
        "asset_tag": "AST-007",
        "category": "Furniture",
        "location": "Mumbai"
    })

    response = client.get("/assets?type=IT")

    assert response.status_code == 200

    data = response.get_json()

    assert len(data) == 1
    assert data[0]["asset_name"] == "Laptop"
    assert data[0]["category"] == "IT" 


def test_filter_assets_by_tag(client):

    asset_response = client.post("/assets", json={
        "asset_name": "Laptop",
        "asset_tag": "AST-008",
        "category": "IT",
        "location": "Pune"
    })

    asset_id = asset_response.get_json()["id"]

    client.post(f"/assets/{asset_id}/tags", json={
        "tags": ["Office"]
    })

    response = client.get("/assets?tag=Office")

    assert response.status_code == 200

    data = response.get_json()

    assert len(data) == 1
    assert data[0]["asset_name"] == "Laptop"
    assert data[0]["asset_tag"] == "AST-008"    


def test_get_asset_by_id(client):

    create_response = client.post("/assets", json={
        "asset_name": "Monitor",
        "asset_tag": "AST-009",
        "category": "IT",
        "location": "Pune",
        "purchase_cost": 15000
    })

    asset_id = create_response.get_json()["id"]

    response = client.get(f"/assets/{asset_id}")

    assert response.status_code == 200

    data = response.get_json()

    assert data["id"] == asset_id
    assert data["asset_name"] == "Monitor"
    assert data["asset_tag"] == "AST-009"
    assert data["category"] == "IT"
    assert data["status"] == "Active"


def test_get_asset_not_found(client):

    response = client.get("/assets/9999")

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "AssetNotFoundError"
    assert data["success"] is False
    assert "not found" in data["message"]    



def test_delete_asset(client):

    payload = {
        "asset_name": "Keyboard",
        "asset_tag": "AST-010",
        "category": "IT"
    }

    create_response = client.post("/assets", json=payload)

    asset_id = create_response.get_json()["id"]

    response = client.delete(f"/assets/{asset_id}")

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "Inactive"
    assert data["id"] == asset_id



def test_delete_asset_not_found(client):

    response = client.delete("/assets/9999")

    assert response.status_code == 404

    data = response.get_json()

    assert data["success"] is False
    assert data["error"] == "AssetNotFoundError"
    assert "not found" in data["message"]    


def test_update_asset(client):

    payload = {
        "asset_name": "Laptop",
        "asset_tag": "AST-011",
        "category": "IT"
    }

    create_response = client.post("/assets", json=payload)

    asset_id = create_response.get_json()["id"]

    update_payload = {
        "asset_name": "Dell Laptop",
        "location": "Mumbai"
    }

    response = client.put(
        f"/assets/{asset_id}",
        json=update_payload
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["asset_name"] == "Dell Laptop"
    assert data["location"] == "Mumbai"
    assert data["asset_tag"] == "AST-011"


def test_update_asset_not_found(client):

    update_payload = {
        "asset_name": "Updated Laptop",
        "location": "Mumbai"
    }

    response = client.put(
        "/assets/9999",
        json=update_payload
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["success"] is False
    assert data["error"] == "AssetNotFoundError"
    assert "not found" in data["message"]  


def test_update_asset_negative_purchase_cost(client):

    payload = {
        "asset_name": "Monitor",
        "asset_tag": "AST-012",
        "category": "IT"
    }

    create_response = client.post("/assets", json=payload)

    asset_id = create_response.get_json()["id"]

    update_payload = {
        "purchase_cost": -1000
    }

    response = client.put(
        f"/assets/{asset_id}",
        json=update_payload
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "AssetValidationError"
    assert data["message"] == "Validation failed"

def test_update_asset_empty_payload(client):

    payload = {
        "asset_name": "Mouse",
        "asset_tag": "AST-013",
        "category": "IT"
    }

    create_response = client.post("/assets", json=payload)

    asset_id = create_response.get_json()["id"]

    response = client.put(
        f"/assets/{asset_id}",
        json={}
    )

    assert response.status_code == 400

def test_add_tags_to_asset(client):

    payload = {
        "asset_name": "Printer",
        "asset_tag": "AST-014",
        "category": "IT"
    }

    create_response = client.post("/assets", json=payload)

    asset_id = create_response.get_json()["id"]

    tag_payload = {
        "tags": ["Office", "Printing"]
    }

    response = client.post(
        f"/assets/{asset_id}/tags",
        json=tag_payload
    )

    assert response.status_code == 201

    data = response.get_json()
    tag_names = [tag["tag"] for tag in data["tags"]]

    assert "Office" in tag_names
    assert "Printing" in tag_names


def test_add_existing_active_tag(client):
    # Create an asset
    payload = {
        "asset_name": "Keyboard",
        "asset_tag": "AST-016",
        "category": "IT"
    }

    create_response = client.post("/assets", json=payload)
    asset_id = create_response.get_json()["id"]

    # Add the Office tag for the first time
    tag_payload = {
        "tags": ["Office"]
    }

    first_response = client.post(
        f"/assets/{asset_id}/tags",
        json=tag_payload
    )

    assert first_response.status_code == 201

    # Try adding the same active tag again
    second_response = client.post(
        f"/assets/{asset_id}/tags",
        json=tag_payload
    )

    assert second_response.status_code == 201

    data = second_response.get_json()

    # No duplicate tag should be created
    assert data["tags"] == [] 


def test_delete_asset_with_tags(client):

    # Create an asset
    payload = {
        "asset_name": "Keyboard",
        "asset_tag": "AST-017",
        "category": "IT"
    }

    create_response = client.post("/assets", json=payload)
    asset_id = create_response.get_json()["id"]

    # Add tags to the asset
    tag_payload = {
        "tags": ["Office", "Computer"]
    }

    tag_response = client.post(
        f"/assets/{asset_id}/tags",
        json=tag_payload
    )

    assert tag_response.status_code == 201

    # Delete the asset
    delete_response = client.delete(f"/assets/{asset_id}")

    assert delete_response.status_code == 200

    # Verify that the asset is no longer available
    get_response = client.get(f"/assets/{asset_id}")

    assert get_response.status_code == 404     



def test_update_asset_duplicate_asset_tag(client):
    # Create the first asset
    first_response = client.post("/assets", json={
        "asset_name": "Laptop",
        "asset_tag": "AST-018",
        "category": "IT"
    })
    assert first_response.status_code == 201

    # Create the second asset
    second_response = client.post("/assets", json={
        "asset_name": "Keyboard",
        "asset_tag": "AST-019",
        "category": "IT"
    })
    assert second_response.status_code == 201

    asset_id = second_response.get_json()["id"]

    # Try updating the second asset with the first asset's tag
    update_response = client.put(
        f"/assets/{asset_id}",
        json={"asset_tag": "AST-018"}
    )

    assert update_response.status_code == 409

    data = update_response.get_json()
    assert data["error"] == "DuplicateAssetError"

    # Verify the original asset tag was not changed
    get_response = client.get(f"/assets/{asset_id}")
    assert get_response.status_code == 200
    assert get_response.get_json()["asset_tag"] == "AST-019"


def test_repository_get_missing_asset_raises_exception(client):

    with pytest.raises(AssetNotFoundError):
        asset_repository.get_by_id(999) 


def test_deactivated_asset_not_returned_in_list(client):

    # Create an asset
    create_response = client.post("/assets", json={
        "asset_name": "Laptop",
        "asset_tag": "AST-020",
        "category": "IT",
        "location": "Pune"
    })

    assert create_response.status_code == 201

    asset_id = create_response.get_json()["id"]

    # Deactivate the asset
    delete_response = client.delete(f"/assets/{asset_id}")

    assert delete_response.status_code == 200

    # Get all assets
    response = client.get("/assets")

    assert response.status_code == 200

    data = response.get_json()

    # Check that the deactivated asset is not in the list
    assert all(asset["id"] != asset_id for asset in data)         


def test_get_tags_for_asset(client):

    # Create an asset
    create_response = client.post("/assets", json={
        "asset_name": "Laptop",
        "asset_tag": "AST-021",
        "category": "IT",
        "location": "Pune"
    })

    assert create_response.status_code == 201

    asset_id = create_response.get_json()["id"]

    # Add tags to the asset
    tag_response = client.post(f"/assets/{asset_id}/tags", json={
        "tags": ["Office", "Computer"]
    })

    assert tag_response.status_code == 201

    # Retrieve tags for the asset
    response = client.get(f"/assets/{asset_id}/tags")

    assert response.status_code == 200

    data = response.get_json()

    assert len(data["tags"]) == 2
    assert data["tags"][0]["tag"] == "Office"
    assert data["tags"][1]["tag"] == "Computer"
