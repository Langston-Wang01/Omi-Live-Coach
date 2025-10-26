import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Import both functions from the baseten module
from baseten import get_live_feedback_nudge, get_final_summary

# --- Setup ---
load_dotenv()
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# --- State and Cooldown Logic ---
# States can be 'waiting', 'given', or 'ended'
user_consent_status = {}
CONSENT_TRIGGERS = {"i agree", "i consent", "let's begin", "start analysis"}
END_TRIGGERS = {"goodbye", "talk to you later", "end conversation", "that's all"}
last_feedback_time = {}
FEEDBACK_COOLDOWN = timedelta(seconds=7.5)

# --- API Endpoints ---
@app.post('/livetranscript')
async def get_live_feedback(transcript: dict, uid: str):
    """
    Manages the conversation analysis lifecycle: waits for consent, gives live feedback,
    and provides a final summary upon detecting the end of the conversation.
    """
    consent_status = user_consent_status.get(uid, 'waiting')
    
    # --- LOGIC BRANCH 1: Conversation has already ended ---
    if consent_status == 'ended':
        #return {"message": "This conversation analysis has ended."}
        return
    # Assemble the transcript text
    segments = transcript.get("segments", [])
    full_transcript = " ".join(segment.get("text", "") for segment in segments)
    
    # --- LOGIC BRANCH 2: Waiting for Consent ---
    if consent_status == 'waiting':
        if any(trigger in full_transcript.lower() for trigger in CONSENT_TRIGGERS):
            print(f"Consent detected for {uid}.")
            user_consent_status[uid] = 'given'
            return {"message": "Consent confirmed. Conversation analysis beginning."}
        else:
            return {"status": "waiting_for_consent"}

    # --- LOGIC BRANCH 3: Consent Given, Conversation is Active ---
    elif consent_status == 'given':
        # First, check for end-of-conversation triggers
        if any(trigger in full_transcript.lower() for trigger in END_TRIGGERS):
            print(f"End of conversation detected for {uid}. Generating final summary.")
            summary = get_final_summary(full_transcript)
            user_consent_status[uid] = 'ended' # Set state to 'ended'
            if uid in last_feedback_time: del last_feedback_time[uid] # Clean up
            return {"message": "Conversation coach has ended. Read the summmary: " + summary}

        # If conversation is not ending, proceed with live feedback cooldown
        now = datetime.now()
        last_sent = last_feedback_time.get(uid)
        if not last_sent or (now - last_sent) > FEEDBACK_COOLDOWN:
            print(f"Cooldown over for {uid}. Getting live feedback from LLM...")
            feedback = get_live_feedback_nudge(full_transcript)
            last_feedback_time[uid] = now
            print(f"Feedback for {uid}: {feedback}")
            return {"message": feedback}
        else:
            print(f"Uid: {uid} is still in cooldown.")
            return {"status": "in_cooldown"}

if __name__ == "__main__":
    uvicorn.run("testapi:app", host="127.0.0.1", port=8000, reload=True)