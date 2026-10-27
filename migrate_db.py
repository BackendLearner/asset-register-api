
from sqlalchemy import inspect, text

from app import app, db


NEW_COLUMNS = {
    "createdAt": "DATETIME",
    "updatedAt": "DATETIME",
    "createdBy": "VARCHAR(100)",
    "updatedBy": "VARCHAR(100)",
}

with app.app_context():
    inspector = inspect(db.engine)
    existing_tables = inspector.get_table_names()

    if "assets" not in existing_tables:
        print("Assets table does not exist. Start the app first.")
        raise SystemExit(1)

    existing_columns = {
        column["name"]
        for column in inspector.get_columns("assets")
    }

    with db.engine.begin() as connection:
        for column_name, column_type in NEW_COLUMNS.items():
            if column_name not in existing_columns:
                connection.execute(text(
                    f"ALTER TABLE assets ADD COLUMN "
                    f'"{column_name}" {column_type}'
                ))
                print(f"Added column: {column_name}")

        connection.execute(text("""
            UPDATE assets
            SET createdAt = COALESCE(
                createdAt, CURRENT_TIMESTAMP
            ),
            updatedAt = COALESCE(
                updatedAt, CURRENT_TIMESTAMP
            ),
            createdBy = COALESCE(createdBy, 'system'),
            updatedBy = COALESCE(updatedBy, 'system')
        """))

    print("Database migration completed successfully.")
