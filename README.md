Asset Register API

A RESTful API built using Python, Flask, Flask-SQLAlchemy, SQLAlchemy, Pydantic, and SQLite to manage an organization's assets.

The API supports creating, listing, filtering, retrieving, updating, tagging, and deactivating assets. It uses a structured application architecture with SQLAlchemy models, Python dataclasses, and Pydantic request validation.

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
Return appropriate HTTP status codes and validation errors.
Represent application-level asset data using Python dataclasses.
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

app.py           Creates the Flask application and registers Blueprints.

models.py        Defines SQLAlchemy database models and initializes the database.

migrate_db.py    Handles database schema migrations.

utils.py         Contains reusable utility and response functions.

assets/domain.py Contains the Asset dataclass and conversion methods.

assets/schemas/asset_schema.py Contains Pydantic models for request validation.

assets/repository.py  Centralizes database operations through the AssetRepository class.

assets/routes/asset_routes.py Defines asset API endpoints and handles HTTP requests.

assets/routes/tag_routes.py Defines asset tag endpoints.

requirements.txt   Lists project dependencies.

Future assignment steps will introduce repository.py and exceptions.py to further separate database operations and application error handling.

Prerequisites

Before running the project, ensure that you have installed:

Python 3.10 or later
Git
Visual Studio Code (recommended)
Postman
Installation and Setup
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


After successful activation, your terminal should display (.venv).

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

Base URL: http://127.0.0.1:5000

Keep the terminal open while testing the API.

API Endpoints

All endpoints use the following base URL:

text
http://127.0.0.1:5000


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

Required fields
asset_name
asset_tag
category
Optional fields
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
  "createdAt": "2026-10-28T10:00:00",
  "updatedAt": "2026-10-28T10:00:00",
  "createdBy": "system",
  "updatedBy": "system",
  "status": "Active"
}


The ID and timestamps are illustrative. Actual values are generated by the application or database.

2. List All Active Assets

Returns all assets whose status is Active.

Method: GET
Endpoint: /assets
Expected status: 200 OK

Example:

http
GET /assets


Returns an array of active assets.

If no active assets exist, the API returns an empty array.

3. Filter Assets by Category

Returns active assets belonging to a specified category.

Method: GET
Endpoint: /assets?type=IT%20Equipment
Expected status: 200 OK

Alternatively, in Postman, add the following parameter:

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

If the asset does not exist or has been deactivated, the API returns:

404 Not Found

Example error response:

json
{
  "error": "Asset not found"
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
Explicit null values are rejected for asset name, asset tag, and category.
Purchase cost cannot be negative.
Unknown fields, including status, are rejected.

The API uses Pydantic's model_dump(exclude_unset=True) to ensure that fields not supplied by the user remain unchanged.

The response contains the updated asset details.

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
Existing active tags for the asset are not added again.
Only active assets can receive new tags.
8. Deactivate an Asset

Soft-deletes an asset by changing its status to Inactive.

Method: DELETE
Endpoint: /assets/1
Expected status: 200 OK
Example response
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
The AssetRepository class provides the following methods:
Method	Responsibility
create()	Creates and saves a new asset.
get_by_id()	Retrieves an asset using its ID.
list()	Retrieves active assets with optional category and tag filters.
update()	Updates existing asset information.
deactivate()	Changes an asset's status to Inactive.
add_tags()	Adds tags to an asset while avoiding duplicate active tags.
get_tags()	Retrieves active tags associated with an asset.
Database Transaction Handling

All database transaction operations are handled inside the repository.

This includes:

db.session.add()
db.session.commit()
db.session.rollback()

The repository also handles SQLAlchemy database exceptions and re-raises them for the route layer to handle.

Benefits of the Repository Pattern
Separates database logic from API endpoints.
Reduces code duplication.
Makes database operations easier to maintain.
Improves code organization.
Makes future unit testing easier.

API routes interact with the database through the AssetRepository class rather than directly accessing SQLAlchemy sessions.

HTTP Status Codes
Status code	Description
200 OK	Request completed successfully.
201 Created	Asset or tags created successfully.
400 Bad Request	Invalid JSON or input data.
404 Not Found	Asset does not exist or is inactive.
409 Conflict	Duplicate asset tag or database constraint conflict.
500 Internal Server Error	Unexpected server error.

The actual status codes and error messages depend on the application's implemented error handling.

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

Verify that the returned HTTP status codes and JSON error messages match the implementation.

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


To commit and push changes:

bash
git add .
git commit -m "Describe your changes"
git push


Use feature branches and pull requests according to the project's contribution workflow.

Future Assignment Improvements

The following improvements are planned as part of the backend architecture assignment:

AssetRepository: Introduce an AssetRepository class to centralize all database operations and remove direct database access from API endpoints.
Custom Exceptions: Introduce custom exceptions such as AssetNotFoundError and DuplicateAssetError, with centralized error handling.
Mypy: Add static type checking to Python functions and classes, and ensure that mypy . passes without errors.
Automated Testing: Add automated unit and integration tests.
Authentication: Introduce authentication and role-based access control.
Pagination: Implement pagination for asset listing.
Database Migrations: Introduce Flask-Migrate for database schema management.
