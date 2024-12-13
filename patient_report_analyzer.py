import json
import re
import torch
import numpy as np
import pandas as pd
import streamlit as st
import pdfplumber

from transformers import (
    AutoModelForTokenClassification, 
    AutoTokenizer, 
    pipeline,
    AutoModelForSequenceClassification
)

class AdvancedMedicalIntelligenceSystem:
    def __init__(self):
        # Device configuration
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Advanced Biomedical NER Model
        self._initialize_ner_model()
        
        # Medical Specialty Classification Model
        self._initialize_specialty_model()
        
        # Medical Risk Assessment Knowledge Base
        self._load_risk_knowledge_base()

    def _initialize_ner_model(self):
        try:
            self.ner_tokenizer = AutoTokenizer.from_pretrained("d4data/biomedical-ner-all")
            self.ner_model = AutoModelForTokenClassification.from_pretrained("d4data/biomedical-ner-all")
            
            self.ner_pipeline = pipeline(
                "ner", 
                model=self.ner_model, 
                tokenizer=self.ner_tokenizer,
                aggregation_strategy="simple",
                device=0 if torch.cuda.is_available() else -1
            )
        except Exception as e:
            st.error(f"Error loading NER model: {e}")
            self.ner_pipeline = None

    def _initialize_specialty_model(self):
        try:
            self.specialty_tokenizer = AutoTokenizer.from_pretrained(
                "microsoft/BiomedNLP-BiomedBERT-base-uncased-abstract"
            )
            self.specialty_model = AutoModelForSequenceClassification.from_pretrained(
                "microsoft/BiomedNLP-BiomedBERT-base-uncased-abstract"
            )
            
            self.specialty_model.classifier = torch.nn.Linear(
                self.specialty_model.config.hidden_size, 
                7  # Match the number of specialties
            )
        except Exception as e:
            st.error(f"Error loading specialty classification model: {e}")
            self.specialty_model = None

    def _load_risk_knowledge_base(self):
        try:
            with open('medical_risk_knowledge_base.json', 'r') as f:
                self.risk_knowledge_base = json.load(f)
        except FileNotFoundError:
            st.warning("Medical risk knowledge base not found. Using default minimal knowledge base.")
            self.risk_knowledge_base = {
                "default": {
                    "base_risk": "Low",
                    "risk_factors": ["General health assessment recommended"],
                    "recommended_actions": ["Consult with primary care physician"]
                }
            }

    def extract_pdf_text(self, pdf_file):
        """Advanced PDF text extraction with error handling"""
        try:
            with pdfplumber.open(pdf_file) as pdf:
                full_text = "\n".join([
                    page.extract_text() for page in pdf.pages 
                    if page.extract_text() is not None
                ])
                return full_text
        except Exception as e:
            st.error(f"Critical PDF extraction error: {e}")
            return ""

    def advanced_medical_ner(self, text):
        """Advanced Biomedical Named Entity Recognition"""
        if not self.ner_pipeline:
            st.warning("NER model not loaded. Using fallback method.")
            return self._fallback_entity_extraction(text)
    
        try:
            # Truncate text to model's max length
            max_length = self.ner_tokenizer.model_max_length
            text = text[:max_length]
            
            # Perform Named Entity Recognition
            entities = self.ner_pipeline(text)
            
            # Updated organized entities with fallback
            organized_entities = {
                "Medical_Conditions": [],
                "Medications": [],
                "Procedures": [],
                "Lab_Results": []
            }
            
            # Process and categorize entities
            for entity in entities:
                entity_text = entity.get('word', '')
                entity_type = entity.get('entity_group', '').lower()
                
                if not entity_text:
                    continue
                
                # Categorize entities
                if any(keyword in entity_type for keyword in ['disease', 'condition', 'disorder']):
                    if entity_text not in organized_entities["Medical_Conditions"]:
                        organized_entities["Medical_Conditions"].append(entity_text)
                
                elif any(keyword in entity_type for keyword in ['drug', 'medication', 'medicine']):
                    if entity_text not in organized_entities["Medications"]:
                        organized_entities["Medications"].append(entity_text)
                
                elif any(keyword in entity_type for keyword in ['procedure', 'test', 'exam', 'treatment']):
                    if entity_text not in organized_entities["Procedures"]:
                        organized_entities["Procedures"].append(entity_text)
                
                # Capture numerical lab results
                if re.search(r'\d+(\.\d+)?', entity_text):
                    if entity_text not in organized_entities["Lab_Results"]:
                        organized_entities["Lab_Results"].append(entity_text)
            
            return organized_entities
        
        except Exception as e:
            st.error(f"Error in advanced NER: {e}")
            return self._fallback_entity_extraction(text)

    def _fallback_entity_extraction(self, text):
        """Fallback method for entity extraction"""
        entities = {
            "Medical_Conditions": [],
            "Medications": [],
            "Procedures": [],
            "Lab_Results": []
        }
        
        # Enhanced fallback regex patterns
        patterns = {
            "Medical_Conditions": [
                r'\b(diabetes|hypertension|cancer|heart disease|syndrome|disorder|condition|)\b',
            ],
            "Medications": [
                r'\b(insulin|aspirin|metformin|warfarin|medication|drug)\b',
            ],
            "Procedures": [
                r'\b(surgery|biopsy|MRI|CT scan|X-ray|test|screening|examination)\b',
            ],
            "Lab_Results": [
                r'\b(\d+(\.\d+)?)\s*(mg/dL|mmHg|%|ml|g/dL)\b'
            ]
        }
        
        # Extract entities using regex
        for category, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = re.findall(pattern, text, re.IGNORECASE)
                unique_matches = list(set([match[0] if isinstance(match, tuple) else match for match in matches]))
                entities[category].extend(unique_matches)
        
        return entities

    def medical_specialty_classification(self, text):
        """Advanced Medical Specialty Classification"""
        if not self.specialty_model or not self.specialty_tokenizer:
            st.warning("Specialty classification model not loaded.")
            return {"Relevant_Medical_Specialties": []}
        
        try:
            # Predefined medical specialties
            specialties = [
                "Cardiology", "Oncology", "Neurology", 
                "Endocrinology", "Pulmonology", "Gastroenterology", "Hematology"
            ]
            
            # Truncate text to model's max length
            max_length = self.specialty_tokenizer.model_max_length
            text = text[:max_length]
            
            # Prepare input
            inputs = self.specialty_tokenizer(
                text, 
                return_tensors="pt", 
                truncation=True, 
                max_length=max_length
            )
            
            # Move inputs to the same device as the model
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            self.specialty_model.to(self.device)
            
            # Perform classification
            with torch.no_grad():
                outputs = self.specialty_model(**inputs)
                
                # Use safe conversion methods
                logits = outputs.logits.cpu()
                probabilities = torch.nn.functional.softmax(logits, dim=1)
            
            # Safely process predictions
            relevant_specialties = []
            for i, specialty in enumerate(specialties):
                try:
                    confidence = probabilities[0][i].item() * 100
                    if confidence > 30:  # Significance threshold
                        relevant_specialties.append({
                            "specialty": specialty,
                            "confidence": round(confidence, 2)
                        })
                except Exception as conversion_error:
                    st.warning(f"Error processing {specialty}: {conversion_error}")
            
            return {
                "Relevant_Medical_Specialties": relevant_specialties
            }
        
        except Exception as e:
            st.error(f"Error in specialty classification: {e}")
            return {"Relevant_Medical_Specialties": []}

    def medical_risk_assessment(self, text, entities):
        """Advanced Medical Risk Assessment"""
        # Enhanced risk assessment logic
        risk_assessment = {
            "Overall_Risk_Level": "Low",
            "Detailed_Risk_Breakdown": {},
            "Recommended_Interventions": []
        }
        
        # Analyze risk based on detected entities
        for condition in entities.get("Medical_Conditions", []):
            # Lookup condition in knowledge base, use default if not found
            condition_risk = self.risk_knowledge_base.get(
                condition.lower(), 
                self.risk_knowledge_base.get("default")
            )
            
            risk_assessment["Detailed_Risk_Breakdown"][condition] = {
                "Risk_Level": condition_risk["base_risk"],
                "Risk_Factors": condition_risk["risk_factors"]
            }
            
            # Accumulate unique interventions
            risk_assessment["Recommended_Interventions"].extend(
                [action for action in condition_risk["recommended_actions"] 
                 if action not in risk_assessment["Recommended_Interventions"]]
            )
        
        # Adjust risk level based on multiple conditions
        high_risk_conditions = [
            c for c, details in risk_assessment["Detailed_Risk_Breakdown"].items()
            if details["Risk_Level"] == "High"
        ]
        
        if len(high_risk_conditions) > 1:
            risk_assessment["Overall_Risk_Level"] = "High"
        elif high_risk_conditions:
            risk_assessment["Overall_Risk_Level"] = "Moderate"
        
        # Remove duplicates from recommended interventions
        risk_assessment["Recommended_Interventions"] = list(dict.fromkeys(risk_assessment["Recommended_Interventions"]))
        
        return risk_assessment


def main():
    st.set_page_config(page_title="Advanced Medical Intelligence", layout="wide")
    
    # Initialize system
    system = AdvancedMedicalIntelligenceSystem()
    
    st.title("🩺 Advanced Biomedical Intelligence Analysis")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Upload Medical Report (PDF)", 
        type=["pdf"], 
        help="Upload a medical PDF for comprehensive biomedical analysis"
    )
    
    if uploaded_file:
        with st.spinner("🔬 Performing Advanced Biomedical Analysis..."):
            try:
                # Process medical document
                raw_text = system.extract_pdf_text(uploaded_file)
                
                if not raw_text:
                    st.error("Unable to extract text from the PDF. Please check the document.")
                    return
                
                # Advanced entity recognition
                medical_entities = system.advanced_medical_ner(raw_text)
                
                # Medical specialty classification
                medical_insights = system.medical_specialty_classification(raw_text)
                
                # Risk assessment
                risk_assessment = system.medical_risk_assessment(raw_text, medical_entities)
                
                # Display comprehensive report
                st.header("🏥 Comprehensive Biomedical Intelligence Report")
                
                # Medical Specialties Relevance
                st.subheader("📊 Relevant Medical Specialties")
                specialties = medical_insights.get("Relevant_Medical_Specialties", [])
                
                if specialties:
                    cols = st.columns(len(specialties))
                    for i, specialty in enumerate(specialties):
                        with cols[i]:
                            st.metric(
                                specialty['specialty'], 
                                f"{specialty['confidence']}%"
                            )
                else:
                    st.warning("No specific medical specialties identified")
                
                # Detailed Entity Extraction
                st.subheader("🔍 Detailed Medical Entities")
                
                # Display different entity categories in rows
                entity_categories = [
                    ("Medical_Conditions", "🩺"),
                    ("Medications", "💊"),
                    ("Procedures", "🩸"),
                    ("Lab_Results", "🧪")
                ]
                
                # Create 4 columns for entity categories
                cols = st.columns(4)
                
                # Display entities in columns
                for i, (category, emoji) in enumerate(entity_categories):
                    with cols[i]:
                        st.markdown(f"**{emoji} {category.replace('_', ' ')}**")
                        
                        # Get entities for this category
                        entities = medical_entities.get(category, [])
                        
                        if entities:
                            for entity in entities:
                                st.write(f"- {entity}")
                        else:
                            st.write(f"No {category.lower().replace('_', ' ')} detected")
                
                # Risk Assessment
                st.subheader("⚠️ Medical Risk Stratification")
                
                # Overall Risk
                st.write(f"**Overall Risk Level:** {risk_assessment['Overall_Risk_Level']}")
                
                # Detailed Risk Breakdown
                st.write("**Detailed Risk Breakdown:**")
                risk_breakdown = risk_assessment.get("Detailed_Risk_Breakdown", {})
                
                if risk_breakdown:
                    for condition, details in risk_breakdown.items():
                        st.write(f"- **{condition}**")
                        st.write(f"  Risk Level: {details['Risk_Level']}")
                        st.write(f"  Risk Factors: {', '.join(details['Risk_Factors'])}")
                else:
                    st.write("No specific risk factors identified")
                
                # Recommended Interventions
                st.write("**Recommended Interventions:**")
                interventions = risk_assessment.get("Recommended_Interventions", [])
                
                if interventions:
                    for intervention in interventions:
                        st.write(f"- {intervention}")
                else:
                    st.write("No specific interventions recommended")
            
            except Exception as e:
                st.error(f"An unexpected error occurred during analysis: {e}")

if __name__ == "__main__":
    main()zzz