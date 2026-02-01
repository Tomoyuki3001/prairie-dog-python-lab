import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
from app import generate_plan_with_gemini

load_dotenv()

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))


def split_text(text, max_length=2900):
    if not text:
        return []

    return [text[i : i + max_length] for i in range(0, len(text), max_length)]


@app.command("/architect")
def handle_command(ack, body, say):
    ack()

    user_goal = body.get("text")
    user_id = body.get("user_id")

    if not user_goal:
        say("Please provide a project goal.")
        return

    say(f"Hello, @<{user_id}>! You asked me to architect: *{user_goal}*")

    try:
        result = generate_plan_with_gemini(user_goal)

        if "error" in result:
            say(
                f"Sorry, the AI returned an error: {result.get('error', 'Unknown error')}"
            )
            return

        full_plan_lines = [
            f"*{result.get('project_name', 'Plan')}*",
            f"Difficulty: {result.get('difficulty', 'N/A')} | Est. hours: {result.get('estimated_hours', 'N/A')}",
            f"Created: {result.get('created_at', 'N/A')}",
            "",
            "*Steps:*",
        ]

        for i, step in enumerate(result.get("steps", []), 1):
            full_plan_lines.append(f"{i}. {step}")
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
        )
    except Exception as e:
        say(f"Sorry, I encountered an error: {e}")


if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
