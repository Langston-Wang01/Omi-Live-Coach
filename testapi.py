import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from dotenv import load_dotenv

from baseten import get_communication_feedback

# --- Setup ---
load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- State and Cooldown Logic ---

# 1. NEW: Store the consent status for each user ('waiting' or 'given')
user_consent_status = {}

# 2. NEW: Define the trigger words for giving consent
CONSENT_TRIGGERS = {"i agree", "i consent", "let's begin", "start analysis"}

# 3. Store the last feedback time (only used after consent is given)
last_feedback_time = {}
FEEDBACK_COOLDOWN = timedelta(seconds=15)


# --- API Endpoints ---
@app.post('/livetranscript')
async def get_live_feedback(transcript: dict, uid: str):
    """
    Waits for consent, then analyzes a transcript and provides feedback,
    rate-limited to once every 15 seconds per user after consent is given.
    """
    # Determine the user's current consent status, defaulting to 'waiting'
    consent_status = user_consent_status.get(uid, 'waiting')

    # Assemble the transcript text once
    segments = transcript.get("segments", [])
    if not segments and consent_status == 'given': # Only an issue if we are analyzing
        return {"status": "no_text_in_transcript"}
    full_transcript = " ".join(segment.get("text", "") for segment in segments)
    
    # --- LOGIC BRANCH 1: Waiting for Consent ---
    if consent_status == 'waiting':
        # Check if any trigger word is in the transcript (case-insensitive)
        if any(trigger in full_transcript.lower() for trigger in CONSENT_TRIGGERS):
            print(f"Consent detected for {uid}.")
            # Update the user's state to 'given'
            user_consent_status[uid] = 'given'
            # Return the confirmation message and stop here for this request
            return {"message": "conversation analysis beginning"}
        else:
            # If no trigger word is found, just wait
            return {"status": "waiting_for_consent"}

    # --- LOGIC BRANCH 2: Consent Has Been Given ---
    elif consent_status == 'given':
        now = datetime.now()
        last_sent = last_feedback_time.get(uid)

        # Apply cooldown logic ONLY after consent has been given
        if not last_sent or (now - last_sent) > FEEDBACK_COOLDOWN:
            print(f"Cooldown over for {uid}. Getting feedback from LLM...")
            feedback = get_communication_feedback(full_transcript)
            
            # Update the cooldown timestamp
            last_feedback_time[uid] = now
            print(f"Feedback for {uid}: {feedback}")
            return {"message": feedback}
        else:
            # User is in the cooldown period
            print(f"Uid: {uid} is still in cooldown.")
            return {"status": "in_cooldown"}


if __name__ == "__main__":
    uvicorn.run("testapi:app", host="127.0.0.1", port=8000, reload=True)