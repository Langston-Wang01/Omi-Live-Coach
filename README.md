# Omi Rizz App
l
A real-time conversation analysis tool that listens to Omi's live transcription and provides Rizz scores, summaries, suggestions, and live feedback during and after conversations.

## Goal

Help users understand and improve their conversational presence by analyzing tone, pacing, and reciprocity, then offering insight into their overall "rizz."

## What "Rizz" Means

In this context, rizz refers to a blend of warmth, attentiveness, reciprocity, and chemistry signals — not attractiveness or personal value. The goal is to reflect how naturally engaging and connected the speaker sounds.

## Function

- Listens to live conversation transcriptions through Omi
- Provides real-time feedback and communication tips as the conversation unfolds
- Generates a final Rizz Score at the end of the transcription (like a full conversation review)
- Summarizes the key moments and offers personalized improvement suggestions
- Built with FastAPI and can be deployed to Modal

## How to Run

### Install dependencies
```bash
pip install -r requirements.txt
```

### Add environment variables
Create a `.env` file in the project folder:
```env
BASETEN_API_KEY=your_key
```

### Run the FastAPI server
```bash
uvicorn main:app --reload --port 8000
```

## Summary

The Rizz App analyzes full conversations captured through Omi's transcription, offering live feedback during the interaction and a final Rizz score, summary, and personalized suggestions once the conversation ends.
