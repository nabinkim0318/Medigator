#!/usr/bin/env python3
"""
Create test patient data for development and testing
"""

import json
import sqlite3
import uuid
from datetime import datetime, timedelta
import random

# Test patient data
TEST_PATIENTS = [
    {
        "name": "John Smith",
        "age": 45,
        "gender": "Male",
        "bloodGroup": "A+",
        "phone": "555-1234-5678",
        "email": "john.smith@example.com",
        "appointment": {
            "q1": "Earlier today",
            "q2": "Middle of chest, spreads to left arm / jaw / neck / back",
            "q3": "Pressure or squeezing, Tightness / heaviness",
            "q4": "Physical activity, Stress or anxiety",
            "q5": "Rest, Stopping activity",
            "q6": "Shortness of breath, Sweating, Nausea or vomiting",
            "q7": "5–30 minutes",
            "q8": "A few times a week",
            "q9": "6–7 (severe)",
        },
    },
    {
        "name": "Sarah Johnson",
        "age": 32,
        "gender": "Female",
        "bloodGroup": "B+",
        "phone": "555-2345-6789",
        "email": "sarah.johnson@example.com",
        "appointment": {
            "q1": "Yesterday",
            "q2": "Upper abdomen, spreads to back and shoulders",
            "q3": "Burning, Sharp stabbing",
            "q4": "After eating, Lying down",
            "q5": "Sitting up, Antacids",
            "q6": "Nausea, Vomiting, Loss of appetite",
            "q7": "1-2 hours",
            "q8": "Daily for 3 days",
            "q9": "5-6 (moderate to severe)",
        },
    },
    {
        "name": "Michael Brown",
        "age": 28,
        "gender": "Male",
        "bloodGroup": "O+",
        "phone": "555-3456-7890",
        "email": "michael.brown@example.com",
        "appointment": {
            "q1": "2 days ago",
            "q2": "Front of head, spreads to neck and shoulders",
            "q3": "Throbbing, Pulsating",
            "q4": "Stress, Bright lights, Loud noises",
            "q5": "Dark room, Pain medication, Sleep",
            "q6": "Dizziness, Nausea, Light sensitivity",
            "q7": "4-6 hours",
            "q8": "Daily for 2 days",
            "q9": "7-8 (severe)",
        },
    },
    {
        "name": "Emily Davis",
        "age": 55,
        "gender": "Female",
        "bloodGroup": "AB+",
        "phone": "555-4567-8901",
        "email": "emily.davis@example.com",
        "appointment": {
            "q1": "3 days ago",
            "q2": "legs, spreads to lower back",
            "q3": "aching",
            "q4": "walking",
            "q5": "rest",
            "q6": "numbness",
            "q7": "7-8",
            "q8": "1 week",
            "q9": "5-6",
        },
    },
    {
        "name": "David Wilson",
        "age": 41,
        "gender": "Male",
        "bloodGroup": "A-",
        "phone": "555-5678-9012",
        "email": "david.wilson@example.com",
        "appointment": {
            "q1": "1 week ago",
            "q2": "shoulder, spreads to arm",
            "q3": "stiff",
            "q4": "exercise",
            "q5": "massage",
            "q6": "numbness",
            "q7": "5-6",
            "q8": "2 weeks",
            "q9": "3-4",
        },
    },
    {
        "name": "Lisa Anderson",
        "age": 37,
        "gender": "Female",
        "bloodGroup": "B-",
        "phone": "555-6789-0123",
        "email": "lisa.anderson@example.com",
        "appointment": {
            "q1": "4 days ago",
            "q2": "stomach, spreads to chest",
            "q3": "cramping",
            "q4": "eating",
            "q5": "sitting",
            "q6": "nausea",
            "q7": "6-7",
            "q8": "5 days",
            "q9": "4-5",
        },
    },
    {
        "name": "Robert Taylor",
        "age": 29,
        "gender": "Male",
        "bloodGroup": "O-",
        "phone": "555-7890-1234",
        "email": "robert.taylor@example.com",
        "appointment": {
            "q1": "5 days ago",
            "q2": "neck, spreads to shoulder",
            "q3": "stiff",
            "q4": "computer work",
            "q5": "stretching",
            "q6": "shoulder tension",
            "q7": "4-5",
            "q8": "1 week",
            "q9": "3-4",
        },
    },
    {
        "name": "Jennifer Martinez",
        "age": 43,
        "gender": "Female",
        "bloodGroup": "A+",
        "phone": "555-8901-2345",
        "email": "jennifer.martinez@example.com",
        "appointment": {
            "q1": "6 days ago",
            "q2": "lower back, spreads to legs",
            "q3": "aching",
            "q4": "lifting",
            "q5": "rest",
            "q6": "numbness",
            "q7": "7-8",
            "q8": "1 week",
            "q9": "5-6",
        },
    },
    {
        "name": "Christopher Lee",
        "age": 35,
        "gender": "Male",
        "bloodGroup": "B+",
        "phone": "555-9012-3456",
        "email": "christopher.lee@example.com",
        "appointment": {
            "q1": "2 days ago",
            "q2": "chest, spreads to back",
            "q3": "sharp",
            "q4": "breathing",
            "q5": "sitting",
            "q6": "shortness of breath",
            "q7": "8-9",
            "q8": "3 days",
            "q9": "4-5",
        },
    },
    {
        "name": "Amanda White",
        "age": 26,
        "gender": "Female",
        "bloodGroup": "AB-",
        "phone": "555-0123-4567",
        "email": "amanda.white@example.com",
        "appointment": {
            "q1": "1 day ago",
            "q2": "head, spreads to neck",
            "q3": "throbbing",
            "q4": "stress",
            "q5": "pain medication",
            "q6": "dizziness",
            "q7": "5-6",
            "q8": "1 day",
            "q9": "3-4",
        },
    },
]


def create_test_patients():
    """Create test patient data in the database"""
    # Connect to database
    conn = sqlite3.connect("copilot.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Ensure tables exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS intake_session (
            id TEXT PRIMARY KEY,
            token TEXT UNIQUE NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('PENDING','SUBMITTED','EXPIRED')),
            patient_hint TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            expires_at TEXT NOT NULL,
            submitted_at TEXT
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS intake_payload (
            session_id TEXT PRIMARY KEY REFERENCES intake_session(id) ON DELETE CASCADE,
            answers_json TEXT NOT NULL
        );
    """)

    print("Creating test patients...")

    for i, patient_data in enumerate(TEST_PATIENTS):
        # Generate unique token
        token = f"test-patient-{i+1:02d}"
        session_id = str(uuid.uuid4())

        # Create intake session
        created_at = datetime.now() - timedelta(days=random.randint(1, 30))
        expires_at = created_at + timedelta(days=1)

        cursor.execute(
            """
            INSERT INTO intake_session (id, token, status, created_at, expires_at, submitted_at)
            VALUES (?, ?, 'SUBMITTED', ?, ?, ?)
        """,
            (
                session_id,
                token,
                created_at.isoformat(),
                expires_at.isoformat(),
                created_at.isoformat(),
            ),
        )

        # Create patient profile data
        profile_data = {
            "name": patient_data["name"],
            "age": patient_data["age"],
            "gender": patient_data["gender"],
            "bloodGroup": patient_data["bloodGroup"],
            "phone": patient_data["phone"],
            "email": patient_data["email"],
        }

        # Create intake payload with both patient_data and answers_json
        cursor.execute(
            """
            INSERT INTO intake_payload (session_id, patient_data, answers_json)
            VALUES (?, ?, ?)
        """,
            (
                session_id,
                json.dumps(profile_data),
                json.dumps(patient_data["appointment"]),
            ),
        )

        print(f"Created patient {i+1}: {patient_data['name']} ({token})")

    conn.commit()
    conn.close()
    print(f"\n✅ Successfully created {len(TEST_PATIENTS)} test patients!")
    print("\nTest patient tokens:")
    for i in range(len(TEST_PATIENTS)):
        print(f"  - test-patient-{i+1:02d}")


if __name__ == "__main__":
    create_test_patients()
