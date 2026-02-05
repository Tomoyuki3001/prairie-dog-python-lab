import os
import json
import threading
import time
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from termcolor import colored
from colorama import just_fix_windows_console
from datetime import datetime

just_fix_windows_console()
load_dotenv()
client = genai.Client()


class LoadingSpinner:
    def __init__(self):
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._animate)

    def _animate(self):
        for char in ["-", "\\", "|", "/"]:
            if self.stop_event.is_set():
                break

            sys.stdout.write(f"\r{char}")
            sys.stdout.flush()
            time.sleep(0.1)
            if char == "\\":
                self._animate()

    def start(self):
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        self.thread.join()
        sys.stdout.write("\r")


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


def show_project_summary():
    if not os.path.exists("plans") or not os.listdir("plans"):
        print(colored("No plans found. Creating new plan...", "blue"))
        return

    files = sorted(
        os.listdir("plans"),
        key=lambda x: os.path.getmtime(os.path.join("plans", x)),
        reverse=True,
    )

    print(colored("\nPrevious Plans:", "blue", attrs=["bold"]))

    for i, filename in enumerate(files, 1):
        display_name = filename.replace("_", " ").replace(".txt", "").title()
        created_at = datetime.fromtimestamp(
            os.path.getmtime(os.path.join("plans", filename))
        ).strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"{i}. {colored(display_name, 'cyan', attrs=['bold'])}"
            + f" - {colored('Created at:', 'white', attrs=['bold'])} {colored(created_at, 'blue', attrs=['bold'])}"
        )

    choice = input(
        f"\nType a {colored('plan', 'cyan', attrs=['bold'])} to read a plan, or hit {colored('enter', 'green')} to go back: "
    ).strip()

    if choice.isdigit():
        index = int(choice) - 1
        if 0 <= index < len(files):
            filepath = os.path.join("plans", files[index])
            print(
                colored(f"\nReading plan: {files[index]}", "blue")
                + f". {colored(result['created_at'], 'blue', attrs=['bold'])}"
            )

            with open(filepath, "r", encoding="utf-8") as f:
                print(f.read())

            print(colored("\nPress Enter to go back", "yellow"))
        else:
            print(colored("Invalid number. Please try again.", "red"))


def output_plan(result):
    diff = result["difficulty"]
    color = "green" if diff == "Easy" else "yellow" if diff == "Medium" else "red"
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print(f"\n{colored(result['project_name'], 'cyan', attrs=['bold'])}")
        print(f"{colored(diff, color, attrs=['reverse', 'bold'])}\n")
        print(f"{colored('Execution Steps:', 'blue', attrs=['bold'])}")
        print(f"{colored(result['estimated_hours'], 'blue', attrs=['bold'])} hours")
        print(
            f"{colored('Created_at:', 'blue', attrs=['bold'])} {colored(now, 'blue', attrs=['bold'])}"
        )
        for index, step in enumerate(result["steps"], 1):
            print(f"{index}. {colored(step, 'white', attrs=['bold'])}")
        print("\n Happy building!")

        if not os.path.exists("plans"):
            os.makedirs("plans")
            print(f"Created folder: {colored('plans', 'blue')}")
        clean_name = result["project_name"].replace(" ", "_").lower()
        filename = f"plans/{clean_name}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"Project: {result['project_name']}\n")
            f.write(f"Difficulty: {result['difficulty']}\n")
            f.write(f"Created at: {result['created_at']}\n")
            f.write("\nSteps:\n")
            for step in result["steps"]:
                f.write(f"- {step}\n")
            f.write(f"\nEstimated hours: {result['estimated_hours']}\n")
        print(f"\n Plan saved to {colored(os.path.basename(filename), 'green')}")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.start(port=port, host="0.0.0.0")
    while True:
        user_input = input(
            f"\nWhat is your goal? (or type '{colored('quit', 'red')}' to exit): "
        ).strip()

        if user_input.lower() == "quit":
            print(colored("Goodbye!", "yellow"))
            break

        if user_input.lower() == "history":
            show_project_summary()
            continue

        if not user_input:
            print(colored("Please enter a valid goal.", "red"))
            continue

        try:
            spinner = LoadingSpinner()
            spinner.start()
            print("Architecting...")
            result = generate_plan_with_gemini(user_input)
            output_plan(result)
            spinner.stop()
        except Exception as e:
            spinner.stop()
            print(colored(f"An error occurred: {e}", "red"))
            print(colored("Please try again.", "red"))
            continue
