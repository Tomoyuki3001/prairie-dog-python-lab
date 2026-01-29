import json
from dotenv import load_dotenv
from google import genai
from google.genai import types
from termcolor import colored
from colorama import just_fix_windows_console

just_fix_windows_console()

load_dotenv()
client = genai.Client()


def generate_plan_with_gemini(user_goal):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[f"Create a plan for: {user_goal}"],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            system_instruction=(
                "You are a Technical Architect. Always respond in JSON. "
                "Use this schema: {'project_name': str, 'steps': list[str], 'estimated_hours': int, 'difficulty': str}"
            ),
        ),
    )

    try:
        data = json.loads(response.text)
        return data
    except json.JSONDecodeError:
        return {"error": "AI returned messy data", "raw_text": response.tex}


if __name__ == "__main__":
    goal = input("What are we building today? ")
    print("Architecting...\n")

    result = generate_plan_with_gemini(goal)

    diff = result["difficulty"]
    color = "green" if diff == "Easy" else "yellow" if diff == "Medium" else "red"

    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print(f"\n{colored(result['project_name'], 'cyan', attrs=['bold'])}")
        print(f"{colored(diff, color, attrs=['reverse', 'bold'])}\n")
        print(f"{colored('Execution Steps:', 'blue', attrs=['bold'])}")
        print(f"{colored(result['estimated_hours'], 'blue', attrs=['bold'])} hours")
    for index, step in enumerate(result["steps"], 1):
        print(f"{index}. {colored(step, 'white', attrs=['bold'])}")
    print("\n Happy building!")

    clean_name = result["project_name"].replace(" ", "_").lower()
    filename = f"{clean_name}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"Project: {result['project_name']}\n")
        f.write(f"Difficulty: {result['difficulty']}\n")
        f.write("\nSteps:\n")
        for step in result["steps"]:
            f.write(f"- {step}\n")

    print(f"\n Plan saved to {colored(filename, 'green')}")
