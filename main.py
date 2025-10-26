import os
from typing import List
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from modal import Image, App, Secret, asgi_app, mount
from multion.client import MultiOn

import templates
from db import get_notion_crm_api_key, get_notion_database_id, store_notion_crm_api_key, store_notion_database_id, \
    clean_all_transcripts_except, append_segment_to_transcript, remove_transcript
from llm import news_checker, analyze_live_conversation, retrieve_books_to_buy, segments_as_string
from models import Memory, LiveUpdate, ConversationState, Structured
from notion_utils import store_memoy_in_db

app = FastAPI()

modal_app = App(
    name='plugins_examples',
    secrets=[Secret.from_dotenv('.env')],
    mounts=[
        mount.Mount.from_local_dir('templates/', remote_path='templates/'),
    ]
)

multion = MultiOn(api_key=os.getenv('MULTION_API_KEY', '123'))


@modal_app.function(
    image=Image.debian_slim().pip_install_from_requirements('requirements.txt'),
    keep_warm=1,  # need 7 for 1rps
    memory=(1024, 2048),
    cpu=4,
    allow_concurrent_inputs=10,
)
@asgi_app()
def plugins_app():
    return app


def call_multion(books: List[str]):
    print('Buying books with MultiOn')
    response = multion.browse(
        cmd=f"Add to my cart the following books (in paperback version, or any physical version): {books}",
        url="https://amazon.com",
        local=True,
    )
    return response.message


# **************************************************
# ************ On Memory Created Plugin ************
# **************************************************

# noinspection PyRedeclaration
templates = Jinja2Templates(directory="templates")


@app.get('/setup-notion-crm', response_class=HTMLResponse)
async def setup_notion_crm(request: Request, uid: str):
    if not uid:
        raise HTTPException(status_code=400, detail='UID is required')
    return templates.TemplateResponse("setup_notion_crm.html", {"request": request, "uid": uid})


@app.post('/creds/notion-crm', response_class=HTMLResponse)
def creds_notion_crm(request: Request, uid: str = Form(...), api_key: str = Form(...), database_id: str = Form(...)):
    if not api_key or not database_id:
        raise HTTPException(status_code=400, detail='API Key and Database ID are required')
    print({'uid': uid, 'api_key': api_key, 'database_id': database_id})
    store_notion_crm_api_key(uid, api_key)
    store_notion_database_id(uid, database_id)
    return templates.TemplateResponse("okpage.html", {"request": request, "uid": uid})


@app.get('/setup/notion-crm')
def is_setup_completed(uid: str):
    notion_api_key = get_notion_crm_api_key(uid)
    notion_database_id = get_notion_database_id(uid)
    return {'is_setup_completed': notion_api_key is not None and notion_database_id is not None}


@app.post('/notion-crm')
def notion_crm(memory: Memory, uid: str):
    print(memory.dict())
    notion_api_key = get_notion_crm_api_key(uid)
    if not notion_api_key:
        return {'message': 'Your Notion CRM plugin is not setup properly. Check your plugin settings.'}

    store_memoy_in_db(notion_api_key, get_notion_database_id(uid), memory)
    return {}


# *******************************************************
# ************ On Transcript Received Plugin ************
# *******************************************************


@app.post('/news-checker')
def news_checker_endpoint(uid: str, data: dict):
    session_id = data['session_id']  # use session id in case your plugin needs the whole conversation context
    new_segments = data['segments']
    clean_all_transcripts_except(uid, session_id)

    transcript: list[dict] = append_segment_to_transcript(uid, session_id, new_segments)
    message = news_checker(transcript, is_live=True)

    if message:
        # so that in the next call with already triggered stuff, it doesn't trigger again
        remove_transcript(uid, session_id)

    return {'message': message}


# *******************************************************
# ************ Live Conversation Processing ************
# *******************************************************

@app.post('/live-updates')
def live_updates_endpoint(uid: str, data: dict):
    """
    Main endpoint for live conversation processing.
    Receives new segments and returns updates for Omi users.
    """
    session_id = data['session_id']
    new_segments = data['segments']
    
    # Clean old transcripts except current session
    clean_all_transcripts_except(uid, session_id)
    
    # Append new segments
    transcript: list[dict] = append_segment_to_transcript(uid, session_id, new_segments)
    
    updates = []
    
    # 1. News checking (only if significant content)
    if len(transcript) > 5:  # Only check after some conversation
        news_message = news_checker(transcript, is_live=True)
        if news_message:
            updates.append({
                'type': 'news_check',
                'content': news_message,
                'priority': 'high',
                'timestamp': transcript[-1]['end'] if transcript else 0
            })
    
    # 2. Live conversation analysis
    if len(transcript) > 3:  # Analyze after some segments
        analysis = analyze_live_conversation(transcript)
        if analysis['insights']:
            updates.append({
                'type': 'insight',
                'content': analysis['insights'][0],
                'priority': 'normal',
                'timestamp': analysis['timestamp']
            })
    
    # 3. Book recommendations (check periodically)
    if len(transcript) > 10 and len(transcript) % 10 == 0:  # Check every 10 segments
        # Create a temporary memory object for book analysis
        temp_memory = Memory(
            createdAt=datetime.now(),
            transcript=segments_as_string(transcript),
            transcriptSegments=[],  # Will be populated if needed
            structured=Structured(title="Live Conversation", overview="", emoji="", category="live"),
            discarded=False,
            is_live=True,
            session_id=session_id
        )
        
        books = retrieve_books_to_buy(temp_memory, is_live=True)
        if books:
            updates.append({
                'type': 'book_recommendation',
                'content': f"Books mentioned: {', '.join(books)}",
                'priority': 'normal',
                'timestamp': transcript[-1]['end'] if transcript else 0
            })
    
    return {
        'updates': updates,
        'session_id': session_id,
        'total_segments': len(transcript)
    }


@app.get('/conversation-state/{uid}/{session_id}')
def get_conversation_state(uid: str, session_id: str):
    """Get the current state of a live conversation"""
    # This would typically fetch from your database
    # For now, return basic state info
    return {
        'session_id': session_id,
        'user_id': uid,
        'is_active': True,
        'last_update_sent': None,
        'total_segments': 0,
        'update_frequency': 5
    }


@app.post('/end-conversation/{uid}/{session_id}')
def end_conversation(uid: str, session_id: str):
    """End a live conversation session"""
    # Clean up the session data
    remove_transcript(uid, session_id)
    
    return {
        'message': 'Conversation ended',
        'session_id': session_id
    }


# https://e604-107-3-134-29.ngrok-free.app/news-checker
