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

@app.post("/slack/tm")
async def handle_tm_command(request: Request):
    # Verify the request signature
    form_data = await request.form()
    if not signature_verifier.is_valid_request(await request.body(), request.headers):
        raise HTTPException(status_code=401, detail="Invalid request signature")
    
    # Extract the command details
    command_text = form_data.get("text", "").strip()
    user_id = form_data.get("user_id")
    channel_id = form_data.get("channel_id")
    
    # Process the command
    if command_text == "test":
        response_text = "This is a test response!"
    else:
        response_text = f"Unknown command: {command_text}"
    
    # Send a response to Slack
    slack_client.chat_postMessage(channel=channel_id, text=response_text)
    return {"response_type": "in_channel", "text": response_text}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=800