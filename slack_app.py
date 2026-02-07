import os
import re
import logging
from datetime import datetime
from dotenv import load_dotenv
from app import generate_plan_with_gemini
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from flask import Flask, request

load_dotenv()

slack_app_token = os.environ.get("SLACK_APP_TOKEN")
slack_bot_token = os.environ.get("SLACK_BOT_TOKEN")
slack_signing_secret = os.environ.get("SLACK_SIGNING_SECRET")

app = App(token=slack_bot_token, signing_secret=slack_signing_secret)

handler = SlackRequestHandler(app)

flask_app = Flask(__name__)


@flask_app.route("/slack/events", methods=["GET", "POST"])
def slack_events():
    return handler.handle(request)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("platform.log"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)


@app.event("app_mention")
def handle_app_mention_events(body, say):
    logger.info(body)
    user_text = body["event"]["text"]
    response = generate_plan_with_gemini(user_text)

    project_name = response.get("project_name", "Your Plan")
    difficulty = response.get("difficulty", "Normal")
    hours = response.get("estimated_hours", "??")

    message = f"*Project: {project_name}*\n"
    message += f"*Difficulty:* {difficulty} | *Est. Time:* {hours} hours\n\n"
    message += "*Action Plan:*\n"

    for i, step in enumerate(response.get("steps", []), 1):
        step_clean = re.sub(r"^\s*\d+[\.\)]\s*", "", str(step)).strip()
        message += f"{i}. {step_clean}\n"

    say(message)


def split_text(text, max_length=2900):
    if not text:
        return []

    return [text[i : i + max_length] for i in range(0, len(text), max_length)]


def format_timestamp(timestamp):
    if not timestamp:
        return "N/A"
    try:
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        logger.error(f"Error formatting timestamp: {e}")
        return "N/A"


@app.command("/architect")
def handle_command(ack, body, say):
    ack()
    user_goal = body.get("text")
    user_id = body.get("user_id")

    logger.info(f"Received command from user {user_id} with goal: {user_goal}")

    if not user_goal:
        say("Please provide a project goal.")
        return

    response = say(f"Architecting a plan for: *{user_goal}*")
    thread_ts = response["ts"]

    try:
        result = generate_plan_with_gemini(user_goal)

        if "error" in result:
            say(
                f"Sorry, the AI returned an error: {result.get('error', 'Unknown error')}"
            )
            return

        say(f"Generating plan...", thread_ts=thread_ts)

        full_plan_lines = [
            f"*{result.get('project_name', 'Plan')}*",
            f"Difficulty: {result.get('difficulty', 'N/A')} | Est. hours: {result.get('estimated_hours', 'N/A')}",
            f"Created: {format_timestamp(result.get('created_at', 'N/A'))}",
            "",
            "*Steps:*",
        ]

        for i, step in enumerate(result.get("steps", []), 1):
            step_clean = re.sub(r"^\s*\d+[\.\)]\s*", "", str(step)).strip()
            full_plan_lines.append(f"{i}. {step_clean}")
        full_plan_text = "\n".join(full_plan_lines)
        plan_chunks = split_text(full_plan_text)

        response_block = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"Here is the full plan: {result.get('project_name', 'Technical Transformation Plan')}",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Here is the goal: {user_goal}",
                },
            },
            {"type": "divider"},
        ]

        for chunk in plan_chunks:
            response_block.append(
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": chunk},
                },
            )

        say(
            blocks=response_block,
            text=f"Here is the full plan: {result.get('project_name', 'Technical Transformation Plan')}",
            thread_ts=thread_ts,
        )
    except Exception as e:
        logger.error(f"Error in architect command: {e}")
        say(
            f"Sorry, I encountered an error: {e}",
            thread_ts=thread_ts,
        )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(port=port, host="0.0.0.0")
