# baseten.py
import os
import string
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# --- (The rest of your file is the same) ---

COMMUNICATION_COACH_PROMPT = """
You are an expert communication coach analyzing a transcript of a live conversation.
Maintain a lightweight “topics” memory to recall recurring themes, tone patterns, or 
communication habits across turns and use it to generate more personalized follow-ups.
Provide one concise, forward-looking sentence of feedback (no more than 10 words) that 
helps the speaker improve future communication. The feedback must be specific, actionable,
and personalized — offering a unique suggestion tailored to the conversation’s tone, flow, and context. 
If the speaker is communicating effectively, instead provide a short, positive sentence 
of encouragement (no more than 10 words). Consider “effective” communication to include natural, 
imperfect moments — only suggest improvement when patterns clearly hinder clarity, empathy, or flow. 
All sentences must end with a period. Avoid rephrasing identical advice. If the same issue 
persists, vary the feedback by highlighting new context, impact, or phrasing to keep it fresh and human. 
Anchor every suggestion in something directly observable from the transcript, such as word choice, tone, pacing, or response timing.
"""



def custom_strip(s: str, chars: str = None) -> str:
    # ... (this function remains unchanged)
    if chars is None:
        chars_to_remove = string.whitespace
    else:
        chars_to_remove = chars
    start_index = 0
    while start_index < len(s) and s[start_index] in chars_to_remove:
        start_index += 1
    end_index = len(s) - 1
    while end_index >= start_index and s[end_index] in chars_to_remove:
        end_index -= 1
    return s[start_index : end_index + 1]


def get_communication_feedback(transcript_text: str) -> str:
    """
    Analyzes a transcript and returns one sentence of communication feedback.
    """
    try:
        # Get the API key from the environment variable
        api_key = os.getenv("BASETEN_API_KEY")
        if not api_key:
            raise ValueError("BASETEN_API_KEY not found in environment variables.")

        client = OpenAI(
            api_key=api_key, 
            base_url="https://inference.baseten.co/v1"
        )

        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": COMMUNICATION_COACH_PROMPT},
                {"role": "user", "content": transcript_text}
            ],
            max_tokens=150,
            temperature=0.7,
            stream=False
        )
        
        if response.choices:
            return response.choices[0].message.content or ""#custom_strip(response.choices[0].message.content or "")
        return "No feedback was generated."

    except Exception as e:
        print(f"An error occurred: {e}")
        return "Error: Could not get feedback from the LLM."
