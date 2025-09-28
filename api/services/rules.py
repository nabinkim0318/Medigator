"""
Rule engine service
Manage medical rules and policies.
"""

import sqlite3
from typing import Any

from api.core.config import settings


class RulesService:
    """Rule engine service class"""

    def __init__(self):
        """Rule service initialization"""
        self.db_path = settings.db_url.replace("sqlite:///", "")

    def get_connection(self):
        """Return database connection"""
        return sqlite3.connect(self.db_path)

    async def get_symptom_icd_mapping(self, symptom: str) -> list[dict[str, Any]]:
        """
        Get ICD code mapping for symptom.

        Args:
            symptom: Symptom name

        Returns:
            ICD code mapping list
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT symptom, icd_code, icd_description
                FROM symptom_icd
                WHERE symptom LIKE ? OR icd_description LIKE ?
                ORDER BY symptom
            """,
                (f"%{symptom}%", f"%{symptom}%"),
            )

            results = []
            for row in cursor.fetchall():
                results.append(
                    {"symptom": row[0], "icd_code": row[1], "icd_description": row[2]}
                )

            return results

        finally:
            conn.close()

    async def get_cpt_codes_for_condition(self, condition: str) -> list[dict[str, Any]]:
        """
        Get CPT codes for condition.

        Args:
            condition: Condition name

        Returns:
            CPT code list
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT trigger_condition, cpt_code, cpt_description
                FROM trigger_cpt
                WHERE trigger_condition LIKE ? OR cpt_description LIKE ?
                ORDER BY trigger_condition
            """,
                (f"%{condition}%", f"%{condition}%"),
            )

            results = []
            for row in cursor.fetchall():
                results.append(
                    {
                        "trigger_condition": row[0],
                        "cpt_code": row[1],
                        "cpt_description": row[2],
                    },
                )

            return results

        finally:
            conn.close()

    async def get_fee_for_cpt(self, cpt_code: str) -> dict[str, Any] | None:
        """
        Get fee information for CPT code.

        Args:
            cpt_code: CPT code

        Returns:
            Fee information
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT cpt_code, fee_amount, currency, effective_date
                FROM fees
                WHERE cpt_code = ?
                ORDER BY effective_date DESC
                LIMIT 1
            """,
                (cpt_code,),
            )

            row = cursor.fetchone()
            if row:
                return {
                    "cpt_code": row[0],
                    "fee_amount": row[1],
                    "currency": row[2],
                    "effective_date": row[3],
                }

            return None

        finally:
            conn.close()

    async def get_active_rules(self) -> list[dict[str, Any]]:
        """
        Get active EM rules.

        Returns:
            Active rules list
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT id, rule_name, rule_description, rule_condition,
                       rule_action, priority, is_active
                FROM em_rules
                WHERE is_active = 1
                ORDER BY priority ASC
            """,
            )

            results = []
            for row in cursor.fetchall():
                results.append(
                    {
                        "id": row[0],
                        "rule_name": row[1],
                        "rule_description": row[2],
                        "rule_condition": row[3],
                        "rule_action": row[4],
                        "priority": row[5],
                        "is_active": bool(row[6]),
                    },
                )

            return results

        finally:
            conn.close()

    async def evaluate_rules(
        self,
        patient_data: dict[str, Any],
        symptoms: list[str],
        vital_signs: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """
        Evaluate rules for patient data.

        Args:
            patient_data: Patient data
            symptoms: Symptoms list
            vital_signs: Vital signs

        Returns:
            Applied rules list
        """
        rules = await self.get_active_rules()
        applied_rules = []

        for rule in rules:
            if await self._evaluate_rule_condition(
                rule, patient_data, symptoms, vital_signs
            ):
                applied_rules.append(
                    {
                        "rule_id": rule["id"],
                        "rule_name": rule["rule_name"],
                        "action": rule["rule_action"],
                        "priority": rule["priority"],
                    },
                )

        return applied_rules

    async def _evaluate_rule_condition(
        self,
        rule: dict[str, Any],
        patient_data: dict[str, Any],
        symptoms: list[str],
        vital_signs: dict[str, Any],
    ) -> bool:
        """
        Evaluate rule condition.

        Args:
            rule: rule data
            patient_data: Patient data
            symptoms: Symptoms list
            vital_signs: Vital signs

        Returns:
            Rule application status
        """
        condition = rule["rule_condition"]

        # Simple condition evaluation (actual parsing is needed)
        try:
            # Age condition
            if "age >" in condition:
                age_threshold = int(condition.split("age >")[1].split()[0])
                patient_age = patient_data.get("age", 0)
                if patient_age <= age_threshold:
                    return False

            # Symptom condition
            if "symptoms" in condition:
                for symptom in symptoms:
                    if symptom.lower() in condition.lower():
                        return True

            # Vital signs condition
            if "vital_signs_abnormal" in condition:
                # Simple vital signs evaluation
                if self._check_abnormal_vitals(vital_signs):
                    return True

            # By default, rule is applied
            return True

        except Exception:
            return False

    def _check_abnormal_vitals(self, vital_signs: dict[str, Any]) -> bool:
        """
        Check if vital signs are abnormal.

        Args:
            vital_signs: Vital signs

        Returns:
            Abnormal status
        """
        # Simple vital signs evaluation logic
        if "temperature" in vital_signs:
            temp = vital_signs["temperature"]
            if temp > 38.0 or temp < 36.0:  # Fever or low temperature
                return True

        if "blood_pressure_systolic" in vital_signs:
            bp_sys = vital_signs["blood_pressure_systolic"]
            if bp_sys > 140 or bp_sys < 90:  # High blood pressure or low blood pressure
                return True

        if "heart_rate" in vital_signs:
            hr = vital_signs["heart_rate"]
            if hr > 100 or hr < 60:  # Bradycardia or Tachycardia
                return True

        return False

    async def add_rule(
        self,
        rule_name: str,
        rule_description: str,
        rule_condition: str,
        rule_action: str,
        priority: int = 0,
    ) -> int:
        """
        Add new rule.

        Args:
            rule_name: Rule name
            rule_description: Rule description
            rule_condition: Rule condition
            rule_action: Rule action
            priority: Priority

        Returns:
            Added rule ID
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO em_rules (rule_name, rule_description, rule_condition,
                                     rule_action, priority, is_active)
                VALUES (?, ?, ?, ?, ?, 1)
            """,
                (rule_name, rule_description, rule_condition, rule_action, priority),
            )

            rule_id = cursor.lastrowid
            conn.commit()

            return rule_id

        finally:
            conn.close()

    async def update_rule_status(self, rule_id: int, is_active: bool) -> bool:
        """
        Update rule activation status.

        Args:
            rule_id: Rule ID
            is_active: Activation status

        Returns:
            Update success status
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                UPDATE em_rules
                SET is_active = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """,
                (1 if is_active else 0, rule_id),
            )

            conn.commit()
            return cursor.rowcount > 0

        finally:
            conn.close()


# Global rule service instance
rules_service = RulesService()
