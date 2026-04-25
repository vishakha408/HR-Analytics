"""PDF report generation for HR analytics"""

import io
import os
from datetime import datetime
import pandas as pd
import streamlit as st
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


def create_pdf_report(df_filtered: pd.DataFrame, kpis: dict, figures: list = None, 
                     output_path: str = "report.pdf"):
    """
    Create a PDF report with KPIs and figures
    
    Args:
        df_filtered: Filtered dataframe
        kpis: Dictionary with KPI values (attrition_pct, avg_salary, high_risk_pct, avg_tenure)
        figures: List of matplotlib figures to include
        output_path: Path to save PDF
    
    Returns:
        bytes: PDF file content
    """
    
    # Create PDF document
    buffer = io.BytesIO()
    pdf_path = output_path or "report.pdf"
    
    doc = SimpleDocTemplate(pdf_path, pagesize=letter,
                           rightMargin=0.5*inch, leftMargin=0.5*inch,
                           topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Container for PDF elements
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=10,
        fontName='Helvetica-Bold'
    )
    
    # Title
    elements.append(Paragraph("HR Analytics Report", title_style))
    elements.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}", 
                             styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    # KPI Section
    elements.append(Paragraph("Key Performance Indicators", heading_style))
    
    kpi_data = [
        ['Metric', 'Value'],
        ['Attrition Rate', f"{kpis.get('attrition_pct', 0):.1f}%"],
        ['Average Salary', f"${kpis.get('avg_salary', 0):,.0f}"],
        ['High-Risk Employees', f"{kpis.get('high_risk_pct', 0):.1f}%"],
        ['Average Tenure', f"{kpis.get('avg_tenure', 0):.1f} years"],
        ['Total Employees', f"{kpis.get('total_employees', 0)}"]
    ]
    
    kpi_table = Table(kpi_data, colWidths=[3*inch, 2*inch])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(kpi_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Dataset Summary
    elements.append(Paragraph("Dataset Summary", heading_style))
    dataset_info = f"""
    <b>Total Records:</b> {len(df_filtered)}<br/>
    <b>Departments:</b> {df_filtered['Department'].nunique() if 'Department' in df_filtered.columns else 'N/A'}<br/>
    <b>Job Roles:</b> {df_filtered['JobRole'].nunique() if 'JobRole' in df_filtered.columns else 'N/A'}<br/>
    <b>Date Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    elements.append(Paragraph(dataset_info, styles['Normal']))
    elements.append(Spacer(1, 0.2*inch))
    
    # Add figures if provided
    if figures:
        elements.append(PageBreak())
        elements.append(Paragraph("Visualizations", heading_style))
        
        for i, fig in enumerate(figures):
            if fig is not None:
                # Save figure temporarily
                temp_path = f"/tmp/fig_{i}.png"
                fig.savefig(temp_path, dpi=100, bbox_inches='tight')
                
                # Add to PDF
                img = Image(temp_path, width=6*inch, height=4*inch)
                elements.append(img)
                elements.append(Spacer(1, 0.2*inch))
                
                # Cleanup
                if os.path.exists(temp_path):
                    os.remove(temp_path)
    
    # Build PDF
    doc.build(elements)
    
    # Read PDF as bytes
    with open(pdf_path, 'rb') as f:
        pdf_bytes = f.read()
    
    return pdf_bytes, pdf_path


def export_predictions_to_excel(df_predictions: pd.DataFrame, output_path: str = "predictions.xlsx"):
    """
    Export predictions to Excel format
    
    Args:
        df_predictions: DataFrame with predictions
        output_path: Path to save Excel file
    
    Returns:
        bytes: Excel file content
    """
    
    buffer = io.BytesIO()
    
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_predictions.to_excel(writer, index=False, sheet_name='Predictions')
        
        # Add summary sheet
        summary_data = {
            'Metric': ['Total Predictions', 'Attrition Risk (High)', 'Attrition Risk (Low)', 
                      'Average Probability', 'Export Date'],
            'Value': [
                len(df_predictions),
                (df_predictions['prediction_label'] == 'At Risk').sum() if 'prediction_label' in df_predictions.columns else 0,
                (df_predictions['prediction_label'] == 'Stable').sum() if 'prediction_label' in df_predictions.columns else 0,
                f"{df_predictions['prediction_prob'].mean():.2%}" if 'prediction_prob' in df_predictions.columns else 'N/A',
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, index=False, sheet_name='Summary')
    
    buffer.seek(0)
    return buffer.getvalue(), output_path


@st.cache_data
def prepare_export_data(df_predictions: pd.DataFrame) -> bytes:
    """Prepare data for export (cached)"""
    excel_bytes, _ = export_predictions_to_excel(df_predictions)
    return excel_bytes
