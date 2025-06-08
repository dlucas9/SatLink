#!/usr/bin/env python3
"""
SatLink REST API

Provides REST endpoints for satellite link calculation functions:
- /api/single-point: Single point link budget calculation
- /api/multi-point: Multi-point availability calculation
- /api/single-point-antenna-size: Single point antenna size calculation
- /api/multi-point-antenna-size: Multi-point antenna size calculation

Author: SatLink Team
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
from GrStat import GroundStation, Reception
from sat import Satellite
from scipy import interpolate
import multiprocessing
import tempfile
import os
import io
import traceback
from typing import Dict, List, Any
import math

app = Flask(__name__)
CORS(app)  # Enable CORS for all domains

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def safe_float(value, default=None):
    """Convert value to float, handling NaN and infinite values."""
    try:
        result = float(value)
        if math.isnan(result) or math.isinf(result):
            return default
        return result
    except (TypeError, ValueError):
        return default

def validate_satellite_params(data: Dict) -> Dict[str, Any]:
    """Validate and extract satellite parameters from request data."""
    required_fields = ['sat_long', 'freq', 'eirp', 'b_transponder', 'b_util', 'mod', 'fec']
    
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")
    
    # Set defaults for optional parameters
    satellite_params = {
        'sat_long': float(data['sat_long']),
        'freq': float(data['freq']),
        'eirp': float(data['eirp']),
        'hsat': float(data.get('hsat', 35800)),
        'b_transponder': float(data['b_transponder']),
        'b_util': float(data['b_util']),
        'backoff': float(data.get('backoff', 0)),
        'contour': float(data.get('contour', 0)),
        'mod': str(data['mod']),
        'rolloff': float(data.get('rolloff', 0.2)),
        'fec': str(data['fec'])
    }
    
    return satellite_params

def validate_reception_params(data: Dict) -> Dict[str, Any]:
    """Validate and extract reception parameters from request data."""
    reception_params = {
        'ant_size': float(data.get('ant_size', 1.2)),
        'ant_eff': float(data.get('ant_eff', 0.6)),
        'coupling_loss': float(data.get('coupling_loss', 0)),
        'polarization_loss': float(data.get('polarization_loss', 3)),
        'lnb_gain': float(data.get('lnb_gain', 55)),
        'lnb_noise_temp': float(data.get('lnb_noise_temp', 20)),
        'cable_loss': float(data.get('cable_loss', 4)),
        'max_depoint': float(data.get('max_depoint', 0.1))
    }
    
    return reception_params

def validate_ground_station_params(data: Dict) -> Dict[str, Any]:
    """Validate and extract ground station parameters from request data."""
    required_fields = ['site_lat', 'site_long']
    
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")
    
    station_params = {
        'site_lat': float(data['site_lat']),
        'site_long': float(data['site_long'])
    }
    
    return station_params

@app.route('/', methods=['GET'])
def index():
    """API documentation endpoint."""
    return jsonify({
        "name": "SatLink REST API",
        "version": "1.0.0",
        "description": "REST API for satellite link budget calculations",
        "endpoints": {
            "/api/single-point": {
                "method": "POST",
                "description": "Single point link budget calculation",
                "required_params": ["sat_long", "freq", "eirp", "b_transponder", "b_util", "mod", "fec", "site_lat", "site_long"]
            },
            "/api/multi-point": {
                "method": "POST", 
                "description": "Multi-point availability calculation",
                "required_params": ["sat_long", "freq", "eirp", "b_transponder", "b_util", "mod", "fec", "points"]
            },
            "/api/single-point-antenna-size": {
                "method": "POST",
                "description": "Single point antenna size calculation",
                "required_params": ["sat_long", "freq", "eirp", "b_transponder", "b_util", "mod", "fec", "site_lat", "site_long"]
            },
            "/api/multi-point-antenna-size": {
                "method": "POST",
                "description": "Multi-point antenna size calculation", 
                "required_params": ["sat_long", "freq", "eirp", "b_transponder", "b_util", "mod", "fec", "points"]
            }
        }
    })

@app.route('/api/single-point', methods=['POST'])
def single_point():
    """Single point link budget calculation endpoint."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Validate and extract parameters
        sat_params = validate_satellite_params(data)
        station_params = validate_ground_station_params(data)
        reception_params = validate_reception_params(data)
        
        # Optional probability parameter
        p = float(data.get('p', np.random.rand()))
        
        # Create objects
        station = GroundStation(station_params['site_lat'], station_params['site_long'])
        sat = Satellite(
            sat_params['sat_long'], sat_params['freq'], sat_params['eirp'],
            sat_params['hsat'], sat_params['b_transponder'], sat_params['b_util'],
            sat_params['backoff'], sat_params['contour'], sat_params['mod'],
            sat_params['rolloff'], sat_params['fec']
        )
        reception = Reception(
            reception_params['ant_size'], reception_params['ant_eff'],
            reception_params['coupling_loss'], reception_params['polarization_loss'],
            reception_params['lnb_gain'], reception_params['lnb_noise_temp'],
            reception_params['cable_loss'], reception_params['max_depoint']
        )
        
        # Set up satellite
        sat.set_grstation(station)
        sat.set_reception(reception)
        
        # Perform calculations
        a_fs, a_dep, a_g, a_c, a_r, a_s, a_t, a_tot = sat.get_link_attenuation(p)
        
        # Collect results
        results = {
            "input_parameters": {
                "satellite": sat_params,
                "ground_station": station_params,
                "reception": reception_params,
                "probability": p
            },
            "availability": {
                "percentage": safe_float(sat.get_availability())
            },
            "link_budget": {
                "gaseous_attenuation_db": safe_float(a_g.value) if hasattr(a_g, 'value') else safe_float(a_g),
                "cloud_attenuation_db": safe_float(a_c.value) if hasattr(a_c, 'value') else safe_float(a_c),
                "rain_attenuation_db": safe_float(a_r.value) if hasattr(a_r, 'value') else safe_float(a_r),
                "scintillation_attenuation_db": safe_float(a_s.value) if hasattr(a_s, 'value') else safe_float(a_s),
                "total_atmospheric_attenuation_db": safe_float(a_t.value) if hasattr(a_t, 'value') else safe_float(a_t),
                "free_space_attenuation_db": safe_float(a_fs),
                "depointing_loss_db": safe_float(a_dep),
                "total_attenuation_db": safe_float(a_tot),
                "c_over_n0_db_hz": safe_float(sat.get_c_over_n0(p)),
                "snr_clear_sky_db": safe_float(sat.get_snr(0.001)),  # SNR with minimal atmospheric attenuation
                "snr_with_attenuation_db": safe_float(sat.get_snr(p)),
                "snr_db": safe_float(sat.get_snr(p)),  # Keep for backward compatibility
                "link_margin_db": safe_float(sat.get_snr(p) - sat.get_reception_threshold()) if safe_float(sat.get_snr(p)) is not None and safe_float(sat.get_reception_threshold()) is not None else None
            },
            "atmospheric_attenuation": {
                "rain_attenuation_db": safe_float(a_r.value) if hasattr(a_r, 'value') else safe_float(a_r),
                "total_atmospheric_attenuation_db": safe_float(a_t.value) if hasattr(a_t, 'value') else safe_float(a_t)
            },
            "system_parameters": {
                "snr_threshold_db": safe_float(sat.get_reception_threshold()),
                "earth_radius_km": safe_float(sat.grstation.get_earth_radius()),
                "elevation_angle_deg": safe_float(sat.get_elevation()),
                "link_distance_km": safe_float(sat.get_distance()),
                "figure_of_merit": safe_float(sat.get_figure_of_merit()),
                "ground_brightness_temp_k": safe_float(sat.reception.get_ground_temp()),
                "sky_brightness_temp_k": safe_float(sat.reception.get_brightness_temp()),
                "antenna_noise_temp_k": safe_float(sat.reception.get_antenna_noise_temp()),
                "total_noise_temp_k": safe_float(sat.get_total_noise_temp()),
                "rx_antenna_gain_dbi": safe_float(sat.reception.get_antenna_gain()),
                "rx_antenna_beamwidth_deg": safe_float(sat.reception.get_beamwidth()),
                "link_availability_percent": safe_float(sat.get_availability())
            }
        }
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

@app.route('/api/multi-point', methods=['POST'])
def multi_point():
    """Multi-point availability calculation endpoint."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Validate satellite and reception parameters
        sat_params = validate_satellite_params(data)
        reception_params = validate_reception_params(data)
        
        # Validate points list
        if 'points' not in data:
            return jsonify({"error": "Missing required field: points"}), 400
        
        points = data['points']
        if not isinstance(points, list) or len(points) == 0:
            return jsonify({"error": "Points must be a non-empty list"}), 400
        
        # Validate each point
        for i, point in enumerate(points):
            if 'lat' not in point or 'long' not in point:
                return jsonify({"error": f"Point {i} missing 'lat' or 'long' field"}), 400
        
        # Create satellite and reception objects
        sat = Satellite(
            sat_params['sat_long'], sat_params['freq'], sat_params['eirp'],
            sat_params['hsat'], sat_params['b_transponder'], sat_params['b_util'],
            sat_params['backoff'], sat_params['contour'], sat_params['mod'],
            sat_params['rolloff'], sat_params['fec']
        )
        reception = Reception(
            reception_params['ant_size'], reception_params['ant_eff'],
            reception_params['coupling_loss'], reception_params['polarization_loss'],
            reception_params['lnb_gain'], reception_params['lnb_noise_temp'],
            reception_params['cable_loss'], reception_params['max_depoint']
        )
        
        # Calculate availability for each point
        results = []
        for i, point in enumerate(points):
            try:
                station = GroundStation(float(point['lat']), float(point['long']))
                sat.set_grstation(station)
                sat.set_reception(reception)
                
                # Perform full calculations like single-point
                p = 0.01  # Use default probability for multi-point
                a_fs, a_dep, a_g, a_c, a_r, a_s, a_t, a_tot = sat.get_link_attenuation(p)
                
                point_result = {
                    "location": {
                        "index": i,
                        "lat": float(point['lat']),
                        "long": float(point['long']),
                        "name": point.get('name', f"Point_{i}")
                    },
                    "availability": {
                        "percentage": safe_float(sat.get_availability())
                    },
                    "link_budget": {
                        "snr_clear_sky_db": safe_float(sat.get_snr(0.001)),
                        "snr_with_attenuation_db": safe_float(sat.get_snr(p)),
                        "link_margin_db": safe_float(sat.get_snr(p) - sat.get_reception_threshold()) if safe_float(sat.get_snr(p)) is not None and safe_float(sat.get_reception_threshold()) is not None else None
                    },
                    "atmospheric_attenuation": {
                        "rain_attenuation_db": safe_float(a_r.value) if hasattr(a_r, 'value') else safe_float(a_r),
                        "total_atmospheric_attenuation_db": safe_float(a_t.value) if hasattr(a_t, 'value') else safe_float(a_t)
                    },
                    "system_parameters": {
                        "elevation_angle_deg": safe_float(sat.get_elevation()),
                        "link_distance_km": safe_float(sat.get_distance())
                    }
                }
                results.append(point_result)
                
            except Exception as e:
                point_result = {
                    "location": {
                        "index": i,
                        "lat": float(point['lat']),
                        "long": float(point['long']),
                        "name": point.get('name', f"Point_{i}")
                    },
                    "error": str(e)
                }
                results.append(point_result)
        
        response = {
            "input_parameters": {
                "satellite": sat_params,
                "reception": reception_params,
                "points_count": len(points)
            },
            "results": results
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

@app.route('/api/single-point-antenna-size', methods=['POST'])
def single_point_antenna_size():
    """Single point antenna size calculation endpoint."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Validate parameters
        sat_params = validate_satellite_params(data)
        station_params = validate_ground_station_params(data)
        reception_params = validate_reception_params(data)
        
        # Antenna size range parameters
        min_ant_size = float(data.get('min_ant_size', 0.5))
        max_ant_size = float(data.get('max_ant_size', 3.0))
        step_size = float(data.get('step_size', 0.1))
        
        # Create ground station
        station = GroundStation(station_params['site_lat'], station_params['site_long'])
        
        # Generate antenna size range
        antenna_sizes = np.arange(min_ant_size, max_ant_size + step_size, step_size)
        results = []
        
        for ant_size in antenna_sizes:
            try:
                # Create satellite and reception objects
                sat = Satellite(
                    sat_params['sat_long'], sat_params['freq'], sat_params['eirp'],
                    sat_params['hsat'], sat_params['b_transponder'], sat_params['b_util'],
                    sat_params['backoff'], sat_params['contour'], sat_params['mod'],
                    sat_params['rolloff'], sat_params['fec']
                )
                
                reception = Reception(
                    ant_size, reception_params['ant_eff'],
                    reception_params['coupling_loss'], reception_params['polarization_loss'],
                    reception_params['lnb_gain'], reception_params['lnb_noise_temp'],
                    reception_params['cable_loss'], reception_params['max_depoint']
                )
                
                # Set up satellite
                sat.set_grstation(station)
                sat.set_reception(reception)
                
                # Calculate performance metrics
                p = 0.01  # Use 1% probability for calculations
                a_fs, a_dep, a_g, a_c, a_r, a_s, a_t, a_tot = sat.get_link_attenuation(p)
                availability = safe_float(sat.get_availability())
                snr_clear = safe_float(sat.get_snr(0.001))
                snr_attenuated = safe_float(sat.get_snr(p))
                antenna_gain = safe_float(sat.reception.get_antenna_gain())
                figure_of_merit = safe_float(sat.get_figure_of_merit())
                reception_threshold = safe_float(sat.get_reception_threshold())
                link_margin = safe_float(snr_attenuated - reception_threshold) if snr_attenuated is not None and reception_threshold is not None else None
                
                result = {
                    "antenna_size_m": float(ant_size),
                    "availability": {
                        "percentage": availability
                    },
                    "link_budget": {
                        "snr_clear_sky_db": snr_clear,
                        "snr_with_attenuation_db": snr_attenuated,
                        "link_margin_db": link_margin,
                        "antenna_gain_dbi": antenna_gain,
                        "figure_of_merit": figure_of_merit
                    },
                    "atmospheric_attenuation": {
                        "rain_attenuation_db": safe_float(a_r.value) if hasattr(a_r, 'value') else safe_float(a_r),
                        "total_atmospheric_attenuation_db": safe_float(a_t.value) if hasattr(a_t, 'value') else safe_float(a_t)
                    }
                }
                results.append(result)
                
            except Exception as e:
                result = {
                    "antenna_size_m": float(ant_size),
                    "error": str(e)
                }
                results.append(result)
        
        response = {
            "input_parameters": {
                "satellite": sat_params,
                "ground_station": station_params,
                "reception": reception_params,
                "antenna_size_range": {
                    "min_m": min_ant_size,
                    "max_m": max_ant_size,
                    "step_m": step_size
                }
            },
            "results": results
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

@app.route('/api/multi-point-antenna-size', methods=['POST'])
def multi_point_antenna_size():
    """Multi-point antenna size calculation endpoint."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Validate parameters
        sat_params = validate_satellite_params(data)
        reception_params = validate_reception_params(data)
        
        # Validate points list
        if 'points' not in data:
            return jsonify({"error": "Missing required field: points"}), 400
        
        points = data['points']
        if not isinstance(points, list) or len(points) == 0:
            return jsonify({"error": "Points must be a non-empty list"}), 400
        
        # Antenna size range parameters
        min_ant_size = float(data.get('min_ant_size', 0.5))
        max_ant_size = float(data.get('max_ant_size', 3.0))
        step_size = float(data.get('step_size', 0.1))
        
        # Generate antenna size range
        antenna_sizes = np.arange(min_ant_size, max_ant_size + step_size, step_size)
        
        # Results for each point and antenna size combination
        results = []
        
        for i, point in enumerate(points):
            if 'lat' not in point or 'long' not in point:
                continue
                
            try:
                station = GroundStation(float(point['lat']), float(point['long']))
                point_results = []
                
                for ant_size in antenna_sizes:
                    try:
                        # Create satellite and reception objects
                        sat = Satellite(
                            sat_params['sat_long'], sat_params['freq'], sat_params['eirp'],
                            sat_params['hsat'], sat_params['b_transponder'], sat_params['b_util'],
                            sat_params['backoff'], sat_params['contour'], sat_params['mod'],
                            sat_params['rolloff'], sat_params['fec']
                        )
                        
                        reception = Reception(
                            ant_size, reception_params['ant_eff'],
                            reception_params['coupling_loss'], reception_params['polarization_loss'],
                            reception_params['lnb_gain'], reception_params['lnb_noise_temp'],
                            reception_params['cable_loss'], reception_params['max_depoint']
                        )
                        
                        # Set up satellite
                        sat.set_grstation(station)
                        sat.set_reception(reception)
                        
                        # Calculate performance metrics
                        p = 0.01  # Use 1% probability for calculations
                        a_fs, a_dep, a_g, a_c, a_r, a_s, a_t, a_tot = sat.get_link_attenuation(p)
                        availability = safe_float(sat.get_availability())
                        snr_clear = safe_float(sat.get_snr(0.001))
                        snr_attenuated = safe_float(sat.get_snr(p))
                        reception_threshold = safe_float(sat.get_reception_threshold())
                        link_margin = safe_float(snr_attenuated - reception_threshold) if snr_attenuated is not None and reception_threshold is not None else None
                        
                        ant_result = {
                            "antenna_size_m": float(ant_size),
                            "availability": {
                                "percentage": availability
                            },
                            "link_budget": {
                                "snr_clear_sky_db": snr_clear,
                                "snr_with_attenuation_db": snr_attenuated,
                                "link_margin_db": link_margin
                            },
                            "atmospheric_attenuation": {
                                "rain_attenuation_db": safe_float(a_r.value) if hasattr(a_r, 'value') else safe_float(a_r),
                                "total_atmospheric_attenuation_db": safe_float(a_t.value) if hasattr(a_t, 'value') else safe_float(a_t)
                            }
                        }
                        point_results.append(ant_result)
                        
                    except Exception as e:
                        ant_result = {
                            "antenna_size_m": float(ant_size),
                            "error": str(e)
                        }
                        point_results.append(ant_result)
                
                point_summary = {
                    "index": i,
                    "lat": float(point['lat']),
                    "long": float(point['long']),
                    "name": point.get('name', f"Point_{i}"),
                    "antenna_size_results": point_results
                }
                results.append(point_summary)
                
            except Exception as e:
                point_summary = {
                    "index": i,
                    "lat": float(point['lat']),
                    "long": float(point['long']),
                    "name": point.get('name', f"Point_{i}"),
                    "error": str(e)
                }
                results.append(point_summary)
        
        response = {
            "input_parameters": {
                "satellite": sat_params,
                "reception": reception_params,
                "points_count": len(points),
                "antenna_size_range": {
                    "min_m": min_ant_size,
                    "max_m": max_ant_size,
                    "step_m": step_size
                }
            },
            "results": results
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({"error": "File too large"}), 413

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method not allowed"}), 405

if __name__ == '__main__':
    print("Starting SatLink REST API...")
    print("Available endpoints:")
    print("  GET  /                              - API documentation")
    print("  POST /api/single-point              - Single point calculation")
    print("  POST /api/multi-point               - Multi-point calculation")
    print("  POST /api/single-point-antenna-size - Single point antenna sizing")
    print("  POST /api/multi-point-antenna-size  - Multi-point antenna sizing")
    print("\nAPI will be available at: http://localhost:5000")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
