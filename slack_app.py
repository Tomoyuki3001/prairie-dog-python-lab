import os
import logging
from dotenv import load_dotenv
from app import generate_audit_with_gemini, generate_interview_questions_with_gemini
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


@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)


@app.event("app_mention")
def handle_app_mention_events(body, say):
    user_text = body["event"]["text"].lower().strip()

    try:
        if "interview" in user_text:
            say(f"I'm generating interview questions...")
            response = generate_interview_questions_with_gemini(user_text)
            say(
                f"Here are the interview questions: {response}\n\n I'm done generating interview questions."
            )
        else:
            say(f"I'm analyzing your resume...")
            response = generate_audit_with_gemini(user_text)
            say(
                f"Here is the full audit: {response}\n\n I'm done analyzing your input."
            )

    except Exception as e:
        logger.error(f"Error analyzing input: {e}")
        say(
            f"I'm sorry, I encountered an error while analyzing your input. Please try again later."
        )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(port=port, host="0.0.0.0")
