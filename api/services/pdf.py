"""
PDF service
Medical report PDF generation service
"""

import os
from typing import Dict, Any, Optional
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from api.core.config import settings


class PDFService:
    """PDF generation service class"""
    
    def __init__(self):
        """PDF service initialization"""
        self.output_dir = settings.pdf_output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Style settings
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomHeading2',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.darkblue
        ))
        
        # Body style
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            alignment=TA_LEFT
        ))
        
        # Header style
        self.styles.add(ParagraphStyle(
            name='Header',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_RIGHT,
            textColor=colors.grey
        ))
    
    async def generate_report_pdf(self, 
                                report_data: Dict[str, Any],
                                patient_data: Dict[str, Any],
                                provider_data: Dict[str, Any]) -> str:
        """
        Generate medical report PDF.
        
        Args:
            report_data: Report data
            patient_data: Patient data
            provider_data: Provider data
            
        Returns:
            Generated PDF file path
        """
        # File name creation
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"medical_report_{timestamp}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        # PDF document creation
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        story = []
        
        # Add header
        story.append(self._create_header(provider_data))
        story.append(Spacer(1, 20))
        
        # Add title
        story.append(Paragraph("Medical report", self.styles['CustomTitle']))
        story.append(Spacer(1, 20))
        
        # Patient info section
        story.append(Paragraph("Patient info", self.styles['CustomHeading2']))
        story.append(self._create_patient_info_table(patient_data))
        story.append(Spacer(1, 20))
        
        # Report content section
        story.append(Paragraph("Report content", self.styles['CustomHeading2']))
        story.append(self._create_report_content(report_data))
        story.append(Spacer(1, 20))
        
        # Diagnosis and treatment section
        if 'diagnosis' in report_data:
            story.append(Paragraph("Diagnosis", self.styles['CustomHeading2']))
            story.append(Paragraph(report_data['diagnosis'], self.styles['CustomBody']))
            story.append(Spacer(1, 12))
        
        if 'treatment' in report_data:
            story.append(Paragraph("Treatment plan", self.styles['CustomHeading2']))
            story.append(Paragraph(report_data['treatment'], self.styles['CustomBody']))
            story.append(Spacer(1, 12))
        
        # Add footer
        story.append(Spacer(1, 30))
        story.append(self._create_footer())
        
        # PDF generation
        doc.build(story)
        
        return filepath
    
    def _create_header(self, provider_data: Dict[str, Any]) -> Paragraph:
        """Create header."""
        header_text = f"""
        {provider_data.get('name', 'N/A')} Doctor<br/>
        {provider_data.get('specialty', 'N/A')}<br/>
        License number: {provider_data.get('license_number', 'N/A')}
        """
        return Paragraph(header_text, self.styles['Header'])
    
    def _create_patient_info_table(self, patient_data: Dict[str, Any]) -> Table:
        """Create patient info table."""
        data = [
            ['Patient name', patient_data.get('name', 'N/A')],
            ['Birth date', str(patient_data.get('birth_date', 'N/A'))],
            ['Gender', patient_data.get('gender', 'N/A')],
            ['Patient ID', patient_data.get('patient_id', 'N/A')]
        ]
        
        table = Table(data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (0, 0), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        return table
    
    def _create_report_content(self, report_data: Dict[str, Any]) -> list:
        """Create report content."""
        content = []
        
        # Chief complaint
        if 'chief_complaint' in report_data:
            content.append(Paragraph("Chief complaint", self.styles['CustomHeading2']))
            content.append(Paragraph(report_data['chief_complaint'], self.styles['CustomBody']))
            content.append(Spacer(1, 12))
        
        # History
        if 'history' in report_data:
            content.append(Paragraph("History", self.styles['CustomHeading2']))
            content.append(Paragraph(report_data['history'], self.styles['CustomBody']))
            content.append(Spacer(1, 12))
        
        # Physical exam
        if 'physical_exam' in report_data:
            content.append(Paragraph("Physical exam", self.styles['CustomHeading2']))
            content.append(Paragraph(report_data['physical_exam'], self.styles['CustomBody']))
            content.append(Spacer(1, 12))
        
        # Test results
        if 'test_results' in report_data:
            content.append(Paragraph("Test results", self.styles['CustomHeading2']))
            content.append(Paragraph(report_data['test_results'], self.styles['CustomBody']))
            content.append(Spacer(1, 12))
        
        return content
    
    def _create_footer(self) -> Paragraph:
        """Create footer."""
        footer_text = f"""
        Report creation date: {datetime.now().strftime('%Y %m %d %H:%M')}<br/>
        This report is written by the doctor, please refer to the patient's treatment.
        """
        return Paragraph(footer_text, self.styles['Header'])
    
    async def generate_demo_pdf(self) -> str:
        """Generate demo PDF."""
        demo_data = {
            'patient': {
                'name': 'John Doe',
                'birth_date': '1980-01-15',
                'gender': 'Male',
                'patient_id': 'P001'
            },
            'provider': {
                'name': 'John Doe',
                'specialty': 'Internal Medicine',
                'license_number': 'MD123456'
            },
            'report': {
                'chief_complaint': 'Abdominal pain and vomiting',
                'history': '3 days ago, abdominal pain started and vomiting was accompanied',
                'physical_exam': 'Abdominal pain and vomiting',
                'diagnosis': 'Acute gastritis',
                'treatment': 'Antacids, fasting, slowly eating'
            }
        }
        
        return await self.generate_report_pdf(
            demo_data['report'],
            demo_data['patient'],
            demo_data['provider']
        )


# Global PDF service instance
pdf_service = PDFService()
