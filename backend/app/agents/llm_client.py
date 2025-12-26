import httpx
from typing import Optional
from ..config import get_settings


class GroqClient:
    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.groq_api_key
        self.model = self.settings.groq_model
        self.endpoint = "https://api.groq.com/openai/v1/chat/completions"

    def interpret_symptoms(self, symptoms: str, available_departments: list = None) -> Optional[str]:
        """
        Uses Groq LLM to suggest a department based on available departments in the hospital.
        Returns a department name string or None if unavailable/fails.
        """
        if not self.api_key:
            return None
        
        # Default departments if not provided
        if not available_departments:
            available_departments = ["General Medicine", "Cardiology", "Neurology", "Pediatrics", 
                                    "Orthopedics", "Dermatology", "ENT", "Psychiatry"]
        
        # Build department list for prompt
        dept_list = "\n".join([f"- {dept}" for dept in available_departments])
        
        # Check if General Medicine is available for fallback
        has_general_medicine = "General Medicine" in available_departments
        
        try:
            system_prompt = f"""You are an expert medical triage AI assistant working in a hospital emergency/OPD department. Your role is to route patients to the correct medical department based on their symptoms.

AVAILABLE DEPARTMENTS IN THIS HOSPITAL:
{dept_list}

COMPREHENSIVE MEDICAL SPECIALTY GUIDE:

🏥 GENERAL MEDICINE (Primary Care)
- General fever, cold, flu, cough, common infections
- Fatigue, weakness, general body ache
- Diabetes, hypertension, lifestyle diseases
- Viral infections, seasonal illnesses
- When no specific specialist is available
- Hair loss, hair fall (NOT Urology!)
- Vitamin deficiencies, anemia

❤️ CARDIOLOGY (Heart & Blood Vessels)
- Chest pain, tightness, pressure
- Heart palpitations, irregular heartbeat
- Shortness of breath (cardiac origin)
- High blood pressure emergencies
- Sweating with chest discomfort

🧠 NEUROLOGY (Brain & Nervous System)
- Headaches, migraines, severe head pain
- Seizures, epilepsy, convulsions
- Dizziness, vertigo (neurological)
- Numbness, tingling, paralysis
- Memory loss, confusion
- Stroke symptoms, facial drooping
- NOT digestive/GI issues!

👂 ENT (Ear, Nose, Throat)
- Ear pain, hearing loss, ear discharge
- Nose bleeding, nasal congestion, sinus
- Sore throat, throat pain, tonsillitis
- Voice problems, hoarseness
- Mouth sores, bleeding from mouth/nose/ear
- Difficulty swallowing (throat)

👁️ OPHTHALMOLOGY (Eyes)
- Eye pain, redness, irritation
- Vision problems, blurred vision
- Eye injury, foreign body
- Cataract, glaucoma symptoms
- Eye discharge, watering

🦴 ORTHOPEDICS (Bones, Joints, Muscles)
- Bone fractures, injuries
- Joint pain, arthritis
- Back pain, neck pain, spine issues
- Muscle strain, sprains
- Sports injuries
- Knee, hip, shoulder problems

🧒 PEDIATRICS (Children under 13 years)
- ALL symptoms in children below 13 years
- Child fever, cough, infections
- Growth & development issues
- Childhood illnesses

🧘 PSYCHIATRY (Mental Health)
- Depression, sadness, hopelessness
- Anxiety, panic attacks, stress
- Sleep disorders, insomnia
- Mood swings, behavioral issues
- Suicidal thoughts (emergency)
- Addiction, substance abuse

🔬 DERMATOLOGY (Skin, Hair, Nails - SKIN ONLY)
- Skin rashes, allergies, hives
- Acne, pimples, skin infections
- Eczema, psoriasis, skin conditions
- Burns (skin), wounds
- Moles, skin growths
- Fungal infections (skin)
- NOT hair fall (that's General Medicine/Endocrinology)

💊 UROLOGY (Kidney, Bladder, Urinary)
- Kidney stones, kidney pain
- Urinary problems, burning urination
- Bladder issues, frequent urination
- Blood in urine
- Prostate issues (male)
- NOT hair issues!

🍽️ GASTROENTEROLOGY (Digestive System)
- Stomach pain, abdomen pain
- Diarrhea, loose motions, constipation
- Vomiting, nausea (GI origin)
- Acidity, heartburn, GERD
- Indigestion, gas, bloating
- Liver, pancreas, intestinal issues
- Blood in stool

🫁 PULMONOLOGY (Lungs & Breathing)
- Chronic cough, persistent cough
- Asthma, wheezing
- Shortness of breath (lung origin)
- Chest congestion, phlegm
- Lung infections, bronchitis
- Tuberculosis symptoms

DECISION RULES:
1. Match symptoms to the medical specialty above
2. If department exists in available list → Return that department name
3. If department doesn't exist → Return 'General Medicine' as fallback
4. For children (under 13) → Always 'Pediatrics' if available
5. Return ONLY the department name, NO explanations

COMMON MISTAKES TO AVOID:
❌ Hair fall/loss is NOT Urology → General Medicine
❌ Digestive issues are NOT Neurology → Gastroenterology/General Medicine  
❌ Eye problems are NOT Dermatology → Ophthalmology/General Medicine
❌ Skin conditions only go to Dermatology, not hair/nails

OUTPUT: Return exactly one department name from the available list above."""
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {"role": "user", "content": f"Symptoms: {symptoms}\n\nDepartment:"},
                ],
                "temperature": 0.1,
                "max_tokens": 30,
            }
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            with httpx.Client(timeout=10.0) as client:
                response = client.post(self.endpoint, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                choice = data.get("choices", [{}])[0]
                content = choice.get("message", {}).get("content", "")
                result = content.strip() if content else None
                
                # Handle NOT_AVAILABLE response
                if result and result.upper() == "NOT_AVAILABLE":
                    return None
                    
                return result
        except Exception:
            return None

