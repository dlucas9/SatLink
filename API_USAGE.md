# SatLink REST API Usage Guide

## Overview

The SatLink REST API provides programmatic access to satellite link budget calculations through four main endpoints. The API runs on Flask and provides JSON responses for all calculations.

## Starting the API Server

```bash
cd /path/to/SatLink
source venv/bin/activate  # If using virtual environment
python satlink_api.py
```

The API will be available at: `http://localhost:5000`

## API Endpoints

### 1. Documentation Endpoint
- **URL**: `GET /`
- **Description**: Returns API documentation and available endpoints

```bash
curl http://localhost:5000/
```

### 2. Single Point Link Budget Calculation
- **URL**: `POST /api/single-point`
- **Description**: Calculate complete link budget for a single location

**Required Parameters:**
- `sat_long`: Satellite longitude (degrees)
- `freq`: Frequency (GHz)
- `eirp`: Satellite EIRP (dBW)
- `b_transponder`: Transponder bandwidth (MHz)
- `b_util`: Utilized bandwidth (MHz)
- `mod`: Modulation (e.g., "8PSK")
- `fec`: Forward Error Correction (e.g., "120/180")
- `site_lat`: Ground station latitude (degrees)
- `site_long`: Ground station longitude (degrees)

**Optional Parameters:**
- `hsat`: Satellite height (km, default: 35800)
- `ant_size`: Antenna size (m, default: 1.2)
- `ant_eff`: Antenna efficiency (default: 0.6)
- `lnb_gain`: LNB gain (dB, default: 55)
- `lnb_noise_temp`: LNB noise temperature (K, default: 20)
- `cable_loss`: Cable loss (dB, default: 4)
- `max_depoint`: Maximum depointing (degrees, default: 0.1)
- `p`: Probability for calculations (default: random)

**Example:**
```bash
curl -X POST http://localhost:5000/api/single-point \
  -H "Content-Type: application/json" \
  -d '{
    "sat_long": -70,
    "freq": 12,
    "eirp": 54,
    "b_transponder": 36,
    "b_util": 9,
    "mod": "8PSK",
    "fec": "120/180",
    "site_lat": -3.7,
    "site_long": -45.9
  }'
```

### 3. Multi-Point Availability Calculation
- **URL**: `POST /api/multi-point`
- **Description**: Calculate availability for multiple geographic points

**Required Parameters:**
- Same satellite parameters as single-point
- `points`: Array of objects with `lat`, `long`, and optional `name`

**Example:**
```bash
curl -X POST http://localhost:5000/api/multi-point \
  -H "Content-Type: application/json" \
  -d '{
    "sat_long": -70,
    "freq": 12,
    "eirp": 54,
    "b_transponder": 36,
    "b_util": 9,
    "mod": "8PSK",
    "fec": "120/180",
    "points": [
      {"lat": -3.7, "long": -45.9, "name": "Sao Luis"},
      {"lat": -15.8, "long": -47.9, "name": "Brasilia"},
      {"lat": -22.9, "long": -43.2, "name": "Rio de Janeiro"}
    ]
  }'
```

### 4. Single Point Antenna Size Analysis
- **URL**: `POST /api/single-point-antenna-size`
- **Description**: Analyze performance across different antenna sizes for one location

**Required Parameters:**
- Same as single-point calculation
- `min_ant_size`: Minimum antenna size (m, default: 0.5)
- `max_ant_size`: Maximum antenna size (m, default: 3.0)
- `step_size`: Step size for antenna range (m, default: 0.1)

**Example:**
```bash
curl -X POST http://localhost:5000/api/single-point-antenna-size \
  -H "Content-Type: application/json" \
  -d '{
    "sat_long": -70,
    "freq": 12,
    "eirp": 54,
    "b_transponder": 36,
    "b_util": 9,
    "mod": "8PSK",
    "fec": "120/180",
    "site_lat": -3.7,
    "site_long": -45.9,
    "min_ant_size": 0.8,
    "max_ant_size": 2.0,
    "step_size": 0.2
  }'
```

### 5. Multi-Point Antenna Size Analysis
- **URL**: `POST /api/multi-point-antenna-size`
- **Description**: Analyze antenna sizing for multiple locations

**Required Parameters:**
- Same satellite parameters as multi-point
- `points`: Array of geographic locations
- Antenna size range parameters (optional)

**Example:**
```bash
curl -X POST http://localhost:5000/api/multi-point-antenna-size \
  -H "Content-Type: application/json" \
  -d '{
    "sat_long": -70,
    "freq": 12,
    "eirp": 54,
    "b_transponder": 36,
    "b_util": 9,
    "mod": "8PSK",
    "fec": "120/180",
    "points": [
      {"lat": -3.7, "long": -45.9, "name": "Sao Luis"},
      {"lat": -15.8, "long": -47.9, "name": "Brasilia"}
    ],
    "min_ant_size": 1.0,
    "max_ant_size": 1.4,
    "step_size": 0.2
  }'
```

## Response Format

All endpoints return JSON responses with the following structure:

- `input_parameters`: Echo of input parameters used
- `results`: Calculation results (varies by endpoint)
- `error`: Error message (if any)

## Available Modulations and FEC

Check the `models/Modulation_dB.csv` file for available modulation and FEC combinations.

Common combinations:
- Modulation: "QPSK", "8PSK", "16APSK", "32APSK"
- FEC: "120/180", "132/180", "140/180", "154/180", etc.

## Error Handling

The API returns appropriate HTTP status codes:
- 200: Success
- 400: Bad Request (missing parameters, invalid data)
- 404: Endpoint not found
- 413: Request entity too large
- 500: Internal server error

## Notes

- All calculations use ITU-R recommendations for atmospheric modeling
- Results include availability percentages, SNR values, and detailed link budget parameters
- The API supports CORS for cross-origin requests
- Maximum request size is limited to 16MB
