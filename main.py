



from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

app = FastAPI()

# Load environment variables
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
client = WebClient(token=SLACK_BOT_TOKEN)


class SlackCommand(BaseModel):
    text: str
    user_id: str
    channel_id: str


@app.get("/")
async def root():
    return {"message": "Tact Magic API is running!"}


@app.post("/slack/tm")
async def handle_tm_command(request: Request):
    form_data = await request.form()
    text = form_data.get("text")
    user_id = form_data.get("user_id")
    channel_id = form_data.get("channel_id")

    if not text:
        raise HTTPException(status_code=400, detail="No content provided.")

    # Process the content (e.g., log it or send it somewhere)
    print(f"Received content from user {user_id} in channel {channel_id}: {text}")

    # Optionally, send a response back to Slack
    try:
        response = client.chat_postMessage(
            channel=channel_id,
            text=f"Received your content: {text}"
        )
    except SlackApiError as e:
        raise HTTPException(status_code=500, detail=f"Slack API error: {e.response['error']}")

    return {"status": "success", "message": "Content processed."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)