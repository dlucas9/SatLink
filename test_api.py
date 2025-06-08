#!/usr/bin/env python3
"""
Test script for SatLink REST API endpoints
"""

import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:5000"

def test_documentation():
    """Test the documentation endpoint"""
    print("Testing documentation endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_single_point():
    """Test single point calculation"""
    print("\nTesting single point calculation...")
    
    # Sample data based on single_point_example.py
    data = {
        "sat_long": -70,
        "freq": 15,
        "eirp": 54,
        "b_transponder": 36,
        "b_util": 9,
        "mod": "8PSK",
        "fec": "120/180",
        "site_lat": -3.7,
        "site_long": -45.9,
        "ant_size": 1.2,
        "ant_eff": 0.6,
        "lnb_gain": 55,
        "lnb_noise_temp": 20,
        "cable_loss": 4,
        "max_depoint": 0.1
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/single-point", json=data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Availability: {result['system_parameters']['link_availability_percent']:.3f}%")
            print(f"SNR: {result['link_budget']['snr_db']:.2f} dB")
            print(f"Total Attenuation: {result['link_budget']['total_attenuation_db']:.2f} dB")
        else:
            print(f"Error Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_multi_point():
    """Test multi-point calculation"""
    print("\nTesting multi-point calculation...")
    
    data = {
        "sat_long": -70,
        "freq": 12,
        "eirp": 50,
        "b_transponder": 36,
        "b_util": 9,
        "mod": "8PSK",
        "fec": "120/180",
        "points": [
            {"lat": -3.7, "long": -45.9, "name": "Sao Luis"},
            {"lat": -15.8, "long": -47.9, "name": "Brasilia"},
            {"lat": -23.5, "long": -46.6, "name": "Sao Paulo"}
        ]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/multi-point", json=data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Points processed: {len(result['results'])}")
            for point in result['results']:
                print(f"  {point['name']}: {point['availability_percent']:.3f}%")
        else:
            print(f"Error Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_single_point_antenna_size():
    """Test single point antenna sizing"""
    print("\nTesting single point antenna sizing...")
    
    data = {
        "sat_long": -70,
        "freq": 12,
        "eirp": 54,
        "b_transponder": 36,
        "b_util": 9,
        "mod": "8PSK",
        "fec": "120/180",
        "site_lat": -3.7,
        "site_long": -45.9,
        "min_ant_size": 0.6,
        "max_ant_size": 2.0,
        "step_size": 0.2
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/single-point-antenna-size", json=data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Antenna sizes tested: {len(result['results'])}")
            for i, ant_result in enumerate(result['results'][:3]):  # Show first 3
                print(f"  {ant_result['antenna_size_m']}m: {ant_result['availability_percent']:.3f}%")
        else:
            print(f"Error Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("SatLink API Test Suite")
    print("=" * 50)
    
    # Test all endpoints
    tests = [
        test_documentation,
        test_single_point,
        test_multi_point,
        test_single_point_antenna_size
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        print("-" * 30)
    
    print(f"\nTests passed: {passed}/{len(tests)}")
