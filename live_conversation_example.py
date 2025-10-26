#!/usr/bin/env python3
"""
Example script demonstrating how to use the live conversation processing system
with Omi for real-time transcription updates.
"""

import requests
import json
import time
from typing import List, Dict

# Configuration
API_BASE_URL = "http://localhost:8000"  # Adjust to your deployed URL
USER_ID = "user123"
SESSION_ID = "session456"

def send_live_update(segments: List[Dict]) -> Dict:
    """
    Send new transcription segments to the live updates endpoint.
    This would be called every 5-10 seconds by Omi.
    """
    url = f"{API_BASE_URL}/live-updates"
    
    payload = {
        "uid": USER_ID,
        "data": {
            "session_id": SESSION_ID,
            "segments": segments
        }
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error sending live update: {e}")
        return {"updates": [], "error": str(e)}

def simulate_live_conversation():
    """
    Simulate a live conversation with transcription segments.
    In real usage, these would come from Omi's transcription service.
    """
    
    # Simulate conversation segments over time
    conversation_segments = [
        # Initial segments
        {
            "text": "Hey, have you heard about that new conspiracy theory about the moon landing?",
            "speaker": "User",
            "speaker_id": 1,
            "is_user": True,
            "start": 0.0,
            "end": 3.5
        },
        {
            "text": "Oh really? What's that about?",
            "speaker": "Friend",
            "speaker_id": 2,
            "is_user": False,
            "start": 4.0,
            "end": 6.0
        },
        {
            "text": "They say it was all fake and filmed in a studio. I read this book about it called 'Moon Landing Hoax'.",
            "speaker": "User",
            "speaker_id": 1,
            "is_user": True,
            "start": 6.5,
            "end": 12.0
        },
        {
            "text": "That sounds interesting. I should check out that book.",
            "speaker": "Friend",
            "speaker_id": 2,
            "is_user": False,
            "start": 12.5,
            "end": 15.0
        },
        {
            "text": "Yeah, you should also read 'Conspiracy Theories Explained' by John Smith.",
            "speaker": "User",
            "speaker_id": 1,
            "is_user": True,
            "start": 15.5,
            "end": 19.0
        }
    ]
    
    print("🚀 Starting live conversation simulation...")
    print("=" * 50)
    
    # Process segments in batches (simulating real-time updates)
    batch_size = 2
    for i in range(0, len(conversation_segments), batch_size):
        batch = conversation_segments[i:i + batch_size]
        
        print(f"\n📝 Processing batch {i//batch_size + 1}:")
        for segment in batch:
            print(f"  [{segment['start']:.1f}s-{segment['end']:.1f}s] {segment['speaker']}: {segment['text']}")
        
        # Send to live updates endpoint
        result = send_live_update(batch)
        
        # Display any updates returned
        if result.get('updates'):
            print(f"\n🔔 Live Updates:")
            for update in result['updates']:
                print(f"  [{update['type'].upper()}] {update['content']}")
                print(f"  Priority: {update['priority']}, Timestamp: {update['timestamp']}")
        else:
            print("  No updates generated")
        
        print(f"  Total segments processed: {result.get('total_segments', 0)}")
        
        # Simulate delay between batches
        if i + batch_size < len(conversation_segments):
            print("  ⏳ Waiting for next batch...")
            time.sleep(2)  # Simulate 2-second delay
    
    print("\n✅ Conversation simulation complete!")

def test_individual_endpoints():
    """Test individual endpoints to ensure they work correctly."""
    
    print("🧪 Testing individual endpoints...")
    
    # Test conversation state endpoint
    try:
        response = requests.get(f"{API_BASE_URL}/conversation-state/{USER_ID}/{SESSION_ID}")
        print(f"✅ Conversation state: {response.json()}")
    except Exception as e:
        print(f"❌ Conversation state error: {e}")
    
    # Test news checker endpoint
    test_segments = [{
        "text": "The government is hiding the truth about aliens!",
        "speaker": "User",
        "speaker_id": 1,
        "is_user": True,
        "start": 0.0,
        "end": 3.0
    }]
    
    try:
        response = requests.post(f"{API_BASE_URL}/news-checker", json={
            "uid": USER_ID,
            "data": {
                "session_id": SESSION_ID,
                "segments": test_segments
            }
        })
        print(f"✅ News checker: {response.json()}")
    except Exception as e:
        print(f"❌ News checker error: {e}")

if __name__ == "__main__":
    print("🎯 Omi Live Conversation Processing System")
    print("=" * 50)
    
    # Test individual endpoints first
    test_individual_endpoints()
    
    print("\n" + "=" * 50)
    
    # Run the simulation
    simulate_live_conversation()
