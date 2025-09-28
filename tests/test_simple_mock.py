#!/usr/bin/env python3
"""
Simple LLM Mock Data Test
Quick test of LLM service with mock patient data
"""

import asyncio
import json
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from api.services.llm.service import llm_service


async def quick_test():
    """Quick test with mock data"""
    print("🏥 Quick LLM Mock Data Test")
    print("-" * 40)

    # Load mock data
    with open("data/intake/mock_patient.json") as f:
        mock_data = json.load(f)

    print("📋 Mock Patient Data:")
    for key, value in mock_data.items():
        print(f"  {key}: {value}")

    print("\n🤖 Generating medical summary...")

    try:
        # Generate summary
        result = await llm_service.summary(mock_data)

        print("\n✅ Summary Generated!")
        print(f"📝 HPI: {result.get('hpi', 'N/A')}")
        print(
            f"🚩 Ischemic Features: {result.get('flags', {}).get('ischemic_features', 'N/A')}"
        )

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(quick_test())
    print(f"\n{'✅ SUCCESS' if success else '❌ FAILED'}")
    sys.exit(0 if success else 1)
