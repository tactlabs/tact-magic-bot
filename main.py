
    
    
from fastapi import FastAPI, Request, HTTPException
from slack_sdk import WebClient
from slack_sdk.signature import SignatureVerifier
import os
from dotenv import load_dotenv


load_dotenv()

app = FastAPI()
slack_client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
signature_verifier = SignatureVerifier(os.getenv("SLACK_SIGNING_SECRET"))


@app.get("/")
async def root():
    return {"message": "Tact Magic API is running!"}



@app.post("/slack/events")
async def slack_events(request: Request):
    body = await request.json()
    
    # Verify the request signature
    if not signature_verifier.is_valid_request(await request.body(), request.headers):
        raise HTTPException(status_code=401, detail="Invalid request signature")
    
    # Handle URL verification challenge
    if body.get("type") == "url_verification":
        return {"challenge": body.get("challenge")}
    
    # Handle event callbacks
    if body.get("type") == "event_callback":
        event = body.get("event", {})
        if event.get("type") == "message" and not event.get("bot_id"):  # Ignore bot messages
            user_id = event.get("user")
            channel_id = event.get("channel")
            text = event.get("text")
            
            # Log the received message
            print(f"Received content from user {user_id} in channel {channel_id}: {text}")
            
            # Respond to the message
            if text.lower() == "hello universe":
                slack_client.chat_postMessage(
                    channel=channel_id,
                    text="Hello world! How can I assist you today?"
                )
    
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)