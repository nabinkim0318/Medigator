#!/usr/bin/env python3
"""
Database seed script
Load CSV/JSON data into SQLite database.
"""

import csv
import json
import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

# Add project root directory to Python path
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, project_root)

from api.core.config import settings  # noqa: E402


def create_database():
    """Create database and tables."""
    db_path = settings.db_url.replace("sqlite:///", "")

    # Create database directory
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Read schema file and execute
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path, encoding="utf-8") as f:
        schema_sql = f.read()

    cursor.executescript(schema_sql)
    conn.commit()

    print(f"[SUCCESS] Database created: {db_path}")
    return conn


def load_csv_data(conn, table_name, csv_path, columns_mapping=None):
    """Load CSV file into database."""
    if not os.path.exists(csv_path):
        print(f"[WARNING] CSV file does not exist: {csv_path}")
        return

    cursor = conn.cursor()

    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        print(f"[WARNING] CSV file is empty: {csv_path}")
        return

    # Apply column mapping if exists
    if columns_mapping:
        for row in rows:
            for old_key, new_key in columns_mapping.items():
                if old_key in row:
                    row[new_key] = row.pop(old_key)

    # Insert data
    for row in rows:
        # Remove empty values
        row = {k: v for k, v in row.items() if v and v.strip()}

        if not row:
            continue

        columns = list(row.keys())
        values = list(row.values())
        placeholders = ", ".join(["?" for _ in columns])

        try:
            cursor.execute(
                f"INSERT OR REPLACE INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})",
                values,
            )
        except Exception as e:
            print(f"[ERROR] {table_name} insert error: {e}")
            print(f"   Data: {row}")

    conn.commit()
    print(f"[SUCCESS] {table_name} data loaded: {len(rows)} rows")


def load_json_data(conn, table_name, json_path):
    """Load JSON file into database."""
    if not os.path.exists(json_path):
        print(f"[WARNING] JSON file does not exist: {json_path}")
        return

    try:
        with open(json_path, encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                print(f"[WARNING] JSON file is empty: {json_path}")
                return
            data = json.loads(content)
    except json.JSONDecodeError as e:
        print(f"[WARNING] JSON parsing error: {json_path} - {e}")
        return

    cursor = conn.cursor()

    # JSON data processing (FHIR bundle, etc.)
    if isinstance(data, dict) and "entry" in data:
        # FHIR Bundle format
        entries = data.get("entry", [])
        for entry in entries:
            resource = entry.get("resource", {})
            if resource.get("resourceType") == "Patient":
                # Insert patient data
                patient_data = {
                    "patient_id": resource.get("id", ""),
                    "name": extract_patient_name(resource),
                    "birth_date": extract_birth_date(resource),
                    "gender": resource.get("gender", ""),
                }
                insert_patient_data(cursor, patient_data)

    conn.commit()
    print(f"[SUCCESS] {table_name} JSON data loaded")


def extract_patient_name(patient_resource):
    """Extract name from patient resource."""
    names = patient_resource.get("name", [])
    if names and len(names) > 0:
        name = names[0]
        given = " ".join(name.get("given", []))
        family = name.get("family", "")
        return f"{given} {family}".strip()
    return ""


def extract_birth_date(patient_resource):
    """Extract birth date from patient resource."""
    birth_date = patient_resource.get("birthDate", "")
    if birth_date:
        try:
            return datetime.strptime(birth_date, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return None
    return None


def insert_patient_data(cursor, patient_data):
    """Insert patient data."""
    try:
        cursor.execute(
            """
            INSERT OR REPLACE INTO patients (patient_id, name, birth_date, gender)
            VALUES (?, ?, ?, ?)
        """,
            (
                patient_data["patient_id"],
                patient_data["name"],
                patient_data["birth_date"],
                patient_data["gender"],
            ),
        )
    except Exception as e:
        print(f"[ERROR] Patient data insert error: {e}")


def create_sample_data(conn):
    """Create sample data."""
    cursor = conn.cursor()

    # Sample provider data
    providers_data = [
        ("PROV001", "Dr.Kim", "Internal Medicine", "MD123456"),
        ("PROV002", "Dr.Lee", "Surgery", "MD789012"),
        ("PROV003", "Dr.Park", "Pediatrics", "MD345678"),
    ]

    for provider_id, name, specialty, license_number in providers_data:
        cursor.execute(
            """
            INSERT OR REPLACE INTO providers (provider_id, name, specialty, license_number)
            VALUES (?, ?, ?, ?)
        """,
            (provider_id, name, specialty, license_number),
        )

    # Sample symptom-ICD mapping data
    symptom_icd_data = [
        ("Headache", "R51", "Headache"),
        ("Abdominal pain", "R10", "Abdominal pain"),
        ("Fever", "R50", "Fever"),
        ("Cough", "R05", "Cough"),
        ("Shortness of breath", "R06", "Shortness of breath"),
    ]

    for symptom, icd_code, description in symptom_icd_data:
        cursor.execute(
            """
            INSERT OR REPLACE INTO symptom_icd (symptom, icd_code, icd_description)
            VALUES (?, ?, ?)
        """,
            (symptom, icd_code, description),
        )

    # Sample CPT code data
    cpt_data = [
        ("General visit", "99213", "General visit"),
        ("Emergency room visit", "99281", "Emergency room visit"),
        ("Surgery", "47562", "Laparoscopic choledochoduodenostomy"),
        ("Test", "80053", "Basic metabolic panel"),
    ]

    for trigger, cpt_code, description in cpt_data:
        cursor.execute(
            """
            INSERT OR REPLACE INTO trigger_cpt (trigger_condition, cpt_code, cpt_description)
            VALUES (?, ?, ?)
        """,
            (trigger, cpt_code, description),
        )

    # Sample fee data
    fees_data = [
        ("99213", 150.00, "USD", "2024-01-01"),
        ("99281", 300.00, "USD", "2024-01-01"),
        ("47562", 2500.00, "USD", "2024-01-01"),
        ("80053", 45.00, "USD", "2024-01-01"),
    ]

    for cpt_code, amount, currency, effective_date in fees_data:
        cursor.execute(
            """
            INSERT OR REPLACE INTO fees (cpt_code, fee_amount, currency, effective_date)
            VALUES (?, ?, ?, ?)
        """,
            (cpt_code, amount, currency, effective_date),
        )

    # Sample EM rules data
    em_rules_data = [
        (
            "High risk patient identification",
            "Rule to identify high risk patients",
            "age > 65 AND chronic_conditions > 2",
            "flag_high_risk",
            1,
        ),
        (
            "Emergency room priority",
            "Rule to determine emergency room priority",
            "vital_signs_abnormal = true",
            "assign_priority_1",
            2,
        ),
        (
            "Provider notification",
            "Rule to notify provider",
            "critical_lab_result = true",
            "notify_provider",
            3,
        ),
    ]

    for rule_name, description, condition, action, priority in em_rules_data:
        cursor.execute(
            """
            INSERT OR REPLACE INTO em_rules (rule_name, rule_description, rule_condition, rule_action, priority)
            VALUES (?, ?, ?, ?, ?)
        """,
            (rule_name, description, condition, action, priority),
        )

    conn.commit()
    print("[SUCCESS] Sample data created")


def main():
    """Main seed function"""
    print("[INFO] Database seed started...")

    # Create database
    conn = create_database()

    try:
        # Data directory path
        data_dir = Path(settings.data_dir)
        rules_dir = data_dir / "rules"
        fhir_dir = data_dir / "fhir"

        # Load CSV data
        csv_files = [
            (rules_dir / "symptom_icd.csv", "symptom_icd"),
            (rules_dir / "trigger_cpt.csv", "trigger_cpt"),
            (rules_dir / "fees.csv", "fees"),
            (rules_dir / "em_rules.csv", "em_rules"),
        ]

        for csv_path, table_name in csv_files:
            load_csv_data(conn, table_name, str(csv_path))

        # JSON data load
        json_files = [(fhir_dir / "cp_bundle.json", "patients")]

        for json_path, table_name in json_files:
            load_json_data(conn, table_name, str(json_path))

        # Create sample data (if CSV files are empty)
        create_sample_data(conn)

        print("[SUCCESS] Database seed completed!")

    except Exception as e:
        print(f"[ERROR] Seed error: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
