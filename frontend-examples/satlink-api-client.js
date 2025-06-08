// SatLink API Integration Example - Vanilla JavaScript
// This file demonstrates basic integration with the SatLink REST API

class SatLinkAPI {
  constructor(baseURL = 'http://localhost:5000') {
    this.baseURL = baseURL;
  }

  async request(endpoint, data) {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
      });

      const result = await response.json();
      
      if (result.status === 'error') {
        throw new Error(result.message);
      }
      
      return result;
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error);
      throw error;
    }
  }

  // Single point calculation
  async calculateSinglePoint(params) {
    return this.request('/api/single-point', params);
  }

  // Multi-point calculation
  async calculateMultiPoint(params) {
    return this.request('/api/multi-point', params);
  }

  // Single point antenna sizing
  async calculateSinglePointAntennaSize(params) {
    return this.request('/api/single-point-antenna-size', params);
  }

  // Multi-point antenna sizing
  async calculateMultiPointAntennaSize(params) {
    return this.request('/api/multi-point-antenna-size', params);
  }
}

// Usage Examples
// Note: Create your own SatLinkAPI instance in your application

// Example 1: Single point calculation
async function exampleSinglePoint() {
  const api = new SatLinkAPI();
  const params = {
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

  try {
    const result = await api.calculateSinglePoint(params);
    console.log('Single Point Results:', result.results);
    
    // Access specific values
    const availability = result.results.availability.percentage;
    const snr = result.results.link_budget.snr_with_attenuation_db;
    const margin = result.results.link_budget.link_margin_db;
    
    console.log(`Availability: ${availability}%`);
    console.log(`SNR: ${snr} dB`);
    console.log(`Link Margin: ${margin} dB`);
    
  } catch (error) {
    console.error('Calculation failed:', error.message);
  }
}

// Example 2: Multi-point calculation
async function exampleMultiPoint() {
  const api = new SatLinkAPI();
  const params = {
    sat_long: -70,
    freq: 12,
    eirp: 54,
    b_transponder: 36,
    b_util: 9,
    mod: "8PSK",
    fec: "120/180",
    locations: [
      { name: "São Paulo", lat: -23.55, long: -46.64 },
      { name: "Rio de Janeiro", lat: -22.91, long: -43.17 },
      { name: "Brasília", lat: -15.78, long: -47.93 }
    ]
  };

  try {
    const result = await api.calculateMultiPoint(params);
    
    result.results.forEach(location => {
      console.log(`${location.location.name}: ${location.availability.percentage}% availability`);
    });
    
  } catch (error) {
    console.error('Multi-point calculation failed:', error.message);
  }
}

// Example 3: Antenna sizing analysis
async function exampleAntennaSizing() {
  const api = new SatLinkAPI();
  const params = {
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
    ant_size_step: 0.3
  };

  try {
    const result = await api.calculateSinglePointAntennaSize(params);
    
    console.log('Antenna Sizing Analysis:');
    result.results.forEach(item => {
      console.log(`${item.antenna_size_m}m: ${item.availability.percentage}% availability, ${item.link_budget.link_margin_db} dB margin`);
    });
    
  } catch (error) {
    console.error('Antenna sizing calculation failed:', error.message);
  }
}

// Form validation helper
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
  
  if (!params.b_transponder || params.b_transponder < 0.1 || params.b_transponder > 1000) {
    errors.push("Transponder bandwidth must be between 0.1 and 1000 MHz");
  }
  
  if (!params.b_util || params.b_util < 0.1 || params.b_util > 1000) {
    errors.push("Utilized bandwidth must be between 0.1 and 1000 MHz");
  }
  
  if (!params.mod || !["QPSK", "8PSK", "16APSK", "32APSK"].includes(params.mod)) {
    errors.push("Modulation must be one of: QPSK, 8PSK, 16APSK, 32APSK");
  }
  
  if (!params.site_lat || params.site_lat < -90 || params.site_lat > 90) {
    errors.push("Site latitude must be between -90 and 90 degrees");
  }
  
  if (!params.site_long || params.site_long < -180 || params.site_long > 180) {
    errors.push("Site longitude must be between -180 and 180 degrees");
  }
  
  return errors;
}

// Result formatter helper
function formatResults(results) {
  const safeFormat = (value, decimals = 2, unit = '') => {
    if (value === null || value === undefined || isNaN(value)) {
      return 'N/A';
    }
    return `${value.toFixed(decimals)}${unit}`;
  };

  return {
    availability: safeFormat(results.availability?.percentage, 2, '%'),
    snr_clear: safeFormat(results.link_budget?.snr_clear_sky_db, 2, ' dB'),
    snr_attenuated: safeFormat(results.link_budget?.snr_with_attenuation_db, 2, ' dB'),
    link_margin: safeFormat(results.link_budget?.link_margin_db, 2, ' dB'),
    elevation: safeFormat(results.system_parameters?.elevation_angle_deg, 1, '°'),
    rain_attenuation: safeFormat(results.atmospheric_attenuation?.rain_attenuation_db, 2, ' dB'),
    total_attenuation: safeFormat(results.atmospheric_attenuation?.total_atmospheric_attenuation_db, 2, ' dB')
  };
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { SatLinkAPI, validateSinglePointParams, formatResults };
}
