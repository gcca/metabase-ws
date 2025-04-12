import psycopg
from sanic import Sanic
from sanic.log import logger


async def CreateSchema(app: Sanic) -> None:
    """Create database schema for mws_location and mws_tenant tables.

    Args:
        app (Sanic): The Sanic application instance containing PostgreSQL connection configuration.

    Creates two tables:
    - mws_location: Stores location data with id, floor_number, display_name, mime_type, and base64 fields.
    - mws_tenant: Stores tenant data with id, code, polygon_points, and location_id fields, referencing mws_location.

    Commits the transaction after executing the schema creation queries.
    """
    logger.info("Creating database schema...")
    pg_conn = app.config.PG_CONN
    async with await psycopg.AsyncConnection.connect(pg_conn) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                CREATE TABLE IF NOT EXISTS mws_floor (
                    id SERIAL PRIMARY KEY,
                    number INTEGER NOT NULL,
                    display_name VARCHAR(255) NOT NULL,
                    mime_type VARCHAR(255) NOT NULL,
                    base64 TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS mws_location (
                    id SERIAL PRIMARY KEY,
                    code VARCHAR(255) NOT NULL,
                    polygon_points TEXT NOT NULL,
                    floor_id INTEGER NOT NULL,
                    FOREIGN KEY (floor_id) REFERENCES mws_floor(id)
                );
                """
            )
            await conn.commit()


async def CreateSampleData(app: Sanic) -> None:
    """Insert sample data into mws_floor and mws_location tables.

    Args:
        app (Sanic): The Sanic application instance containing PostgreSQL connection configuration.

    Inserts:
    - Two records into mws_floor with sample floor data, including display names, mime types, and base64-encoded images.
    - Three records into mws_location with sample tenant codes, polygon points, and associated location IDs.

    Commits the transaction after executing the insert queries.

    Note: The base64 values are truncated placeholders and should be replaced with valid data.
    """
    logger.info("Creating sample data...")
    pg_conn = app.config.PG_CONN
    async with await psycopg.AsyncConnection.connect(pg_conn) as conn:
        async with conn.cursor() as cur:
            with open("init.db/sample.sql") as sample_file:
                await cur.execute(sample_file.read().encode())
            await conn.commit()
