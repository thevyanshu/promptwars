from google.cloud import aiplatform
from vertexai.generative_models import GenerativeModel, Part, SafetySetting, HarmCategory, HarmBlockThreshold
from app.config import settings
from app.infrastructure.ai.prompts.system import SYSTEM_PROMPT
import json

class PlannerAI:
    def __init__(self):
        # Initialize Vertex AI. For MVP, we might mock this if project isn't fully configured
        try:
            aiplatform.init(project=settings.GOOGLE_CLOUD_PROJECT, location=settings.VERTEX_AI_LOCATION)
            
            # Strict safety settings
            self.safety_settings = [
                SafetySetting(
                    category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                    threshold=HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                ),
                SafetySetting(
                    category=HarmCategory.HARM_CATEGORY_HARASSMENT,
                    threshold=HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                ),
                SafetySetting(
                    category=HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                    threshold=HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                ),
                SafetySetting(
                    category=HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                    threshold=HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                ),
            ]
            
            self.model = GenerativeModel(
                "gemini-2.5-pro",
                system_instruction=SYSTEM_PROMPT,
                safety_settings=self.safety_settings
            )
        except Exception as e:
            print(f"Warning: Vertex AI initialization failed. {e}")
            self.model = None

    def generate_plan(self, trip_details: dict) -> dict:
        """
        Generates an itinerary using Gemini 2.5 Pro.
        Returns a JSON dictionary.
        """
        if not self.model:
            # Fallback mock for local development without GCP auth
            return self._mock_generation(trip_details)
            
        prompt = f"Generate an itinerary for the following trip constraints:\n{json.dumps(trip_details, indent=2)}"
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            return json.loads(response.text)
        except Exception as e:
            return {"status": "error", "message": f"AI Generation Failed: {str(e)}"}
            
    def _mock_generation(self, trip_details: dict) -> dict:
        """Mock response for local development when GCP credentials aren't available."""
        return {
            "itinerary": [
                {
                    "day": 1,
                    "date": trip_details.get("start_date", "2024-01-01"),
                    "theme": "Arrival and Exploration",
                    "activities": [
                        {
                            "time_start": "10:00",
                            "time_end": "12:00",
                            "activity_name": "Arrive and Check-in",
                            "location": "Mock Hotel",
                            "description": "Settle in and freshen up.",
                            "estimated_cost": "$0",
                            "booking_type": "hotel"
                        },
                        {
                            "time_start": "13:00",
                            "time_end": "15:00",
                            "activity_name": "Lunch at local spot",
                            "location": "Downtown Restaurant",
                            "description": "Enjoy local cuisine respecting your dietary constraints.",
                            "estimated_cost": "$20",
                            "booking_type": "dining"
                        }
                    ]
                }
            ],
            "budget_summary": "Stayed well within the budget level.",
            "ai_notes": "This is a mocked response for local MVP testing."
        }

planner_ai = PlannerAI()
