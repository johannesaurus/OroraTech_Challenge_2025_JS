# OroraTech Wildfire Tech Challenge - API

## Overview
This FastAPI-based project provides an API for retrieving and managing wildfire detection data. The API supports querying hotspots based on geospatial constraints, timestamps, and unique IDs.

## Features
- Retrieve wildfire detections within a polygon or bounding box.
- Filter detections by timestamp range.
- Retrieve wildfire detections by unique ID.
- Add new wildfire detections.
- Delete wildfire detections.

## Changelog

### v 0.0.2.
- Release Date: 2025.03.03
- Switch from mockDB to SQLite

### v 0.0.1
- Release Date: 2025.03.01
- Initial push

## Installation

### Prerequisites
- Python 3.8+
- pip

### Setup
1. Clone the repository:
   ```sh
   git clone <repo_url>
   cd <repo_folder>
   ```
2. Create a virtual environment and activate it:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
   (pip freeze > requirements.txt)

## Running the API
To start the FastAPI server, run:
```sh
uvicorn api.api:app --host 0.0.0.0 --port 8080 --reload

```
By default, the API will be available at:
- Swagger UI: [http://127.0.0.1:8080/docs](http://127.0.0.1:8080/docs)
- ReDoc UI: [http://127.0.0.1:8080/redoc](http://127.0.0.1:8080/redoc)

## API Endpoints
### 1. Get all hotspots
```
GET /hotspots
```
**Query Parameters:**
- `polygon` (optional): GeoJSON Polygon as a string.
- `min_lat`, `max_lat`, `min_lon`, `max_lon` (optional): Bounding box coordinates.
- `start_timestamp`, `end_timestamp` (optional): Timestamp range in ISO format.

**Response:**
Returns a GeoJSON `FeatureCollection` with detected hotspots.

### 2. Get a hotspot by ID
```
GET /hotspots/{id}
```
**Path Parameter:**
- `id` (int): Unique identifier of the hotspot.

**Response:**
Returns a GeoJSON `Feature` with the detected hotspot details.

### 3. Add a new hotspot
```
POST /hotspots/add
```
**Body Parameters:**
- `latitude` (float)
- `longitude` (float)
- `timestamp_start` (datetime, ISO format)
- `timestamp_end` (datetime, ISO format)

**Response:**
Confirmation message with the assigned ID.

### 4. Delete a hotspot
```
DELETE /hotspots/remove?id={id}
```
**Query Parameter:**
- `id` (int): ID of the hotspot to delete.

**Response:**
Confirmation message upon successful deletion.

### Example
```
http://127.0.0.1:8080/hotspots?polygon={"coordinates":[[[-68.48242560897704,-15.539147107838772],[-68.48242560897704,-16.615626834992582],[-67.31945863367787,-16.615626834992582],[-67.31945863367787,-15.539147107838772],[-68.48242560897704,-15.539147107838772]]],"type":"Polygon"}&start_timestamp=2023-11-16T19:13:14.364950&end_timestamp=2023-11-20T19:13:14.364950
```

## Development Workflow
### Branching Strategy
This project follows a structured branching strategy:
- `main`: Stable branch for major version releases.
- `working`: Active development branch where updates and fixes are merged before going to `main`.
- `fix/*`: Feature/fix branches created for specific changes, merged into `working` before final deployment.

### Creating a Pull Request (PR)
1. **Create a feature/fix branch:**
   ```sh
   git checkout -b fix/bug-description
   ```
2. **Make changes and commit:**
   ```sh
   git add .
   git commit -m "Fix: resolved bug in hotspot retrieval"
   ```
3. **Push the branch:**
   ```sh
   git push origin fix/bug-description
   ```
4. **Open a PR on GitHub:**
   - Go to the repository.
   - Click "Compare & pull request".
   - Set base as `working`, add a description, and submit.
   - Request a review and merge upon approval.
5. **Merge `working` into `main` for major releases:**
   ```sh
   git checkout main
   git merge working
   git push origin main
   ```

## Notes
Create/Run requirements.txt:
```sh
pip freeze > requirements.txt
pip install -r requirements.txt
```

Format with black:
```sh
black . > logs/black.log 2>&1
```

Lint with Ruff:
```sh
ruff check . --fix > logs/ruff.log 2>&1
```

Run MyPy:
```sh
mypy . --exclude "because_postgres_is_not_playing_along|data|logs|other" > logs/mypy.log 2>&1
```

Run PyTest + create log and html:
```sh
set PYTHONPATH=.
pytest --cov=api --cov=fcts --cov=models --cov-report=html:logs/coverage_html > logs/pytest.log 2>&1
```

DB: creates fire_detections.db
```sh
python models/model_db.py (inits db)
python fcts/load_csv.py (fills db)
```

## License
NA


## Author
Johannes Seelig

