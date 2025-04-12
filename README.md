# Metabase Web Service

A Sanic-based web service for managing and visualizing floor data with SVG generation, backed by PostgreSQL.

## Features

- **Health Check**: Endpoint (`/health-check`) to verify service status.
- **Floors List**: Retrieve floor data with associated locations (`/floors`).
- **Floor SVG**: Generate SVG images for specific floors with color-coded polygons based on sales data (`/floors/<number>/svg`).
- **Database Schema**: Initializes `mws_floor` and `mws_location` tables.
- **Sample Data**: Populates database with sample floor and location records.
- **Caching**: In-memory caching for SVG responses to improve performance.
- **External API Integration**: Fetches sales data from an Overlord API for SVG color coding.

## Project Structure

```text
.
├── metabase-ws.py             # Main Sanic application
├── metabase_ws/
│   ├── handlers.py            # Request handlers for floors and SVG generation
│   ├── init_db.py             # Database schema and sample data setup
│   └── remote.py              # External API client for sales data
├── Dockerfile                 # Docker image configuration
├── docker-compose.yaml        # Docker Compose setup for web and database
├── requirements.txt           # Production dependencies
├── requirements-dev.txt       # Development dependencies
└── init.db/sample.sql         # Sample SQL data for database initialization
```

## Requirements

- Python 3.13
- PostgreSQL

## Setup

1. **Clone Repository**:
   ```bash
   git clone https://github.com/gcca/metabase-ws.git
   cd metabase-ws
   ```

2. **Install Dependencies**:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure Environment**:
   Create a `.env` file with:
   ```
   MWS_PG_CONN=postgresql://user:password@localhost:5432/db
   MWS_OVERLORD_HOST=<overlord-api-host>
   MWS_OVERLORD_USERNAME=<username>
   MWS_OVERLORD_PASSWORD=<password>
   ```

4. **Run Locally**:
   ```bash
   sanic metabase-ws -H 0.0.0.0 -p 8000
   ```

## Docker Deployment

1. **Build and Run**:
   ```bash
   docker-compose up --build
   ```

2. **Access**:
   - Web service: `http://localhost:8000`
   - PostgreSQL: `localhost:5432` (user: `user`, password: `password`, database: `db`)

## Endpoints

- **GET /health-check**
  - Returns: `⚕️` (indicates service is running)
- **GET /floors**
  - Returns: JSON array of floors with IDs, numbers, display names, mime types, base64 images, and associated locations (ID, code, polygon points).
- **GET /floors/<number>/svg**
  - Parameters: `number` (integer, floor number)
  - Returns: SVG image with floor map and color-coded polygons based on sales data (cached for performance).

## Database Schema

- **mws_floor**:
  - `id`: SERIAL PRIMARY KEY
  - `number`: INTEGER NOT NULL
  - `display_name`: VARCHAR(255) NOT NULL
  - `mime_type`: VARCHAR(255) NOT NULL
  - `base64`: TEXT NOT NULL (base64-encoded image)

- **mws_location**:
  - `id`: SERIAL PRIMARY KEY
  - `code`: VARCHAR(255) NOT NULL
  - `polygon_points`: TEXT NOT NULL
  - `floor_id`: INTEGER NOT NULL (references `mws_floor.id`)

## SVG Generation

- Fetches floor base64 PNG and location polygon points from PostgreSQL.
- Queries Overlord API for sales data (`q1`, `q2`, `q3`, `q4`).
- Colors polygons:
  - `q1`: Red
  - `q2`: Orange
  - `q3`: Yellow
  - `q4`: Green
  - Other: Gray
- Combines PNG and polygons into an SVG response.

## Development

- **Linting**:
   ```bash
   pre-commit run --all-files
   ```

## Notes

- Replace placeholder `init.db/sample.sql` with valid SQL data.
- Ensure Overlord API credentials are valid for sales data retrieval.
- SVG caching is in-memory; consider persistent caching for production.
- Base64 image decoding may fail if invalid; validate inputs in production.

## License

GPL-3.0
