"""
Clinical PDF Report Generation Service for ChronicCare.
Generates professional clinical reports with patient data and recommendations.
"""
from datetime import datetime
from io import BytesIO
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.utils.exceptions import ModelError
from app.utils.logging import get_logger

logger = get_logger(__name__)


class PDFReportService:
    """Service for generating clinical PDF reports."""

    def __init__(self) -> None:
        """Initialize PDF report service."""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self) -> None:
        """Setup custom paragraph styles for medical reports."""
        self.styles.add(
            ParagraphStyle(
                name="ClinicTitle",
                parent=self.styles["Heading1"],
                fontSize=20,
                textColor=colors.HexColor("#1F2937"),
                spaceAfter=6,
                alignment=1,  # Center
            )
        )

        self.styles.add(
            ParagraphStyle(
                name="ClinicHeading",
                parent=self.styles["Heading2"],
                fontSize=12,
                textColor=colors.HexColor("#374151"),
                spaceAfter=6,
                spaceBefore=12,
                borderColor=colors.HexColor("#E5E7EB"),
                borderWidth=1,
                borderPadding=4,
            )
        )

        self.styles.add(
            ParagraphStyle(
                name="ClinicBody",
                parent=self.styles["BodyText"],
                fontSize=10,
                leading=14,
                alignment=4,  # Justify
            )
        )

    async def generate_patient_report(
        self,
        patient_id: str,
        patient_name: str,
        patient_data: dict[str, Any],
        risk_assessment: dict[str, Any],
        clinical_notes: str,
        glossary_context: str,
    ) -> bytes:
        """
        Generate a comprehensive clinical report in PDF format.

        Args:
            patient_id: Patient identifier
            patient_name: Patient full name
            patient_data: Dictionary of patient health metrics
            risk_assessment: Risk assessment results
            clinical_notes: NOUR clinical reasoning notes
            glossary_context: Medical glossary context used

        Returns:
            PDF document as bytes

        Raises:
            ModelError: If PDF generation fails
        """
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=letter,
                rightMargin=0.75 * inch,
                leftMargin=0.75 * inch,
                topMargin=0.75 * inch,
                bottomMargin=0.75 * inch,
            )

            story = []

            # Header
            story.append(
                Paragraph("CHRONICCARE CLINICAL REPORT", self.styles["ClinicTitle"])
            )
            story.append(Spacer(1, 0.2 * inch))

            # Patient Information Section
            story.append(
                Paragraph("PATIENT INFORMATION", self.styles["ClinicHeading"])
            )
            patient_table_data = [
                ["Patient ID:", patient_id],
                ["Name:", patient_name],
                ["Report Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            ]
            patient_table = Table(patient_table_data, colWidths=[1.5 * inch, 4 * inch])
            patient_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F3F4F6")),
                        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#1F2937")),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 9),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                        ("TOPPADDING", (0, 0), (-1, -1), 4),
                        ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#E5E7EB")),
                    ]
                )
            )
            story.append(patient_table)
            story.append(Spacer(1, 0.3 * inch))

            # Vital Signs Section
            story.append(
                Paragraph("VITAL SIGNS & METRICS", self.styles["ClinicHeading"])
            )
            vital_signs_data = [
                ["Metric", "Value", "Status"],
                [
                    "Age",
                    f"{patient_data.get('age', 'N/A')} years",
                    self._get_status_badge(patient_data.get("age", 50), "age"),
                ],
                [
                    "BMI",
                    f"{patient_data.get('bmi', 'N/A')} kg/m²",
                    self._get_status_badge(patient_data.get("bmi", 25), "bmi"),
                ],
                [
                    "Blood Pressure",
                    f"{patient_data.get('systolic_bp', 'N/A')}/{patient_data.get('diastolic_bp', 'N/A')} mmHg",
                    self._get_status_badge(
                        patient_data.get("systolic_bp", 120), "bp"
                    ),
                ],
                [
                    "Fasting Glucose",
                    f"{patient_data.get('fasting_glucose', 'N/A')} mg/dL",
                    self._get_status_badge(
                        patient_data.get("fasting_glucose", 100), "glucose"
                    ),
                ],
            ]
            vitals_table = Table(vital_signs_data, colWidths=[2 * inch, 2 * inch, 1.5 * inch])
            vitals_table.setStyle(
                self._get_table_style(header_color=colors.HexColor("#D1D5DB"))
            )
            story.append(vitals_table)
            story.append(Spacer(1, 0.3 * inch))

            # Risk Assessment Section
            story.append(
                Paragraph("RISK ASSESSMENT", self.styles["ClinicHeading"])
            )
            risk_color = self._get_risk_color(risk_assessment.get("category", "MODERATE"))
            risk_table_data = [
                [
                    "Risk Category",
                    risk_assessment.get("category", "MODERATE"),
                ],
                [
                    "Risk Score",
                    f"{risk_assessment.get('risk_score', 0)}/10",
                ],
                [
                    "Monitoring Frequency",
                    risk_assessment.get("monitoring_frequency", "As clinically indicated"),
                ],
            ]
            risk_table = Table(risk_table_data, colWidths=[2 * inch, 3.5 * inch])
            risk_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F3F4F6")),
                        ("BACKGROUND", (1, 0), (1, 0), risk_color),
                        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#1F2937")),
                        ("TEXTCOLOR", (1, 0), (1, 0), colors.white),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                        ("FONTNAME", (1, 0), (1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 10),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                        ("TOPPADDING", (0, 0), (-1, -1), 6),
                        ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#E5E7EB")),
                    ]
                )
            )
            story.append(risk_table)
            story.append(Spacer(1, 0.3 * inch))

            # Clinical Notes Section
            story.append(
                Paragraph("CLINICAL ASSESSMENT", self.styles["ClinicHeading"])
            )
            story.append(Paragraph(clinical_notes, self.styles["ClinicBody"]))
            story.append(Spacer(1, 0.2 * inch))

            # Recommendations Section
            if risk_assessment.get("recommendations"):
                story.append(
                    Paragraph("RECOMMENDATIONS", self.styles["ClinicHeading"])
                )
                recommendations = risk_assessment.get("recommendations", [])
                for rec in recommendations:
                    story.append(
                        Paragraph(f"• {rec}", self.styles["ClinicBody"])
                    )
                story.append(Spacer(1, 0.2 * inch))

            # Footer
            story.append(Spacer(1, 0.3 * inch))
            story.append(
                Paragraph(
                    "This report was generated by ChronicCare AI system. "
                    "It is intended as a clinical support tool and should be reviewed by a qualified healthcare provider.",
                    self.styles["Normal"],
                )
            )

            # Build PDF
            doc.build(story)
            pdf_bytes = buffer.getvalue()
            buffer.close()

            logger.info(f"Generated PDF report for patient: {patient_id}")
            return pdf_bytes
        except Exception as e:
            logger.error(f"PDF generation failed: {str(e)}")
            raise ModelError(
                f"Failed to generate PDF report: {str(e)}",
                details={"patient_id": patient_id},
            )

    def _get_table_style(self, header_color: Any = None) -> TableStyle:
        """Get standard table style for reports."""
        return TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), header_color or colors.HexColor("#374151")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("TOPPADDING", (0, 0), (-1, 0), 8),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F9FAFB")),
                ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#E5E7EB")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9FAFB")]),
                ("FONTSIZE", (0, 1), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
                ("TOPPADDING", (0, 1), (-1, -1), 6),
            ]
        )

    def _get_status_badge(self, value: Any, metric_type: str) -> str:
        """Get status badge for metric value."""
        try:
            val = float(value)
            if metric_type == "age":
                return "Normal" if val < 65 else "Monitor"
            elif metric_type == "bmi":
                if val < 18.5:
                    return "Underweight"
                elif val < 25:
                    return "Normal"
                elif val < 30:
                    return "Overweight"
                else:
                    return "Obese"
            elif metric_type == "bp":
                if val < 120:
                    return "Normal"
                elif val < 140:
                    return "Elevated"
                else:
                    return "High"
            elif metric_type == "glucose":
                if val < 100:
                    return "Normal"
                elif val < 126:
                    return "Prediabetic"
                else:
                    return "Diabetic"
        except (ValueError, TypeError):
            pass
        return "Check"

    def _get_risk_color(self, category: str) -> Any:
        """Get color for risk category."""
        colors_map = {
            "LOW": colors.HexColor("#10B981"),  # Green
            "MODERATE": colors.HexColor("#F59E0B"),  # Amber
            "HIGH": colors.HexColor("#EF4444"),  # Red
        }
        return colors_map.get(category, colors.HexColor("#6B7280"))


# Global service instance
_pdf_service: "PDFReportService | None" = None


def get_pdf_service() -> PDFReportService:
    """Get or create PDF report service instance."""
    global _pdf_service
    if _pdf_service is None:
        _pdf_service = PDFReportService()
    return _pdf_service
