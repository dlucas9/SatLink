# SatLink API Frontend Developer Manual

## Overview

This manual provides comprehensive documentation for frontend developers to integrate with the SatLink REST API. The API provides satellite link budget calculations, multi-point availability analysis, and antenna sizing functionality.

## Base Configuration

### API Server
- **Base URL**: `http://localhost:5000`
- **Protocol**: HTTP/HTTPS
- **Content-Type**: `application/json`
- **CORS**: Enabled for cross-origin requests

### Starting the API Server
```bash
python satlink_api.py
```

## API Endpoints

### 1. Single Point Link Budget Calculation

**Endpoint**: `POST /api/single-point`

**Description**: Calculates satellite link budget for a single geographic location including atmospheric attenuation, system parameters, and availability metrics.

#### Request Parameters

| Parameter | Type | Required | Description | Valid Values |
|-----------|------|----------|-------------|--------------|
| `sat_long` | float | Yes | Satellite longitude (degrees) | -180 to 180 |
| `freq` | float | Yes | Frequency (GHz) | 1 to 100 |
| `eirp` | float | Yes | Satellite EIRP (dBW) | 0 to 100 |
| `hsat` | float | No | Satellite height (km) | Default: 35786 |
| `b_transponder` | float | Yes | Transponder bandwidth (MHz) | 0.1 to 1000 |
| `b_util` | float | Yes | Utilized bandwidth (MHz) | 0.1 to 1000 |
| `mod` | string | Yes | Modulation type | "QPSK", "8PSK", "16APSK", "32APSK" |
| `rolloff` | float | No | Roll-off factor | Default: 0.35 (0.1 to 0.5) |
| `fec` | string | Yes | Forward Error Correction | "90/180", "96/180", "100/180", "104/180", "116/180", "124/180", "128/180", "132/180", "140/180", "154/180", "18/30", "20/30", "21/30", "23/30", "25/30", "26/30", "28/30", "29/30" |
| `site_lat` | float | Yes | Ground station latitude (degrees) | -90 to 90 |
| `site_long` | float | Yes | Ground station longitude (degrees) | -180 to 180 |
| `ant_size` | float | No | Antenna diameter (meters) | Default: 1.2 |
| `ant_eff` | float | No | Antenna efficiency (%) | Default: 65 (0 to 100) |
| `coupling_loss` | float | No | Coupling loss (dB) | Default: 0.2 |
| `polarization_loss` | float | No | Polarization loss (dB) | Default: 0.5 |
| `lnb_gain` | float | No | LNB gain (dB) | Default: 55 |
| `lnb_noise_temp` | float | No | LNB noise temperature (K) | Default: 25 |
| `cable_loss` | float | No | Cable loss (dB) | Default: 1 |
| `desfoc_max` | float | No | Maximum defocusing (dB) | Default: 0.5 |

#### Request Example
```javascript
const requestData = {
  sat_long: -70,
  freq: 12,
  eirp: 54,
  b_transponder: 36,
  b_util: 9,
  mod: "8PSK",
  fec: "120/180",
  site_lat: -3.7,
  site_long: -45.9,
  ant_size: 1.2
};

fetch('http://localhost:5000/api/single-point', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(requestData)
})
.then(response => response.json())
.then(data => console.log(data));
```

#### Response Format
```json
{
  "status": "success",
  "input_parameters": {
    "satellite": { /* satellite parameters */ },
    "ground_station": { /* ground station parameters */ },
    "reception": { /* reception parameters */ }
  },
  "results": {
    "atmospheric_attenuation": {
      "gaseous_attenuation_db": 0.123,
      "cloud_attenuation_db": 0.456,
      "rain_attenuation_db": 2.789,
      "scintillation_attenuation_db": 0.234,
      "total_atmospheric_attenuation_db": 3.602
    },
    "link_budget": {
      "free_space_loss_db": 205.67,
      "antenna_gain_db": 39.85,
      "system_noise_temperature_k": 156.78,
      "g_t_db_k": 16.89,
      "snr_clear_sky_db": 24.73,
      "snr_with_attenuation_db": 21.13,
      "snr_threshold_db": 7.23,
      "link_margin_db": 13.9
    },
    "system_parameters": {
      "elevation_angle_deg": 45.67,
      "azimuth_angle_deg": 123.45,
      "link_distance_km": 38456.78,
      "power_flux_density_dbw_m2": -123.45
    },
    "availability": {
      "percentage": 99.986,
      "unavailability_percentage": 0.014,
      "outage_time_minutes_per_year": 73.58
    }
  }
}
```

### 2. Multi-Point Availability Calculation

**Endpoint**: `POST /api/multi-point`

**Description**: Calculates availability for multiple geographic locations with the same satellite and reception parameters.

#### Request Parameters

All satellite and reception parameters from single-point endpoint, plus:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `locations` | array | Yes | Array of location objects |

**Location Object Structure**:
```json
{
  "name": "Location Name",
  "lat": -12.34,
  "long": -56.78
}
```

#### Request Example
```javascript
const requestData = {
  sat_long: -70,
  freq: 12,
  eirp: 54,
  b_transponder: 36,
  b_util: 9,
  mod: "8PSK",
  fec: "120/180",
  locations: [
    { "name": "São Paulo", "lat": -23.55, "long": -46.64 },
    { "name": "Rio de Janeiro", "lat": -22.91, "long": -43.17 },
    { "name": "Brasília", "lat": -15.78, "long": -47.93 }
  ]
};
```

#### Response Format
```json
{
  "status": "success",
  "input_parameters": { /* same as single-point */ },
  "results": [
    {
      "location": {
        "name": "São Paulo",
        "lat": -23.55,
        "long": -46.64
      },
      "atmospheric_attenuation": { /* same structure as single-point */ },
      "link_budget": { /* same structure as single-point */ },
      "system_parameters": { /* same structure as single-point */ },
      "availability": { /* same structure as single-point */ }
    }
    /* ... more locations */
  ]
}
```

### 3. Single Point Antenna Sizing

**Endpoint**: `POST /api/single-point-antenna-size`

**Description**: Analyzes performance across different antenna sizes for a single location.

#### Request Parameters

All single-point parameters except `ant_size`, plus:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ant_size_min` | float | Yes | Minimum antenna size (meters) |
| `ant_size_max` | float | Yes | Maximum antenna size (meters) |
| `ant_size_step` | float | No | Step size (meters). Default: 0.1 |

#### Request Example
```javascript
const requestData = {
  sat_long: -70,
  freq: 12,
  eirp: 54,
  b_transponder: 36,
  b_util: 9,
  mod: "8PSK",
  fec: "120/180",
  site_lat: -3.7,
  site_long: -45.9,
  ant_size_min: 0.6,
  ant_size_max: 2.4,
  ant_size_step: 0.2
};
```

#### Response Format
```json
{
  "status": "success",
  "input_parameters": { /* parameters used */ },
  "results": [
    {
      "antenna_size_m": 0.6,
      "atmospheric_attenuation": { /* attenuation data */ },
      "link_budget": { /* link budget data */ },
      "system_parameters": { /* system data */ },
      "availability": { /* availability data */ }
    }
    /* ... more antenna sizes */
  ]
}
```

### 4. Multi-Point Antenna Sizing

**Endpoint**: `POST /api/multi-point-antenna-size`

**Description**: Analyzes performance across different antenna sizes for multiple locations.

#### Request Parameters

Combination of multi-point locations and antenna sizing parameters.

#### Request Example
```javascript
const requestData = {
  sat_long: -70,
  freq: 12,
  eirp: 54,
  b_transponder: 36,
  b_util: 9,
  mod: "8PSK",
  fec: "120/180",
  locations: [
    { "name": "São Paulo", "lat": -23.55, "long": -46.64 },
    { "name": "Rio de Janeiro", "lat": -22.91, "long": -43.17 }
  ],
  ant_size_min: 0.6,
  ant_size_max: 1.8,
  ant_size_step: 0.3
};
```

#### Response Format
```json
{
  "status": "success",
  "input_parameters": { /* parameters used */ },
  "results": [
    {
      "location": {
        "name": "São Paulo",
        "lat": -23.55,
        "long": -46.64
      },
      "antenna_analysis": [
        {
          "antenna_size_m": 0.6,
          "atmospheric_attenuation": { /* data */ },
          "link_budget": { /* data */ },
          "system_parameters": { /* data */ },
          "availability": { /* data */ }
        }
        /* ... more antenna sizes for this location */
      ]
    }
    /* ... more locations */
  ]
}
```

## Error Handling

### Error Response Format
```json
{
  "status": "error",
  "message": "Description of the error",
  "details": "Additional error details",
  "traceback": "Full error traceback (in debug mode)"
}
```

### Common Error Codes

| HTTP Code | Description | Common Causes |
|-----------|-------------|---------------|
| 400 | Bad Request | Missing required parameters, invalid parameter values |
| 500 | Internal Server Error | Calculation errors, server issues |

### Error Examples

**Missing Required Parameter**:
```json
{
  "status": "error",
  "message": "Missing required parameter: freq",
  "details": "The 'freq' parameter is required for satellite calculations"
}
```

**Invalid Parameter Value**:
```json
{
  "status": "error",
  "message": "Invalid value for parameter 'freq'",
  "details": "Frequency must be between 1 and 100 GHz, got: 150"
}
```

## Frontend Integration Guidelines

### 1. Input Validation

Implement client-side validation before sending requests:

```javascript
function validateSinglePointParams(params) {
  const errors = [];
  
  if (!params.sat_long || params.sat_long < -180 || params.sat_long > 180) {
    errors.push("Satellite longitude must be between -180 and 180 degrees");
  }
  
  if (!params.freq || params.freq < 1 || params.freq > 100) {
    errors.push("Frequency must be between 1 and 100 GHz");
  }
  
  if (!params.eirp || params.eirp < 0 || params.eirp > 100) {
    errors.push("EIRP must be between 0 and 100 dBW");
  }
  
  // Add more validations...
  
  return errors;
}
```

### 2. Loading States

Show loading indicators for calculations:

```javascript
async function calculateSinglePoint(params) {
  setLoading(true);
  try {
    const response = await fetch('/api/single-point', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params)
    });
    
    const data = await response.json();
    
    if (data.status === 'error') {
      throw new Error(data.message);
    }
    
    return data.results;
  } catch (error) {
    console.error('Calculation failed:', error);
    throw error;
  } finally {
    setLoading(false);
  }
}
```

### 3. Result Visualization

#### Link Budget Display
```javascript
function renderLinkBudget(linkBudget) {
  return (
    <div className="link-budget">
      <h3>Link Budget Analysis</h3>
      <div className="metrics">
        <div className="metric">
          <label>SNR (Clear Sky):</label>
          <span>{linkBudget.snr_clear_sky_db.toFixed(2)} dB</span>
        </div>
        <div className="metric">
          <label>SNR (With Attenuation):</label>
          <span>{linkBudget.snr_with_attenuation_db.toFixed(2)} dB</span>
        </div>
        <div className="metric">
          <label>Link Margin:</label>
          <span className={linkBudget.link_margin_db > 3 ? 'good' : 'warning'}>
            {linkBudget.link_margin_db.toFixed(2)} dB
          </span>
        </div>
      </div>
    </div>
  );
}
```

#### Availability Chart
```javascript
function renderAvailabilityChart(results) {
  const chartData = results.map(result => ({
    location: result.location.name,
    availability: result.availability.percentage
  }));
  
  // Use your preferred charting library (Chart.js, D3, etc.)
  return <BarChart data={chartData} />;
}
```

### 4. Form Templates

#### Basic Single Point Form
```javascript
const SinglePointForm = () => {
  const [params, setParams] = useState({
    sat_long: -70,
    freq: 12,
    eirp: 54,
    b_transponder: 36,
    b_util: 9,
    mod: "8PSK",
    fec: "120/180",
    site_lat: "",
    site_long: "",
    ant_size: 1.2
  });
  
  return (
    <form onSubmit={handleSubmit}>
      <div className="form-group">
        <label>Satellite Longitude (°):</label>
        <input 
          type="number" 
          step="0.1"
          min="-180" 
          max="180"
          value={params.sat_long}
          onChange={e => setParams({...params, sat_long: parseFloat(e.target.value)})}
        />
      </div>
      
      <div className="form-group">
        <label>Frequency (GHz):</label>
        <input 
          type="number" 
          step="0.1"
          min="1" 
          max="100"
          value={params.freq}
          onChange={e => setParams({...params, freq: parseFloat(e.target.value)})}
        />
      </div>
      
      {/* Add more form fields... */}
      
      <button type="submit">Calculate</button>
    </form>
  );
};
```

### 5. Performance Considerations

- **Debounce input changes** for real-time calculations
- **Cache results** for repeated calculations with same parameters
- **Implement pagination** for large multi-point results
- **Use progress indicators** for long-running calculations

### 6. Testing API Integration

```javascript
// Test API connectivity
async function testApiConnection() {
  try {
    const response = await fetch('http://localhost:5000/api/single-point', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        sat_long: -70, freq: 12, eirp: 54,
        b_transponder: 36, b_util: 9,
        mod: "8PSK", fec: "120/180",
        site_lat: -3.7, site_long: -45.9
      })
    });
    
    return response.ok;
  } catch (error) {
    console.error('API connection failed:', error);
    return false;
  }
}
```

## Sample Integration Code

See the complete React.js integration example in the `/frontend-examples` directory (coming soon).

## Support

For technical support or questions about the API:
- **Email**: christianfragoas@gmail.com
- **GitHub Issues**: Create an issue in the SatLink repository
- **Documentation**: Check the main [README.md](README.md) and [API_USAGE.md](API_USAGE.md)

## Changelog

- **v1.0**: Initial API release with four main endpoints
- **v1.1**: Added comprehensive error handling and validation
- **v1.2**: Enhanced response format with detailed system parameters

---

*This manual covers all essential aspects of integrating with the SatLink API. For specific implementation questions or feature requests, please contact the development team.*
