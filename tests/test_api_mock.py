#!/usr/bin/env python3
"""
API Mock Data Test
Tests LLM endpoints with mock patient data via HTTP API
"""

import asyncio
import json
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

import httpx
from fastapi.testclient import TestClient

from api.main import app


def test_summary_endpoint():
    """Test summary endpoint with mock data"""
    print("Testing Summary API Endpoint")
    print("-" * 40)

    # Load mock data
    with open("data/intake/mock_patient.json") as f:
        mock_data = json.load(f)

    # Create test client
    with TestClient(app) as client:
        # Prepare request data
        request_data = {
            "encounterId": "test_001",
            "patient": {"age": 45, "sex": "M"},
            "answers": mock_data,
        }

        print("📤 Sending request to /api/v1/summary...")

        # Make API call
        response = client.post("/api/v1/summary", json=request_data)

        print(f"📊 Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ API Response:")
            print(f"  HPI: {result.get('hpi', 'N/A')[:100]}...")
            print(f"  Ischemic Features: {result.get('flags', {}).get('ischemic_features', 'N/A')}")
            return True
        print(f"❌ API Error: {response.text}")
        return False


def test_evidence_endpoint():
    """Test evidence endpoint with mock data"""
    print("\nTesting Evidence API Endpoint")
    print("-" * 40)

    # Create summary data based on mock patient
    summary_data = {
        "hpi": "Patient reports chest pain that started earlier today, described as pressure or squeezing.",
        "ros": {
            "cardiovascular": {"positive": ["chest pain"], "negative": []},
            "respiratory": {"positive": ["shortness of breath"], "negative": []},
            "constitutional": {"positive": [], "negative": []},
        },
        "pmh": [],
        "meds": [],
        "flags": {"ischemic_features": True, "dm_followup": False, "labs_a1c_needed": False},
    }

    with TestClient(app) as client:
        print("📤 Sending request to /api/v1/evidence...")

        response = client.post("/api/v1/evidence", json=summary_data)

        print(f"📊 Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ API Response:")
            print(f"  Evidence Items: {len(result.get('items', []))}")
            for i, item in enumerate(result.get("items", [])[:2], 1):
                print(f"    {i}. {item.get('title', 'N/A')}")
            return True
        print(f"❌ API Error: {response.text}")
        return False


def main():
    """Run API tests"""
    print("BBB Medical API Mock Data Test")
    print("=" * 50)

    tests = [
        ("Summary Endpoint", test_summary_endpoint),
        ("Evidence Endpoint", test_evidence_endpoint),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Results Summary:")

    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if success:
            passed += 1

    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")

    if passed == len(results):
        print("🎉 All API tests passed!")
        return 0
    print("⚠️  Some tests failed")
    return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
