from app.infrastructure.ai.client import planner_ai

trip_details = {
    "title": "Test Trip",
    "start_date": "2024-06-01",
    "end_date": "2024-06-03",
    "preferences": {"budget": "moderate"},
    "constraints": {}
}

print("Running generation...")
result = planner_ai.generate_plan(trip_details)
print(result)
