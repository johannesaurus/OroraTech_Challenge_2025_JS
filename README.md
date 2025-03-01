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

## Running the API
To start the FastAPI server, run:
```sh
uvicorn api:app --host 0.0.0.0 --port 8080 --reload
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

## License
NA

## Author
Johannes Seelig

