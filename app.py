import json
from google import genai
from google.genai import types

client = genai.Client()


def generate_plan_with_gemini(user_goal):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[f"Create a plan for: {user_goal}"],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            system_instruction=(
                "You are a Technical Architect. Always respond in JSON. "
                "Use this schema: {'project_name': str, 'steps': list[str], 'estimated_hours': int, 'difficulty': str, 'created_at': str}"
            ),
        ),
    )

    try:
        data = json.loads(response.text)
        return data
    except json.JSONDecodeError:
        return {"error": "AI returned messy data", "raw_text": response.text}
