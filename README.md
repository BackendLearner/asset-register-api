Asset Register API

A RESTful API built using Python, Flask, Flask-SQLAlchemy, SQLAlchemy, Pydantic, and SQLite to manage an organization's assets.

The API supports creating, listing, filtering, retrieving, updating, tagging, and deactivating assets. It follows a structured application architecture using SQLAlchemy models, Python dataclasses, Pydantic request validation, the Repository Pattern, and custom exception handling.

Features
Create and manage assets.
List all active assets.
Filter assets by category and tag.
Retrieve an asset by its ID.
Update existing asset details.
Add tags to assets.
Soft-delete assets by changing their status to Inactive.
Store asset data in a SQLite database using SQLAlchemy.
Track creation and modification timestamps and user information.
Validate request data using Pydantic v2.
Represent application-level asset data using Python dataclasses.
Centralize database operations using the Repository Pattern.
Handle application errors using custom exceptions.
Return appropriate HTTP status codes and structured JSON error responses.
Technologies Used
Python 3.10+
Flask
Flask-SQLAlchemy
SQLAlchemy
SQLite
Pydantic v2
python-dotenv
Postman
Git and GitHub
Project Structure
text
asset-register-api/
│
├── app.py
├── models.py
├── migrate_db.py
├── utils.py
├── requirements.txt
├── README.md
│
├── exceptions/
│   ├── __init__.py
│   └── asset_exceptions.py
│
├── assets/
│   ├── __init__.py
│   ├── domain.py
│   ├── repository.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── asset_schema.py
│   │
│   └── routes/
│       ├── __init__.py
│       ├── asset_routes.py
│       └── tag_routes.py
│
└── postman/
    └── Asset-Register-API.postman_collection.json

File Responsibilities

app.py	Creates the Flask application, initializes the database, registers Blueprints, and configures global error handlers.
models.py	Defines SQLAlchemy database models and initializes the database.
migrate_db.py	Handles database schema migrations.
utils.py	Contains reusable utility and response functions.
assets/domain.py	Contains the Asset dataclass and conversion methods.
assets/schemas/asset_schema.py	Contains Pydantic models for request validation.
assets/repository.py	Centralizes database operations through the AssetRepository class.
assets/routes/asset_routes.py	Defines asset API endpoints and handles HTTP requests.
assets/routes/tag_routes.py	Defines asset tag endpoints.
exceptions/asset_exceptions.py	Defines custom application exceptions.
requirements.txt	Lists project dependencies.

Installation and Setup
Prerequisites

Before running the project, ensure that you have installed:

Python 3.10 or later
Git
Visual Studio Code (recommended)
Postman

1. Clone the repository
bash
git clone https://github.com/BackendLearner/asset-register-api.git
cd asset-register-api

2. Create a virtual environment

On Windows PowerShell:

powershell
python -m venv .venv

3. Activate the virtual environment
powershell
.\.venv\Scripts\Activate.ps1


If PowerShell prevents script execution, use:

powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass


Then activate the virtual environment again.

4. Install dependencies
powershell
python -m pip install -r requirements.txt


Verify the installed packages:

powershell
python -m pip check

5. Configure environment variables

Create a .env file in the project root directory.

Add:

env
DATABASE_URL=sqlite:///assets.db


The application uses assets.db by default if DATABASE_URL is not configured.

Important: Do not commit your .env file or local database files to Git.

6. Initialize the database

Run:

powershell
python app.py


If the application calls db.create_all() when started, it will create any missing tables.

For an existing database requiring the audit-column migration, stop the application and run:

powershell
python migrate_db.py


Run the migration only when required.

7. Start the API
powershell
python app.py


The development server should be available at:

Base URL: http://127.0.0.1:5001

Keep the terminal open while testing the API.

API Endpoints

All endpoints use the following base URL:

text
http://127.0.0.1:5001


For requests with a body, select Body → raw → JSON in Postman.

1. Create an Asset

Creates a new asset.

Method: POST
Endpoint: /assets
Expected status: 201 Created
Request body
json
{
  "asset_name": "Dell Laptop",
  "asset_tag": "LAP-001",
  "category": "IT Equipment",
  "location": "Office Room 101",
  "purchase_date": "2026-01-15",
  "purchase_cost": 65000
}


Required fields:

asset_name
asset_tag
category

Optional fields:

location
purchase_date
purchase_cost

The status field is not accepted from the request. Every newly created asset automatically receives the status Active.

Validation rules
Asset name must contain between 1 and 100 characters.
Asset tag must contain between 1 and 50 characters.
Category must contain between 1 and 100 characters.
Location can contain a maximum of 100 characters.
Purchase date must use the YYYY-MM-DD format.
Purchase cost must be greater than or equal to zero.
Asset tag must be unique.
Additional fields not defined in the schema are rejected.
Example response
json
{
  "id": 1,
  "asset_name": "Dell Laptop",
  "asset_tag": "LAP-001",
  "category": "IT Equipment",
  "location": "Office Room 101",
  "purchase_date": "2026-01-15",
  "purchase_cost": 65000.0,
  "status": "Active"
}


The ID and timestamps are illustrative. Actual values are generated by the application or database.

2. List All Active Assets

Returns all assets whose status is Active.

Method: GET
Endpoint: /assets
Expected status: 200 OK
http
GET /assets


If no active assets exist, the API returns an empty array.

3. Filter Assets by Category

Returns active assets belonging to a specified category.

Method: GET
Endpoint: /assets?type=IT%20Equipment
Expected status: 200 OK

Alternatively, in Postman:

Key	Value
type	IT Equipment
4. Filter Assets by Tag

Returns active assets associated with the specified active tag.

Method: GET
Endpoint: /assets?tag=urgent
Expected status: 200 OK

If no assets match the tag, the API returns an empty array.

5. Retrieve an Asset by ID

Retrieves a single active asset using its ID.

Method: GET
Endpoint: /assets/1
Expected status: 200 OK

Replace 1 with the actual asset ID.

If the asset does not exist or has been deactivated, the API raises an AssetNotFoundError.

Expected status: 404 Not Found

Example error response:

json
{
  "success": false,
  "error": "AssetNotFoundError",
  "message": "Active asset with ID 9999 not found"
}

6. Update an Asset

Updates the specified fields of an existing active asset.

Method: PUT
Endpoint: /assets/1
Expected status: 200 OK
Request body
json
{
  "location": "Office Room 202",
  "purchase_cost": 62000
}

Update behavior

The API supports partial updates. Users only need to provide the fields they want to change.

The following fields can be updated:

asset_name
asset_tag
category
location
purchase_date
purchase_cost

The status field cannot be updated through the PUT endpoint.

Validation rules
All update fields are optional.
Only supplied fields are updated.
Empty update requests are rejected.
Explicit null values are rejected for required fields.
Purchase cost cannot be negative.
Unknown fields, including status, are rejected.

The API uses Pydantic's model_dump(exclude_unset=True) to ensure that fields not supplied by the user remain unchanged.

7. Add Tags to an Asset

Associates one or more tags with an existing active asset.

Method: POST
Endpoint: /assets/1/tags
Expected status: 201 Created
Request body
json
{
  "tags": [
    "urgent",
    "IT",
    "warranty"
  ]
}

Validation rules
Tags must be a non-empty list.
Every tag must be a non-empty string.
A maximum of 50 tags can be submitted at once.
Duplicate tags within the request are removed.
Existing active tags for the asset are not added again.
Only active assets can receive new tags.
8. Get Asset Tags

Retrieves all active tags associated with an asset.

Method: GET
Endpoint: /assets/1/tags
Expected status: 200 OK

Example response:

json
{
  "asset_id": 1,
  "tags": [
    "urgent",
    "IT",
    "warranty"
  ]
}

9. Deactivate an Asset

Soft-deletes an asset by changing its status to Inactive.

Method: DELETE
Endpoint: /assets/1
Expected status: 200 OK

Example response:

json
{
  "message": "Asset deactivated successfully",
  "id": 1,
  "status": "Inactive"
}


This operation does not permanently delete the database record.

The asset remains stored with its status changed to Inactive.

Deactivated assets are excluded from list and filter results and cannot be retrieved through the single-asset endpoint.

Request Validation Using Pydantic

The application uses Pydantic v2 to validate incoming API request data.

Request validation is separated into dedicated schema classes located in:

text
assets/
└── schemas/
    └── asset_schema.py

AssetCreate

The AssetCreate model validates asset creation requests.

It checks:

Required fields.
String minimum and maximum lengths.
Optional fields.
Purchase date format.
Non-negative purchase cost.

Validation is performed using:

python
data = AssetCreate.model_validate(
    request.get_json(silent=True)
)

AssetUpdate

The AssetUpdate model validates partial asset updates.

All fields are optional, allowing users to update only the required fields.

The application uses:

python
update_data = data.model_dump(exclude_unset=True)


This ensures that only fields supplied by the user are updated.

Handling validation errors

Pydantic validation errors are handled using:

python
except ValidationError as e:
    return jsonify({"errors": e.errors()}), 400


Invalid request data returns HTTP 400 Bad Request with validation details.

The schema also uses extra="forbid" to reject fields that are not defined in the request model.

Domain Layer Using Dataclasses

The application uses Python dataclasses to represent asset information independently of the database models.

The dataclass is located in:

text
assets/domain.py


The Asset dataclass provides:

from_dict(): Creates an Asset object from dictionary data.
to_dict(): Converts an Asset object into dictionary format.
field(default_factory=list): Provides a separate tags list for each Asset instance.

This separates application-level asset data from SQLAlchemy database models.

Repository Layer Using AssetRepository

The application uses the Repository Pattern to separate database operations from API route handling.

The repository is located in:

text
assets/
└── repository.py


The AssetRepository class is responsible for communicating with the database using SQLAlchemy.

It centralizes database operations so that API endpoints do not directly access db.session.

Repository Methods
Method	Responsibility
create()	Creates and saves a new asset.
get_by_id()	Retrieves an active asset using its ID.
list()	Retrieves active assets with optional category and tag filters.
update()	Updates existing asset information.
deactivate()	Changes an asset's status to Inactive.
add_tags()	Adds tags to an asset while avoiding duplicate active tags.
get_tags()	Retrieves active tags associated with an asset.
Database Transaction Handling

All database transaction operations are handled inside the repository.

This includes:

python
db.session.add()
db.session.commit()
db.session.rollback()


The repository catches SQLAlchemy exceptions and rolls back failed transactions.

It also converts database constraint violations into application-specific exceptions where appropriate.

For example:

python
except IntegrityError as exc:
    db.session.rollback()

    raise DuplicateAssetError(
        f"Asset tag '{asset.asset_tag}' already exists"
    ) from exc


This prevents database-specific exceptions from leaking into the API layer.

Benefits of the Repository Pattern
Separates database logic from API endpoints.
Reduces code duplication.
Makes database operations easier to maintain.
Improves code organization.
Makes future unit testing easier.

API routes interact with the database through the AssetRepository class rather than directly accessing SQLAlchemy sessions.

Custom Exception Handling

The application uses custom exceptions to handle application-level errors in a structured and centralized way.

Custom exceptions are defined in:

text
exceptions/
├── __init__.py
└── asset_exceptions.py

Custom Exception Classes

The application defines three custom exception classes.

1. AssetError

The base exception for all asset-related application errors.

python
class AssetError(Exception):
    pass

2. AssetNotFoundError

Raised when an asset does not exist or is inactive.

python
class AssetNotFoundError(AssetError):
    pass

3. DuplicateAssetError

Raised when an asset violates a uniqueness or database constraint.

python
class DuplicateAssetError(AssetError):
    pass

How Custom Exceptions Work

The repository raises custom exceptions when an application-level error occurs.

For example, when an asset ID does not exist:

python
if asset is None or asset.status != "Active":
    raise AssetNotFoundError(
        f"Active asset with ID {asset_id} not found"
    )


When a duplicate asset tag is submitted:

python
raise DuplicateAssetError(
    f"Asset tag '{asset.asset_tag}' already exists"
) from exc


The repository is responsible for identifying and raising these exceptions.

The Flask application is responsible for converting them into HTTP responses.

Centralized Error Handling in Flask

Custom exceptions are registered using Flask's @app.errorhandler() decorator in app.py.

Example:

python
@app.errorhandler(AssetNotFoundError)
def handle_asset_not_found(error):
    return jsonify({
        "success": False,
        "error": "AssetNotFoundError",
        "message": str(error)
    }), 404


Duplicate asset errors:

python
@app.errorhandler(DuplicateAssetError)
def handle_duplicate_asset(error):
    return jsonify({
        "success": False,
        "error": "DuplicateAssetError",
        "message": str(error)
    }), 409


Other asset-related errors:

python
@app.errorhandler(AssetError)
def handle_asset_error(error):
    return jsonify({
        "success": False,
        "error": "AssetError",
        "message": str(error)
    }), 400


Unexpected database errors are also handled centrally using:

python
@app.errorhandler(SQLAlchemyError)
def handle_database_error(error):
    app.logger.exception("Database error occurred")

    return jsonify({
        "success": False,
        "error": "DatabaseError",
        "message": "An internal database error occurred"
    }), 500

Benefits of Custom Exceptions
Provides meaningful application-specific errors.
Separates business errors from database errors.
Avoids repeating error-handling logic in API endpoints.
Keeps route functions cleaner.
Makes HTTP status code handling consistent.
Improves application maintainability.

Instead of handling every exception separately inside each endpoint, Flask's centralized error handlers convert raised exceptions into appropriate HTTP responses.

HTTP Status Codes
Status Code	Description
200 OK	Request completed successfully.
201 Created	Asset or tags created successfully.
400 Bad Request	Invalid JSON, validation failure, or other asset application error.
404 Not Found	Asset does not exist or is inactive.
409 Conflict	Duplicate asset tag or database constraint conflict.
500 Internal Server Error	Unexpected database or server error.
Testing with Postman
1. Import the Postman collection
Start the Flask application using python app.py.
Open Postman.
Select Import.
Choose Files.
Select postman/Asset-Register-API.postman_collection.json.
Import the collection.
2. Test the endpoints

Run the requests in the following order:

Create Asset — POST /assets
List Assets — GET /assets
Filter Assets by Type — GET /assets?type=IT%20Equipment
Filter Assets by Tag — GET /assets?tag=urgent
Get Asset by ID — GET /assets/1
Update Asset — PUT /assets/1
Add Asset Tags — POST /assets/1/tags
Get Asset Tags — GET /assets/1/tags
Deactivate Asset — DELETE /assets/1
Get Asset by ID Again — verify that the deactivated asset returns 404.

Replace 1 with a valid asset ID from your database.

Use a unique asset_tag when creating each new asset.

3. Test invalid requests

Test the following scenarios:

Creating an asset without required fields.
Sending an invalid JSON request body.
Providing an invalid purchase date.
Providing a negative purchase cost.
Providing an asset name longer than 100 characters.
Creating an asset with a duplicate asset tag.
Sending an unknown field in a create request.
Sending an empty update request.
Sending null for a required update field.
Attempting to update the status manually.
Retrieving an asset using a nonexistent ID.
Updating an inactive asset.
Adding tags to an inactive asset.
Retrieving an asset after deactivation.
4. Test Custom Exception Responses

Verify that custom exceptions return the correct HTTP status codes and JSON responses.

Test 404 – AssetNotFoundError

Request:

http
GET /assets/9999


Expected response:

json
{
  "success": false,
  "error": "AssetNotFoundError",
  "message": "Active asset with ID 9999 not found"
}

Test 409 – DuplicateAssetError

Create an asset using an asset_tag that already exists.

Expected response:

json
{
  "success": false,
  "error": "DuplicateAssetError",
  "message": "Asset tag 'AST-017' already exists"
}

Test 400 – Pydantic Validation Error

Request body:

json
{
  "asset_name": "",
  "asset_tag": "",
  "category": ""
}


Expected status: 400 Bad Request

The response contains Pydantic validation details for the invalid fields.

Run the complete Postman collection using Collection Runner after significant changes.

Database and Audit Fields

The application uses SQLite to store asset information.

The asset records include audit fields:

Field	Description
createdAt	Date and time when the asset was created.
updatedAt	Date and time when the asset was last modified.
createdBy	User who created the asset.
updatedBy	User who last modified the asset.
status	Current asset status, such as Active or Inactive.

The example responses use system as the user value. This reflects the current API behavior and does not imply authentication or individual user tracking.

Git and GitHub

Before committing changes, ensure that generated files and local configuration are excluded from version control.

Example .gitignore entries:

gitignore
.venv/
__pycache__/
*.py[cod]
.env
*.db
instance/
.pytest_cache/

Creating a Feature Branch and Pull Request

Create a new feature branch:

bash
git checkout -b feature/custom-exception-handling


Stage your changes:

bash
git add .


Commit your changes:

bash
git commit -m "Add repository pattern and custom exception handling"


Push your feature branch:

bash
git push -u origin feature/custom-exception-handling


Then:

Open your GitHub repository.
Select Compare & Pull Request.
Set the base branch to main (or your project's target branch).
Set the compare branch to feature/custom-exception-handling.
Add a meaningful pull request title and description.
Create the pull request.
Review the changes before merging.
Future Assignment Improvements

The following improvements can be introduced in future development:

Mypy: Add static type checking to Python functions and classes.
Automated Testing: Add automated unit and integration tests using pytest.
Authentication: Introduce authentication and role-based access control.
Pagination: Implement pagination for asset listing.
Database Migrations: Introduce Flask-Migrate for database schema management.
Logging: Implement structured application logging.
API Documentation: Add Swagger/OpenAPI documentation.
Current Implementation Summary

The Asset Register API currently includes:

Flask Blueprint-based application structure.
SQLAlchemy database models.
Python dataclasses for domain representation.
Pydantic v2 request validation.
Repository Pattern for database operations.
Custom exceptions for application errors.
Centralized Flask error handlers.
SQLite database integration.
Postman API testing.