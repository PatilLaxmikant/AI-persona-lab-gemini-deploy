# #  in main repository
# from datetime import datetime
# from typing import List, Optional
# import uuid
# import json
# import requests
# import os
# from pydantic import BaseModel

# OLLAMA_API_URL = "http://127.0.0.1:11434/api"
# # OLLAMA_API_URL = "http://localhost:11434/api"

# class Persona(BaseModel):
#     id: str
#     name: str
#     age: int
#     nationality: str
#     occupation: str
#     background: str
#     routine: str
#     personality: str
#     skills: List[str]
#     avatar: str
#     model: str
#     temperature: float = 0.7
#     max_tokens: int = 1000
#     created_at: datetime
#     modified_at: datetime
#     tags: List[str] = []
#     notes: str = ""

# class PersonaManager:
#     def __init__(self):
#         self.personas = []
#         self.settings = {
#             "default_model": None,
#             "default_temperature": 0.7,
#             "default_max_tokens": 1000
#         }
#         self._load_settings()
#         self._load_personas()
    
#     def _load_personas(self):
#         try:
#             with open("data/personas.json", "r") as f:
#                 data = json.load(f)
#                 self.personas = [Persona(**p) for p in data]
#         except FileNotFoundError:
#             self.personas = []
    
#     def _save_personas(self):
#         with open("data/personas.json", "w") as f:
#             json.dump([p.dict() for p in self.personas], f, default=str)
    
#     def _load_settings(self):
#         """Load settings from settings.json"""
#         try:
#             with open("data/settings.json", "r") as f:
#                 loaded_settings = json.load(f)
#                 self.settings.update(loaded_settings)
#         except FileNotFoundError:
#             self._save_settings()
    
#     def _save_settings(self):
#         """Save settings to settings.json"""
#         os.makedirs("data", exist_ok=True)
#         with open("data/settings.json", "w") as f:
#             json.dump(self.settings, f)
    
#     def update_settings(self, settings: dict):
#         """Update settings and save them"""
#         # Update settings
#         self.settings.update(settings)
#         self._save_settings()
    
#     def get_settings(self) -> dict:
#         """Get current settings"""
#         return self.settings.copy()

#     def generate_persona(self, occupation: str, model: str = None, temperature: float = None, max_tokens: int = None) -> Optional[Persona]:
#         """Generate a new persona with the given occupation using Ollama."""
#         # Use provided model or fall back to default
#         if model is None:
#             model = self.settings.get("default_model")
            
#         # If still no model, try to get available models
#         if model is None:
#             available_models = self.get_available_models()
#             if available_models:
#                 model = available_models[0]
#             else:
#                 raise ValueError("No available models")
                
#         if temperature is None:
#             temperature = self.settings["default_temperature"]
#         if max_tokens is None:
#             max_tokens = self.settings["default_max_tokens"]

#         # Ensure max_tokens is large enough for complete responses
#         if max_tokens < 1000:
#             max_tokens = 1000

#         prompt = f"""You are a JSON generator for creating detailed, realistic personas. You must ONLY output a valid JSON object - no other text.
#         Generate a CONCISE persona for a {occupation} using this exact format:

# {{
#     "name": "Example Name",
#     "age": 35,
#     "nationality": "Example Nationality",
#     "occupation": "{occupation}",
#     "background": "One sentence about education and career.",
#     "routine": "One sentence about daily schedule.",
#     "personality": "One sentence about traits.",
#     "skills": [
#         "Skill 1",
#         "Skill 2",
#         "Skill 3"
#     ]
# }}

# IMPORTANT:
# 1. Output ONLY valid JSON - no other text
# 2. Keep all text fields SHORT (one sentence each)
# 3. Age between 25-65
# 4. Use proper JSON quotes and commas
# 5. Ensure JSON is complete and valid"""

#         try:
#             response = requests.post(
#                 f"{OLLAMA_API_URL}/generate",
#                 json={
#                     "model": model,
#                     "prompt": prompt,
#                     "stream": False,
#                     "options": {
#                         "temperature": temperature,
#                         "num_predict": max_tokens
#                     }
#                 }
#             )
#             response.raise_for_status()
            
#             # Extract and validate the response
#             result = response.json()
#             try:
#                 # Clean the response string
#                 response_text = result["response"].strip()
                
#                 # Find the JSON object
#                 start_idx = response_text.find("{")
#                 end_idx = response_text.rfind("}") + 1
                
#                 if start_idx == -1 or end_idx == 0:
#                     print("Raw response:", response_text)
#                     raise ValueError("No JSON object found in response")
                
#                 # Extract just the JSON part
#                 json_text = response_text[start_idx:end_idx]
                
#                 # Try to parse the JSON
#                 try:
#                     persona_data = json.loads(json_text)
#                 except json.JSONDecodeError:
#                     # If parsing fails, try to fix common issues
#                     # 1. Fix unterminated strings by adding missing quotes
#                     lines = json_text.split('\n')
#                     fixed_lines = []
#                     for i, line in enumerate(lines):
#                         line = line.rstrip()
#                         if i < len(lines) - 1 and ':' in line and not line.rstrip().endswith(',') and not line.rstrip().endswith('{'):
#                             if line.count('"') % 2 == 1:  # Unterminated string
#                                 line = line + '"'
#                             line = line + ','
#                         fixed_lines.append(line)
#                     json_text = '\n'.join(fixed_lines)
                    
#                     # Try parsing again
#                     persona_data = json.loads(json_text)
                
#             except Exception as e:
#                 print("Raw response:", result["response"])
#                 print("JSON error:", str(e))
#                 raise ValueError("Invalid JSON response from model")
            
#             # Validate required fields
#             required_fields = ["name", "age", "nationality", "background", "routine", "personality", "skills"]
#             missing_fields = [field for field in required_fields if field not in persona_data]
#             if missing_fields:
#                 print("Raw response:", result["response"])
#                 raise ValueError(f"Missing required fields in persona data: {missing_fields}")
            
#             if not isinstance(persona_data["skills"], list) or len(persona_data["skills"]) < 1:
#                 raise ValueError("Skills must be a non-empty list")
            
#             if not (25 <= persona_data["age"] <= 65):
#                 raise ValueError("Age must be between 25 and 65")
            
#             # Create new persona with validated data
#             new_persona = Persona(
#                 id=str(uuid.uuid4()),
#                 name=persona_data["name"],
#                 age=persona_data["age"],
#                 nationality=persona_data["nationality"],
#                 occupation=occupation,
#                 background=persona_data["background"],
#                 routine=persona_data["routine"],
#                 personality=persona_data["personality"],
#                 skills=persona_data["skills"],
#                 avatar=self._generate_avatar(persona_data["name"]),
#                 model=model,
#                 temperature=temperature,
#                 max_tokens=max_tokens,
#                 created_at=datetime.now(),
#                 modified_at=datetime.now()
#             )
            
#             self.personas.append(new_persona)
#             self._save_personas()
#             return new_persona
            
#         except json.JSONDecodeError as e:
#             print(f"Error decoding JSON response: {str(e)}")
#             if response and response.text:
#                 print(f"Raw response: {response.text}")
#             return None
#         except Exception as e:
#             print(f"Error generating persona: {str(e)}")
#             return None
    
#     def update_persona(self, persona: Persona):
#         """Update an existing persona"""
#         for i, p in enumerate(self.personas):
#             if p.id == persona.id:
#                 persona.modified_at = datetime.now()
#                 self.personas[i] = persona
#                 self._save_personas()
#                 return True
#         return False

#     def get_available_models(self) -> List[str]:
#         """Get list of available Ollama models"""
#         try:
#             response = requests.get(f"{OLLAMA_API_URL}/tags")
#             if response.status_code == 200:
#                 models_data = response.json()["models"]
#                 return [model["name"] for model in models_data] if models_data else []
#             return []
#         except Exception as e:
#             print(f"Error fetching models: {str(e)}")
#             return []
    
#     def _generate_avatar(self, name: str) -> str:
#         """Generate an avatar URL using DiceBear API."""
#         seed = str(uuid.uuid5(uuid.NAMESPACE_DNS, name))
#         return f"https://api.dicebear.com/7.x/personas/svg?seed={seed}"
    
#     def list_personas(self) -> List[Persona]:
#         """Return list of all personas."""
#         return self.personas
    
#     def get_persona(self, persona_id: str) -> Optional[Persona]:
#         """Get a specific persona by ID."""
#         return next((p for p in self.personas if p.id == persona_id), None)
    
#     def remove_persona(self, persona_id: str) -> bool:
#         """Remove a persona by ID."""
#         persona = self.get_persona(persona_id)
#         if persona:
#             self.personas.remove(persona)
#             self._save_personas()
#             return True
#         return False

#     def create_default_persona(self):
#         """Create a default persona to get users started"""
#         default_persona = {
#             "id": str(uuid.uuid4()),
#             "name": "Assistant",
#             "age": 28,
#             "nationality": "International",
#             "occupation": "AI Assistant",
#             "background": "I am a helpful AI assistant with expertise in various fields. I enjoy helping users accomplish their goals and learning from our interactions.",
#             "personality": "Friendly, professional, and detail-oriented. I maintain a positive attitude while focusing on delivering accurate and helpful information.",
#             "routine": "Available 24/7 to assist users with their queries and tasks. I continuously learn from interactions to provide better assistance.",
#             "skills": ["Communication", "Problem Solving", "Research", "Technical Support", "Creative Thinking"],
#             "model": self.settings["default_model"] if self.settings["default_model"] is not None else "default_model_name",
#             "temperature": self.settings["default_temperature"],
#             "max_tokens": self.settings["default_max_tokens"],
#             "notes": "Default assistant persona to help you get started with AI Persona Lab.",
#             "tags": ["assistant", "helpful", "default"],
#             "created_at": datetime.now(),
#             "modified_at": datetime.now()
#         }
        
#         # Generate an avatar for the default persona
#         avatar = self._generate_avatar(default_persona["name"])
#         default_persona["avatar"] = avatar
        
#         # Create and save the persona
#         persona = Persona(**default_persona)
#         self.personas.append(persona)
#         self._save_personas()
#         return persona



# without ollama, using gemini API for deployed model

from datetime import datetime
from typing import List, Optional
import uuid
import json
import os
from pydantic import BaseModel
import streamlit as st 
import google.generativeai as genai 
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, JSON as SQLJSON, Text
from sqlalchemy.orm import sessionmaker, declarative_base, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

# --- Configure Google API ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except Exception as e:
    st.error("Could not configure Google API. Is 'GOOGLE_API_KEY' in .streamlit/secrets.toml?")

# --- Database Setup ---
try:
    # Get the database URL from secrets
    DB_URL = st.secrets["DATABASE_URL"]
except Exception as e:
    st.error("Database URL not found. Is 'DATABASE_URL' in .streamlit/secrets.toml?")
    st.stop()

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# --- SQL Model for Persona ---
class DBPersona(Base):
    __tablename__ = "personas"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String, nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    nationality: Mapped[str] = mapped_column(String)
    occupation: Mapped[str] = mapped_column(String)
    background: Mapped[str] = mapped_column(Text)
    routine: Mapped[str] = mapped_column(Text)
    personality: Mapped[str] = mapped_column(Text)
    skills: Mapped[list] = mapped_column(SQLJSON)
    avatar: Mapped[str] = mapped_column(String)
    model: Mapped[str] = mapped_column(String)
    temperature: Mapped[float] = mapped_column(Float, default=0.7)
    max_tokens: Mapped[int] = mapped_column(Integer, default=1000)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    modified_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    tags: Mapped[list] = mapped_column(SQLJSON, default=list)
    notes: Mapped[str] = mapped_column(Text, default="")

# Create the table if it doesn't exist
Base.metadata.create_all(bind=engine)


# --- Pydantic Model (This is what our app uses) ---
class Persona(BaseModel):
    id: str
    name: str
    age: int
    nationality: str
    occupation: str
    background: str
    routine: str
    personality: str
    skills: List[str]
    avatar: str
    model: str
    temperature: float = 0.7
    max_tokens: int = 1000
    created_at: datetime
    modified_at: datetime
    tags: List[str] = []
    notes: str = ""

    # Allow conversion from the SQL model
    class Config:
        from_attributes = True # This is the Pydantic V2 setting


# --- Main Persona Manager ---
class PersonaManager:
    def __init__(self):
        self.settings = {
            # Use the correct, valid model names
            "default_model": "gemini-2.5-flash",
            "default_temperature": 0.7,
            "default_max_tokens": 1000
        }
    
    def _get_db(self):
        # Helper to get a new database session
        return SessionLocal()

    # --- CRUD Operations ---
    
    def list_personas(self) -> List[Persona]:
        """Load all personas from the database."""
        db = self._get_db()
        try:
            db_personas = db.query(DBPersona).all()
            # Convert SQL models to Pydantic models
            return [Persona.from_orm(p) for p in db_personas]
        finally:
            db.close()
    
    def get_persona(self, persona_id: str) -> Optional[Persona]:
        """Get a single persona by ID."""
        db = self._get_db()
        try:
            db_persona = db.query(DBPersona).filter(DBPersona.id == persona_id).first()
            if db_persona:
                return Persona.from_orm(db_persona)
            return None
        finally:
            db.close()

    def update_persona(self, persona: Persona):
        """Update an existing persona in the database."""
        db = self._get_db()
        try:
            db_persona = db.query(DBPersona).filter(DBPersona.id == persona.id).first()
            if db_persona:
                # Update all fields from the Pydantic model
                db_persona.name = persona.name
                db_persona.age = persona.age
                db_persona.nationality = persona.nationality
                db_persona.occupation = persona.occupation
                db_persona.background = persona.background
                db_persona.routine = persona.routine
                db_persona.personality = persona.personality
                db_persona.skills = persona.skills
                db_persona.model = persona.model
                db_persona.temperature = persona.temperature
                db_persona.max_tokens = persona.max_tokens
                db_persona.tags = persona.tags
                db_persona.notes = persona.notes
                db_persona.modified_at = datetime.now() # Manually set update time
                
                db.commit()
                return True
            return False
        finally:
            db.close()

    def remove_persona(self, persona_id: str) -> bool:
        """Remove a persona by ID from the database."""
        db = self._get_db()
        try:
            db_persona = db.query(DBPersona).filter(DBPersona.id == persona_id).first()
            if db_persona:
                db.delete(db_persona)
                db.commit()
                return True
            return False
        finally:
            db.close()

    def generate_persona(self, occupation: str, model: str, temperature: float, max_tokens: int) -> Optional[Persona]:
        """Generate a new persona with Google and save it to the database."""
        
        prompt = f"""
        You are a JSON generator for creating detailed, realistic personas. 
        You must ONLY output a valid JSON object.
        Generate a CONCISE persona for a {occupation} using this exact format:

        {{
            "name": "Example Name",
            "age": 35,
            "nationality": "Example Nationality",
            "occupation": "{occupation}",
            "background": "One sentence about education and career.",
            "routine": "One sentence about daily schedule.",
            "personality": "One sentence about traits.",
            "skills": [
                "Skill 1",
                "Skill 2",
                "Skill 3"
            ]
        }}
        
        RULES:
        1. Output ONLY valid JSON. No other text or markdown.
        2. Keep all text fields SHORT (one sentence each).
        3. Age must be between 25-65.
        4. ALL fields are required.
        """

        try:
            # Use the correct, valid model name
            gen_model = genai.GenerativeModel('gemini-2.5-flash')
            
            response = gen_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    response_mime_type="application/json"
                )
            )
            persona_data = json.loads(response.text)
            
            # --- THIS IS THE FIX for KeyError: 'name' ---
            # Validate the JSON data before trying to use it
            required_fields = ["name", "age", "nationality", "background", "routine", "personality", "skills"]
            missing_fields = [field for field in required_fields if field not in persona_data]
            
            if missing_fields:
                print(f"API returned incomplete JSON. Missing fields: {missing_fields}")
                print(f"Raw response: {response.text}")
                raise ValueError(f"Failed to generate complete persona, missing: {', '.join(missing_fields)}")
            # --- END FIX ---

            # Create the Pydantic model first (this is now safe)
            new_persona = Persona(
                id=str(uuid.uuid4()),
                name=persona_data["name"],
                age=persona_data["age"],
                nationality=persona_data["nationality"],
                occupation=occupation,
                background=persona_data["background"],
                routine=persona_data["routine"],
                personality=persona_data["personality"],
                skills=persona_data["skills"],
                avatar=self._generate_avatar(persona_data["name"]),
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                created_at=datetime.now(),
                modified_at=datetime.now()
            )

            # Now create the SQL model and save it
            db = self._get_db()
            try:
                db_persona = DBPersona(**new_persona.dict())
                db.add(db_persona)
                db.commit()
                return new_persona
            finally:
                db.close()
            
        except Exception as e:
            print(f"Error generating persona: {str(e)}")
            if 'response' in locals() and hasattr(response, 'text'):
                print(f"Raw response: {response.text}")
            return None

    def create_default_persona(self):
        """Create a default persona and save it to the database."""
        
        default_model = self.settings["default_model"]
        
        default_persona = Persona(
            id=str(uuid.uuid4()),
            name="Assistant",
            age=28,
            nationality="Digital",
            occupation="AI Assistant",
            background="I am a helpful AI assistant built to help you with your persona lab. I run on Google's Gemini models.",
            personality="Friendly, professional, and detail-oriented. I focus on delivering accurate and helpful information.",
            routine="Available 24/7 to assist users with their queries and tasks.",
            skills=["Communication", "Problem Solving", "Research", "Streamlit", "Python"],
            avatar=self._generate_avatar("Assistant"),
            model=default_model,
            temperature=self.settings["default_temperature"],
            max_tokens=self.settings["default_max_tokens"],
            notes="Default assistant persona to help you get started with AI Persona Lab.",
            tags=["assistant", "helpful", "default"],
            created_at=datetime.now(),
            modified_at=datetime.now()
        )
        
        # Save the new default persona to the database
        db = self._get_db()
        try:
            db_persona = DBPersona(**default_persona.dict())
            db.add(db_persona)
            db.commit()
        finally:
            db.close()
        return default_persona

    def get_available_models(self) -> List[str]:
        """
        Get list of available Google models for the UI.
        """
        # Return the correct, valid model names
        return [
            "gemini-2.5-flash",
            "gemini-2.5-pro"
        ]
    
    def _generate_avatar(self, name: str) -> str:
        """Generate an avatar URL using DiceBear API."""
        seed = str(uuid.uuid5(uuid.NAMESPACE_DNS, name))
        return f"https://api.dicebear.com/7.x/personas/svg?seed={seed}"

    # --- Functions that no longer do anything ---
    def _save_personas(self):
        # This function is now handled by update_persona, remove_persona, etc.
        # It's called by app.py, so we leave it empty to prevent a crash.
        pass