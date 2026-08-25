#!/usr/bin/env python3
"""
Test LLM JSON Output Structure
Verifies that LLM generates structured JSON as expected
"""

import asyncio
import json
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from api.services.llm.service import llm_service


async def test_json_structure():
    """Test LLM JSON output structure"""
    print("🧪 Testing LLM JSON Output Structure")
    print("=" * 50)

    # Load mock data
    with open("data/intake/mock_patient.json") as f:
        mock_data = json.load(f)

    print("📋 Input Mock Data:")
    print(json.dumps(mock_data, indent=2, ensure_ascii=False))

    print("\n🤖 Calling LLM service...")

    try:
        # Generate summary
        result = await llm_service.summary(mock_data)

        print("\n✅ LLM Generated Structured JSON:")
        print("=" * 50)
        print(json.dumps(result, indent=2, ensure_ascii=False))

        # Verify structure
        print("\n🔍 Structure Verification:")
        print("-" * 30)

        required_fields = ["hpi", "ros", "pmh", "meds", "flags"]
        for field in required_fields:
            if field in result:
                print(f"✅ {field}: Present")
                if field == "ros":
                    ros_systems = ["cardiovascular", "respiratory", "constitutional"]
                    for system in ros_systems:
                        if system in result["ros"]:
                            print(f"   ✅ {system}: Present")
                        else:
                            print(f"   ❌ {system}: Missing")
                elif field == "flags":
                    flag_types = ["ischemic_features", "dm_followup", "labs_a1c_needed"]
                    for flag in flag_types:
                        if flag in result["flags"]:
                            print(f"   ✅ {flag}: {result['flags'][flag]}")
                        else:
                            print(f"   ❌ {flag}: Missing")
            else:
                print(f"❌ {field}: Missing")

        # Type verification
        print("\n🔬 Type Verification:")
        print("-" * 20)

        if isinstance(result.get("hpi"), str):
            print("✅ hpi: string")
        else:
            print(f"❌ hpi: {type(result.get('hpi'))}")

        if isinstance(result.get("pmh"), list):
            print("✅ pmh: array")
        else:
            print(f"❌ pmh: {type(result.get('pmh'))}")

        if isinstance(result.get("meds"), list):
            print("✅ meds: array")
        else:
            print(f"❌ meds: {type(result.get('meds'))}")

        if isinstance(result.get("flags"), dict):
            print("✅ flags: object")
            for flag, value in result["flags"].items():
                if isinstance(value, bool):
                    print(f"   ✅ {flag}: boolean ({value})")
                else:
                    print(f"   ❌ {flag}: {type(value)} ({value})")
        else:
            print(f"❌ flags: {type(result.get('flags'))}")

        print("\n🎉 JSON Structure Test Completed!")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_different_inputs():
    """Test with different input structures"""
    print("\n🔄 Testing Different Input Structures")
    print("=" * 50)

    test_cases = [
        {
            "name": "Minimal Input",
            "data": {
                "Q1_When_did_the_pain_start": "Yesterday",
                "Q2_Where_is_the_pain": ["Middle of chest"],
                "Q3_Pain_character": ["Pressure or squeezing"],
            },
        },
        {
            "name": "Complete Input",
            "data": {
                "Q1_When_did_the_pain_start": "Earlier today",
                "Q2_Where_is_the_pain": [
                    "Middle of chest",
                    "Spreads to left arm / jaw / neck / back",
                ],
                "Q3_Pain_character": ["Pressure or squeezing", "Tightness / heaviness"],
                "Q4_Worse_with": ["Physical activity", "Stress or anxiety"],
                "Q5_Better_with": ["Rest", "Stopping activity"],
                "Q6_Associated_symptoms": [
                    "Shortness of breath",
                    "Sweating",
                    "Nausea or vomiting",
                ],
                "Q7_Duration": "5-30 minutes",
                "Q8_Frequency": "A few times a week",
                "Q9_Severity_0_10": "6-7 (severe)",
            },
        },
    ]

    for test_case in test_cases:
        print(f"\n📝 Testing: {test_case['name']}")
        print("-" * 30)

        try:
            result = await llm_service.summary(test_case["data"])

            # Check if all required fields are present
            required_fields = ["hpi", "ros", "pmh", "meds", "flags"]
            missing_fields = [field for field in required_fields if field not in result]

            if not missing_fields:
                print("✅ All required fields present")
                print(f"   HPI length: {len(result.get('hpi', ''))}")
                print(f"   Flags: {result.get('flags', {})}")
            else:
                print(f"❌ Missing fields: {missing_fields}")

        except Exception as e:
            print(f"❌ Error in {test_case['name']}: {e}")


async def main():
    """Main test function"""
    print("🏥 Medigator LLM JSON Structure Test")
    print("=" * 60)

    try:
        # Test 1: JSON structure
        success = await test_json_structure()

        if success:
            # Test 2: Different inputs
            await test_different_inputs()
            print("\n🎉 All JSON structure tests completed!")
        else:
            print("\n❌ JSON structure test failed!")
            return 1

    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
