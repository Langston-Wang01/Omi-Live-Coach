# baseten.py
import os
import string
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# --- PROMPT for Live, In-Conversation Nudges ---
LIVE_NUDGE_PROMPT ="""
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

# --- NEW: PROMPT for Final End-of-Conversation Summary ---
FINAL_SUMMARY_PROMPT = """
You are an expert communication coach analyzing a transcript of a live conversation 
(between any number of participants). Your goal is to help people have warmer, more 
respectful, and engaging conversations by providing post-conversation insights.

'Rizz' in this context means the blend of warmth, attentiveness, reciprocity, and 
conversational flow. It does not measure attractiveness, charisma, or intelligence — 
only how naturally and respectfully the exchange connects both speakers.

Analyze the transcript using these conversational signals:
- Reciprocity and turn-taking: balanced talk time, low interruption rate.
- Attentiveness: question rate, follow-ups referencing prior details.
- Warmth: sentiment trajectory, positive acknowledgments, appreciation phrases.
- Comfort and pacing: speaking rate stability, pause tolerance.

Compute normalized sub-scores for Warmth, Attentiveness, Reciprocity, and Comfort, then 
aggregate them into a 0 to 100 Conversation Rizz Score. Provide:
1. The total score and sub-scores.
2. A short, natural-language summary (1 to 2 sentences).
3. 2 to 3 concise, forward-looking tips to improve future communication.

All feedback must be:
- Personalized to the tone, flow, and content of the conversation.
- Actionable and forward-looking.
- Respectful, constructive, and human-sounding.

Your output should follow this format:
Conversation Rizz: [0 to 100]
Warmth: [score], Attentiveness: [score], Reciprocity: [score], Comfort: [score]
Summary: [1 to 2 sentences]
Tips: [2 to 3 short, forward-looking suggestions]
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


def _call_llm(prompt: str, transcript: str, max_tokens: int) -> str:
    """Helper function to call the Baseten API."""
    api_key = os.getenv("BASETEN_API_KEY")
    if not api_key:
        raise ValueError("BASETEN_API_KEY not found in environment variables.")

    client = OpenAI(api_key=api_key, base_url="https://inference.baseten.co/v1")
    
    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": transcript}
            ],
            max_tokens=max_tokens,
            temperature=0.7,
            stream=False
        )
        if response.choices:
            content = custom_strip(response.choices[0].message.content or "")
            if content:
                return content
        # If the response is empty, return a clear message
        return "The model returned an empty response."
        
    except Exception as e:
        print(f"An error occurred while calling the API: {e}")
        return "Could not generate feedback due to an API error."


def get_live_feedback_nudge(transcript_text: str) -> str:
    """Analyzes a transcript and returns a single, live nudge."""
    return _call_llm(LIVE_NUDGE_PROMPT, transcript_text, 150)


def get_final_summary(transcript_text: str) -> str:
    """Analyzes a full transcript and returns a final summary report."""
    return _call_llm(FINAL_SUMMARY_PROMPT, transcript_text, 300)