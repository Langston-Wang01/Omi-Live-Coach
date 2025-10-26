from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class Structured(BaseModel):
    title: str
    overview: str
    emoji: str = ''
    category: str = 'other'


class ActionItem(BaseModel):
    description: str


class Event(BaseModel):
    title: str
    startsAt: datetime
    duration: int
    description: Optional[str] = ''
    created: bool = False


class MemoryPhoto(BaseModel):
    base64: str
    description: str


class PluginResponse(BaseModel):
    pluginId: Optional[str] = None
    content: str


class TranscriptSegment(BaseModel):
    text: str
    speaker: str
    speaker_id: int
    is_user: bool
    start: float
    end: float


class LiveUpdate(BaseModel):
    """Model for live conversation updates sent to Omi users"""
    session_id: str
    user_id: str
    timestamp: float
    update_type: str  # 'insight', 'action_item', 'news_check', 'book_recommendation'
    content: str
    confidence: float = 0.0  # 0-1 confidence score
    priority: str = 'normal'  # 'low', 'normal', 'high', 'urgent'


class ConversationState(BaseModel):
    """Tracks the current state of a live conversation"""
    session_id: str
    user_id: str
    is_active: bool = True
    last_update_sent: Optional[datetime] = None
    total_segments: int = 0
    last_processed_segment: int = 0
    update_frequency: int = 5  # seconds between updates


class Memory(BaseModel):
    createdAt: datetime
    startedAt: Optional[datetime] = None
    finishedAt: Optional[datetime] = None
    transcript: str = ''
    transcriptSegments: List[TranscriptSegment] = []
    photos: Optional[List[MemoryPhoto]] = []
    recordingFilePath: Optional[str] = None
    recordingFileBase64: Optional[str] = None
    structured: Structured
    pluginsResponse: List[PluginResponse] = []
    discarded: bool
    is_live: bool = False  # Indicates if this is a live conversation
    session_id: Optional[str] = None  # For tracking live sessions
