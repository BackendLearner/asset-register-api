
from sqlalchemy import inspect, text

from app import app, db


AUDIT_COLUMNS = {
    "createdAt": "DATETIME",
    "updatedAt": "DATETIME",
    "createdBy": "VARCHAR(100)",
    "updatedBy": "VARCHAR(100)",
    "status": "VARCHAR(30)",
}

with app.app_context():
    inspector = inspect(db.engine)
    existing_tables = set(inspector.get_table_names())

    required_tables = ("assets", "asset_tags")
    missing_tables = [
        table for table in required_tables
        if table not in existing_tables
    ]

    if missing_tables:
        print(
            "Missing tables: "
            + ", ".join(missing_tables)
            + ". Start the app first."
        )
        raise SystemExit(1)

    with db.engine.begin() as connection:
        for table in required_tables:
            columns = {
                column["name"]
                for column in inspect(
                    connection
                ).get_columns(table)
            }

            for column_name, column_type in AUDIT_COLUMNS.items():
                if column_name not in columns:
                    connection.execute(
                        text(
                            f'ALTER TABLE "{table}" '
                            f'ADD COLUMN "{column_name}" '
                            f'{column_type}'
                        )
                    )
                    print(
                        f"Added {column_name} to {table}"
                    )

            connection.execute(
                text(
                    f"""
                    UPDATE "{table}"
                    SET
                        createdAt = COALESCE(
                            createdAt, CURRENT_TIMESTAMP
                        ),
                        updatedAt = COALESCE(
                            updatedAt, CURRENT_TIMESTAMP
                        ),
                        createdBy = COALESCE(
                            createdBy, 'system'
                        ),
                        updatedBy = COALESCE(
                            updatedBy, 'system'
                        ),
                        status = COALESCE(
                            status, 'Active'
                        )
                    """
                )
            )

    print("Database migration completed successfully.")
