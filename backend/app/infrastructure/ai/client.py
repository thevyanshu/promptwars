from google.cloud import aiplatform
from vertexai.generative_models import GenerativeModel, Part, SafetySetting, HarmCategory, HarmBlockThreshold, Tool, FunctionDeclaration
from app.config import settings
from app.infrastructure.ai.prompts.system import SYSTEM_PROMPT
from app.infrastructure.maps.client import maps_client
import json
from datetime import datetime

class PlannerAI:
    def __init__(self):
        try:
            aiplatform.init(project=settings.GOOGLE_CLOUD_PROJECT, location=settings.VERTEX_AI_LOCATION)
            
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
            
            # Define Google Maps Search tool
            search_places_func = FunctionDeclaration(
                name="search_places",
                description="Search for places, restaurants, and attractions in a specific location.",
                parameters={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query (e.g., 'best sushi in Tokyo')"
                        },
                        "location": {
                            "type": "string",
                            "description": "Optional lat,lng bias (e.g., '35.6762,139.6503')"
                        }
                    },
                    "required": ["query"]
                }
            )
            
            self.tools = [Tool(function_declarations=[search_places_func])]
            
            self._base_model = GenerativeModel(
                "gemini-1.5-pro", # Use stable 1.5 Pro
                safety_settings=self.safety_settings,
                tools=self.tools
            )
        except Exception as e:
            print(f"Warning: Vertex AI initialization failed. {e}")
            self._base_model = None

    def _get_model(self):
        if not self._base_model:
            return None
            
        current_date = datetime.now().strftime("%Y-%m-%d")
        full_system_prompt = SYSTEM_PROMPT.format(current_date=current_date)
        
        return GenerativeModel(
            "gemini-1.5-pro",
            system_instruction=full_system_prompt,
            safety_settings=self.safety_settings,
            tools=self.tools
        )

    def generate_plan(self, trip_details: dict) -> dict:
        model = self._get_model()
        if not model:
            return self._mock_generation(trip_details)
            
        chat = model.start_chat()
        prompt = f"Generate an itinerary for the following trip constraints:\n{json.dumps(trip_details, indent=2)}"
        
        try:
            response = chat.send_message(prompt)
            
            # Handle tool calls (simple loop for MVP)
            while response.candidates[0].content.parts[0].function_call:
                call = response.candidates[0].content.parts[0].function_call
                if call.name == "search_places":
                    result = maps_client.search_places(
                        call.args["query"], 
                        call.args.get("location")
                    )
                    response = chat.send_message(
                        Part.from_function_response(
                            name="search_places",
                            response={"content": result}
                        )
                    )
            
            # Final JSON response should be here
            return json.loads(response.text)
        except Exception as e:
            return {"status": "error", "message": f"AI Generation Failed: {str(e)}"}

    def stream_generate_plan(self, trip_details: dict):
        """
        Streaming with tool calls is complex; for MVP we'll do the research first 
        then stream the final result.
        """
        model = self._get_model()
        if not model:
            yield f"data: {json.dumps(self._mock_generation(trip_details))}\n\n"
            return
            
        chat = model.start_chat()
        prompt = f"Perform research and then generate a full itinerary JSON for:\n{json.dumps(trip_details, indent=2)}"
        
        try:
            response = chat.send_message(prompt)
            
            # Handle tool calls BEFORE streaming the final result
            while response.candidates[0].content.parts[0].function_call:
                call = response.candidates[0].content.parts[0].function_call
                if call.name == "search_places":
                    result = maps_client.search_places(
                        call.args["query"], 
                        call.args.get("location")
                    )
                    response = chat.send_message(
                        Part.from_function_response(
                            name="search_places",
                            response={"content": result}
                        )
                    )
            
            # Now stream the final content (which is now in the chat history)
            # We ask it to output the JSON now.
            final_stream = chat.send_message(
                "Great research. Now output the full final itinerary JSON as requested.",
                stream=True,
                generation_config={"response_mime_type": "application/json"}
            )
            
            for chunk in final_stream:
                if chunk.text:
                    safe_text = chunk.text.replace('\n', '\\n')
                    yield f"data: {safe_text}\n\n"
                    
        except Exception as e:
            error_data = json.dumps({"status": "error", "message": str(e)})
            yield f"data: {error_data}\n\n"
            
    def _mock_generation(self, trip_details: dict) -> dict:
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
                            "lat": 35.6762,
                            "lng": 139.6503,
                            "description": "Settle in and freshen up.",
                            "estimated_cost": "$0",
                            "booking_type": "hotel"
                        }
                    ]
                }
            ],
            "budget_summary": "Stayed well within the budget level.",
            "ai_notes": "This is a mocked response for local MVP testing."
        }

planner_ai = PlannerAI()
