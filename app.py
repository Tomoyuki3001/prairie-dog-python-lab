import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# 1. Setup your API Key
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

def generate_plan_with_gemini(user_input):
    # 2. Initialize the model (Gemini 1.5 Flash is fast and great for tasks)
    model = genai.GenerativeModel('gemini-1.5-flash')

    # 3. Create a System Prompt (Just like we did in TypeScript!)
    prompt = f"""
    You are an expert Task Architect.
    Break down the following goal into 3 clear subtasks.
    Goal: {user_input}
    Format your response as:
    Subtask 1: ...
    Subtask 2: ...
    Subtask 3: ...
    """

    response = model.generate_content(prompt)
    return response.text

# 4. Run the interaction
if __name__ == "__main__":
    goal = input("What do you want to achieve today? ")
    print("\nGemini is thinking...")

    plan = generate_plan_with_gemini(goal)

    print("\n--- YOUR PLAN ---")
    print(plan)