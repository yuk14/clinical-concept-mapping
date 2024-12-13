import streamlit as st
from datetime import datetime
from transformers import pipeline
import time
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import io

# Page config
st.set_page_config(
    page_title="Medical Report Generator",
    page_icon="🏥",
    layout="wide"
)

@st.cache_resource
def load_model():
    """Load the model with proper error handling"""
    try:
        generator = pipeline('text-generation', 
                           model='gpt2',
                           max_length=200)
        return generator
    except Exception as e:
        st.error(f"Model loading failed: {str(e)}")
        return None

def create_pdf(report_data):
    """Create PDF report with proper formatting"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceBefore=20,
        spaceAfter=10
    )
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceBefore=6,
        spaceAfter=6
    )
    
    # Content elements
    elements = []
    
    # Title
    elements.append(Paragraph("Medical Report", title_style))
    elements.append(Spacer(1, 20))
    
    # Date
    elements.append(Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", normal_style))
    elements.append(Spacer(1, 20))
    
    # Patient Information
    elements.append(Paragraph("Patient Information", heading_style))
    patient_data = [
        [Paragraph("Name:", normal_style), Paragraph(report_data['name'], normal_style)],
        [Paragraph("Age:", normal_style), Paragraph(str(report_data['age']), normal_style)],
        [Paragraph("Gender:", normal_style), Paragraph(report_data['gender'], normal_style)],
        [Paragraph("Patient ID:", normal_style), Paragraph(report_data['id'], normal_style)]
    ]
    patient_table = Table(patient_data, colWidths=[100, 400])
    patient_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(patient_table)
    
    # Vital Signs
    elements.append(Paragraph("Vital Signs", heading_style))
    vital_data = [
        [Paragraph("Temperature:", normal_style), Paragraph(f"{report_data['temperature']}°F", normal_style)],
        [Paragraph("Blood Pressure:", normal_style), Paragraph(report_data['blood_pressure'], normal_style)],
        [Paragraph("Heart Rate:", normal_style), Paragraph(f"{report_data['heart_rate']} bpm", normal_style)],
        [Paragraph("Respiratory Rate:", normal_style), Paragraph(f"{report_data['respiratory_rate']} breaths/min", normal_style)]
    ]
    vital_table = Table(vital_data, colWidths=[100, 400])
    vital_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(vital_table)
    
    # Symptoms
    elements.append(Paragraph("Chief Complaints & Symptoms", heading_style))
    elements.append(Paragraph(report_data['symptoms'], normal_style))
    
    # Medical History
    elements.append(Paragraph("Medical History", heading_style))
    elements.append(Paragraph(report_data['medical_history'], normal_style))
    
    # AI Assessment
    if 'ai_assessment' in report_data:
        elements.append(Paragraph("AI-Generated Assessment", heading_style))
        elements.append(Paragraph(report_data['ai_assessment'], normal_style))
    
    # Additional Notes
    elements.append(Paragraph("Additional Notes", heading_style))
    elements.append(Paragraph(report_data['additional_notes'], normal_style))
    
    # Footer
    elements.append(Spacer(1, 30))
    elements.append(Paragraph(
        f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey)
    ))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

# Initialize model at startup
with st.spinner("Loading AI model... (this may take a minute the first time)"):
    generator = load_model()

# Main title
st.title("🏥 Medical Report Generator")

# Sidebar for patient information
st.sidebar.header("Patient Information")
patient_name = st.sidebar.text_input("Patient Name")
patient_age = st.sidebar.number_input("Patient Age", min_value=0, max_value=120)
patient_gender = st.sidebar.selectbox("Patient Gender", ["Male", "Female", "Other"])
patient_id = st.sidebar.text_input("Patient ID")

# Main content
st.header("Clinical Information")

# Create columns for symptoms and medical history
col1, col2 = st.columns(2)

with col1:
    symptoms = st.text_area(
        "Chief Complaints & Symptoms",
        height=150,
        placeholder="Enter patient's current symptoms..."
    )
    
with col2:
    medical_history = st.text_area(
        "Medical History",
        height=150,
        placeholder="Enter patient's medical history..."
    )

# Vital signs
st.subheader("Vital Signs")
vital_cols = st.columns(4)
with vital_cols[0]:
    temperature = st.number_input("Temperature (°F)", min_value=95.0, max_value=105.0, value=98.6)
with vital_cols[1]:
    blood_pressure = st.text_input("Blood Pressure", placeholder="120/80")
with vital_cols[2]:
    heart_rate = st.number_input("Heart Rate (bpm)", min_value=40, max_value=200, value=75)
with vital_cols[3]:
    respiratory_rate = st.number_input("Respiratory Rate (breaths/min)", min_value=8, max_value=40, value=16)

# Additional notes
additional_notes = st.text_area(
    "Additional Notes",
    height=100,
    placeholder="Enter any additional observations or notes..."
)

# Generate Report button
if st.button("Generate Report", type="primary"):
    if not all([patient_name, patient_id, symptoms]):
        st.error("Please fill in at least the patient name, ID, and symptoms.")
        st.stop()
    
    try:
        # Prepare prompt for the model
        prompt = f"""Based on the following patient information, generate a medical assessment:
        Patient: {patient_name}, {patient_age} years old, {patient_gender}
        Symptoms: {symptoms}
        Medical History: {medical_history}
        Vitals: Temperature {temperature}°F, BP {blood_pressure}, HR {heart_rate}, RR {respiratory_rate}
        """
        
        with st.spinner("Generating AI assessment..."):
            if generator is not None:
                # Generate AI assessment
                ai_output = generator(prompt, max_length=300, num_return_sequences=1)[0]['generated_text']
                ai_assessment = ai_output[len(prompt):].strip()
            else:
                ai_assessment = "AI model not loaded properly. Using default assessment."
        
        # Prepare report data
        report_data = {
            'name': patient_name,
            'age': patient_age,
            'gender': patient_gender,
            'id': patient_id,
            'temperature': temperature,
            'blood_pressure': blood_pressure,
            'heart_rate': heart_rate,
            'respiratory_rate': respiratory_rate,
            'symptoms': symptoms,
            'medical_history': medical_history,
            'ai_assessment': ai_assessment,
            'additional_notes': additional_notes
        }
        
        # Generate PDF
        pdf_buffer = create_pdf(report_data)
        
        # Display success message
        st.success("Report generated successfully!")
        
        # Offer PDF download
        st.download_button(
            label="Download Report (PDF)",
            data=pdf_buffer,
            file_name=f"medical_report_{patient_id}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            mime="application/pdf"
        )
        
        # Display preview
        st.markdown("### Report Preview")
        st.markdown(f"""
        ## Medical Report
        
        **Date:** {datetime.now().strftime('%B %d, %Y')}
        
        ### Patient Information
        - **Name:** {patient_name}
        - **Age:** {patient_age}
        - **Gender:** {patient_gender}
        - **Patient ID:** {patient_id}
        
        ### Vital Signs
        - Temperature: {temperature}°F
        - Blood Pressure: {blood_pressure}
        - Heart Rate: {heart_rate} bpm
        - Respiratory Rate: {respiratory_rate} breaths/min
        
        ### Chief Complaints & Symptoms
        {symptoms}
        
        ### Medical History
        {medical_history}
        
        ### AI-Generated Assessment
        {ai_assessment}
        
        ### Additional Notes
        {additional_notes}
        
        *Report generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}*
        """)
        
    except Exception as e:
        st.error(f"Error generating report: {str(e)}")