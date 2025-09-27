"""
LLM service
OpenAI API using natural language processing service
"""

import os
from typing import Dict, List, Optional, Any
from openai import OpenAI
from api.core.config import settings


class LLMService:
    """LLM service class"""
    
    def __init__(self):
        """LLM service initialization"""
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
    
    async def generate_report(self, 
                            patient_data: Dict[str, Any],
                            symptoms: List[str],
                            provider_notes: str) -> str:
        """
        Generate medical report.
        
        Args:
            patient_data: Patient information
            symptoms: Symptom list
            provider_notes: Provider notes
            
        Returns:
            Generated report text
        """
        prompt = self._build_report_prompt(patient_data, symptoms, provider_notes)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"LLM report generation error: {str(e)}")
    
    async def analyze_symptoms(self, symptoms: List[str]) -> Dict[str, Any]:
        """
        Analyze symptoms and suggest ICD code.
        
        Args:
            symptoms: Symptom list
            
        Returns:
            Analysis result (ICD code, risk level, etc.)
        """
        prompt = f"""
        Analyze the following symptoms and suggest appropriate ICD code:
        
        Symptoms: {', '.join(symptoms)}
        
        Respond in the following format:
        - Primary diagnosis: [Diagnosis name]
        - ICD code: [ICD-10 code]
        - Risk level: [Low/Medium/High]
        - Recommended tests: [Test list]
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a medical expert. Provide accurate and专业的medical analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1000
            )
            
            return self._parse_analysis_response(response.choices[0].message.content)
            
        except Exception as e:
            raise Exception(f"Symptom analysis error: {str(e)}")
    
    async def suggest_treatment(self, 
                              diagnosis: str,
                              patient_age: int,
                              medical_history: List[str]) -> Dict[str, Any]:
        """
        Suggest treatment options.
        
        Args:
            diagnosis: Diagnosis name
            patient_age: Patient age
            medical_history: Medical history
            
        Returns:
            Treatment suggestions (medications, tests, recommendations, etc.)
        """
        prompt = f"""
        Suggest treatment options based on the following information:
        
        Diagnosis: {diagnosis}
        Patient age: {patient_age} years
        Medical history: {', '.join(medical_history) if medical_history else 'None'}
        
        Respond in the following format:
        - Recommended medications: [Medication list]
        - Additional tests: [Test list]
        - Lifestyle guidance: [Guidance list]
        - Recommended specialist: [Specialist list]
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a experienced medical professional. Suggest treatment options for the patient's safety."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            return self._parse_treatment_response(response.choices[0].message.content)
            
        except Exception as e:
            raise Exception(f"Treatment suggestion error: {str(e)}")
    
    def _build_report_prompt(self, 
                           patient_data: Dict[str, Any],
                           symptoms: List[str],
                           provider_notes: str) -> str:
        """Build report prompt."""
        return f"""
        Write a professional medical report based on the following information:
        
        Patient information:
        - Name: {patient_data.get('name', 'N/A')}
        - Age: {patient_data.get('age', 'N/A')}
        - Gender: {patient_data.get('gender', 'N/A')}
        
        Symptoms:
        {', '.join(symptoms)}
        
        Provider notes:
        {provider_notes}
        
        Report structure:
        1. Patient information
        2. Symptoms
        3. History
        4. Diagnosis
        5. Treatment plan
        6. Follow-up management
        """
    
    def _get_system_prompt(self) -> str:
        """Get system prompt."""
        return """
        You are a experienced medical professional. 
        Write an accurate and professional medical report.
        Use appropriate medical terminology and consider the patient's safety.
        """
    
    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse analysis response."""
        # Simple parsing logic (actual parsing is more sophisticated)
        lines = response.split('\n')
        result = {}
        
        for line in lines:
            if 'Primary diagnosis:' in line:
                result['primary_diagnosis'] = line.split(':', 1)[1].strip()
            elif 'ICD code:' in line:
                result['icd_code'] = line.split(':', 1)[1].strip()
            elif 'Risk level:' in line:
                result['risk_level'] = line.split(':', 1)[1].strip()
            elif 'Recommended tests:' in line:
                result['recommended_tests'] = line.split(':', 1)[1].strip()
        
        return result
    
    def _parse_treatment_response(self, response: str) -> Dict[str, Any]:
        """Parse treatment response."""
        lines = response.split('\n')
        result = {}
        
        for line in lines:
            if 'Recommended medications:' in line:
                result['medications'] = line.split(':', 1)[1].strip()
            elif 'Additional tests:' in line:
                result['additional_tests'] = line.split(':', 1)[1].strip()
            elif 'Lifestyle guidance:' in line:
                result['lifestyle_guidance'] = line.split(':', 1)[1].strip()
            elif 'Recommended specialist:' in line:
                result['recommended_specialist'] = line.split(':', 1)[1].strip()
        
        return result


# Global LLM service instance
llm_service = LLMService()
