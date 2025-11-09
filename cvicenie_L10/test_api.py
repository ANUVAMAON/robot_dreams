#!/usr/bin/env python3
"""
Test script for Flask API with MongoDB integration
"""

import requests
import json
import time

# API configuration
API_BASE_URL = "http://localhost:8080"


def test_health_check():
    """Test the health check endpoint"""
    print("=== Testing Health Check ===")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_post_sensor_data():
    """Test posting sensor data"""
    print("\n=== Testing POST Sensor Data ===")

    test_data = {
        "id": "sensor_01",
        "temperature": 23.5,
        "humidity": 65.2,
        "unit": "celsius",
        "location": "room_1",
        "timestamp": time.time(),
    }

    try:
        response = requests.post(
            f"{API_BASE_URL}/sensor",
            json=test_data,
            headers={"Content-Type": "application/json"},
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_get_sensor_data():
    """Test getting specific sensor data"""
    print("\n=== Testing GET Sensor Data ===")

    try:
        response = requests.get(f"{API_BASE_URL}/sensor_sensor_01")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        else:
            print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_get_all_sensors():
    """Test getting all sensor data"""
    print("\n=== Testing GET All Sensors ===")

    try:
        response = requests.get(f"{API_BASE_URL}/sensors")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            sensors = response.json()
            print(f"Found {len(sensors)} sensors:")
            for sensor in sensors:
                print(f"  - {sensor.get('id', 'unknown')}: {sensor}")
        else:
            print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_update_sensor_data():
    """Test updating existing sensor data"""
    print("\n=== Testing UPDATE Sensor Data ===")

    updated_data = {
        "id": "sensor_01",
        "temperature": 24.1,
        "humidity": 68.5,
        "unit": "celsius",
        "location": "room_1",
        "timestamp": time.time(),
        "status": "updated",
    }

    try:
        response = requests.post(
            f"{API_BASE_URL}/sensor",
            json=updated_data,
            headers={"Content-Type": "application/json"},
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_delete_sensor():
    """Test deleting sensor data"""
    print("\n=== Testing DELETE Sensor Data ===")

    try:
        response = requests.delete(f"{API_BASE_URL}/sensor_sensor_01")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    """Run all tests"""
    print("Flask API MongoDB Integration Tests")
    print("=" * 50)

    tests = [
        ("Health Check", test_health_check),
        ("POST Sensor Data", test_post_sensor_data),
        ("GET Sensor Data", test_get_sensor_data),
        ("GET All Sensors", test_get_all_sensors),
        ("UPDATE Sensor Data", test_update_sensor_data),
        ("GET Updated Data", test_get_sensor_data),
        ("DELETE Sensor Data", test_delete_sensor),
    ]

    results = []
    for test_name, test_func in tests:
        success = test_func()
        results.append((test_name, success))
        time.sleep(1)  # Small delay between tests

    print("\n" + "=" * 50)
    print("TEST RESULTS:")
    for test_name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{test_name}: {status}")


if __name__ == "__main__":
    main()
