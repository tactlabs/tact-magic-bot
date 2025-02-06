
from fastapi import FastAPI, Request, HTTPException

from slack_sdk import WebClient
from slack_sdk.signature import SignatureVerifier


from fastapi import FastAPI, HTTPException, Query, Header

from pydantic import BaseModel
from fastapi import FastAPI, Form
import requests
import os

import os
import httpx
from dotenv import load_dotenv


load_dotenv()

app = FastAPI()
slack_client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
signature_verifier = SignatureVerifier(os.getenv("SLACK_SIGNING_SECRET"))
vercel_api_url = os.getenv("VERCEL_API_URL")  # Add your Vercel API URL in .env




async def send_to_vercel(content: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(vercel_api_url, json={"content": content})
        response.raise_for_status()
        return response.json()


# class SlackCommand(BaseModel):
#     token: str
#     command: str
#     text: str
#     response_url: str
#     user_id: str
#     channel_id: str
    


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
    if command_text:
        try:
            # Send the content to Vercel API
            vercel_response = await send_to_vercel(command_text)
            response_text = f"Content sent to Vercel: {vercel_response}"
        except Exception as e:
            response_text = f"Failed to send content to Vercel: {str(e)}"
    else:
        response_text = "No content provided."
    
    # Send a response to Slack
    slack_client.chat_postMessage(channel=channel_id, text=response_text)
    return {"response_type": "in_channel", "text": response_text}



@app.post("/slack/tm")
async def handle_tm_command(
    text: str = Form(...),  # Get the command text
    user_id: str = Form(...),  # User who triggered the command
    response_url: str = Form(...),  # Response URL
):
    # Build the response text
    response_text = f"Hello <@{user_id}>, you said: {text}"

    # Send the response to Slack using the response_url
    payload = {
        "response_type": "in_channel",  # or "ephemeral"
        "text": response_text
    }

    # Send the response to Slack
    requests.post(response_url, json=payload)

    return {"status": "ok"}




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)