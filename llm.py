from typing import List, Dict

from langchain_community.tools.asknews import AskNewsSearch
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI

from models import Memory

chat = ChatOpenAI(model='gpt-4o', temperature=0)


# chat = ChatGroq(
#     temperature=0,
#     model="llama-3.1-70b-versatile",
#     # model='llama3-groq-8b-8192-tool-use-preview',
# )

class BooksToBuy(BaseModel):
    books: List[str] = Field(description="The list of titles of the books to buy", default=[], min_items=0)


class NewsCheck(BaseModel):
    query: str = Field(description="The query to ask a news search engine, can be empty.", default='')


def retrieve_books_to_buy(memory: Memory, is_live: bool = True) -> List[str]:
    """
    Enhanced book retrieval for live conversations.
    Optimized to process recent segments for real-time updates.
    """
    chat_with_parser = chat.with_structured_output(BooksToBuy)
    
    # For live conversations, focus on recent segments
    if is_live and len(memory.transcriptSegments) > 20:
        recent_segments = memory.transcriptSegments[-20:]  # Last 20 segments
        recent_transcript = segments_as_string([{
            'text': segment.text,
            'start': segment.start,
            'end': segment.end,
            'is_user': segment.is_user,
            'speaker_id': segment.speaker_id
        } for segment in recent_segments])
    else:
        recent_transcript = memory.transcript
    
    response: BooksToBuy = chat_with_parser.invoke(f'''
    The following is the transcript of a {"live ongoing" if is_live else ""} conversation.
    {recent_transcript}
    
    Your task is to determine if the speakers talked about books or suggested/recommended books to each other \
    {"in the recent conversation" if is_live else "at some point during the conversation"}, and provide the titles of those.
    ''')
    print('Books to buy:', response.books)
    return response.books


def analyze_live_conversation(conversation: list[dict]) -> dict:
    """
    Real-time conversation analysis for live updates.
    Returns key insights and action items from recent conversation segments.
    """
    if not conversation:
        return {"insights": [], "action_items": [], "topics": []}
    
    # Process only recent segments for efficiency
    recent_segments = conversation[-15:] if len(conversation) > 15 else conversation
    conversation_str = segments_as_string(recent_segments)
    
    # Use a more efficient prompt for live analysis
    analysis_prompt = f'''
    Analyze this live conversation segment and provide:
    1. Key topics being discussed
    2. Any action items mentioned
    3. Important insights or decisions
    
    Keep responses concise for real-time updates.
    
    Conversation:
    {conversation_str}
    '''
    
    response = chat.invoke(analysis_prompt)
    
    # Parse the response into structured format
    return {
        "insights": [response.content[:200] + "..." if len(response.content) > 200 else response.content],
        "action_items": [],
        "topics": [],
        "timestamp": recent_segments[-1]['end'] if recent_segments else 0
    }


def get_timestamp_string(start: float, end: float) -> str:
    def format_duration(seconds: float) -> str:
        total_seconds = int(seconds)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        remaining_seconds = total_seconds % 60
        return f"{hours:02}:{minutes:02}:{remaining_seconds:02}"

    start_str = format_duration(start)
    end_str = format_duration(end)

    return f"{start_str} - {end_str}"


def segments_as_string(segments: List[Dict]) -> str:
    transcript = ''

    for segment in segments:
        segment_text = segment['text'].strip()
        timestamp_str = f"[{get_timestamp_string(segment['start'], segment['end'])}]"
        if segment.get('is_user', False):
            transcript += f"{timestamp_str} User: {segment_text} "
        else:
            transcript += f"{timestamp_str} Speaker {segment.get('speaker_id', '')}: {segment_text} "
        transcript += '\n\n'

    return transcript.strip()


def news_checker(conversation: list[dict], is_live: bool = True) -> str:
    """
    Enhanced news checker for live conversation processing.
    Optimized for real-time updates with reduced processing overhead.
    """
    chat_with_parser = chat.with_structured_output(NewsCheck)
    
    # For live conversations, only process recent segments (last 3-5 minutes)
    if is_live and len(conversation) > 10:
        # Get only the most recent segments for efficiency
        recent_segments = conversation[-10:]  # Last 10 segments
        conversation_str = segments_as_string(recent_segments)
    else:
        conversation_str = segments_as_string(conversation)
    
    print(f"Processing {len(conversation)} segments (live: {is_live})")
    
    result: NewsCheck = chat_with_parser.invoke(f'''
    You are analyzing a {"live ongoing" if is_live else ""} conversation for potential misinformation.
    
    Your task is to determine if the conversation discusses facts that appear conspiratorial, unscientific, or heavily biased.
    Only if the topic is of significant importance and urgency for the user to be aware of, provide a question to be asked to a news search engine.
    Otherwise, output an empty question.
    
    {"Note: This is a live conversation, so focus on recent developments and urgent matters." if is_live else ""}
    
    Transcript:
    {conversation_str}
    ''')
    
    print('News Query:', result.query)
    if len(result.query) < 5:
        return ''

    # For live conversations, limit search results to reduce processing time
    max_results = 1 if is_live else 2
    tool = AskNewsSearch(max_results=max_results)
    output = tool.invoke({"query": result.query})
    
    result = chat.invoke(f'''
    A user just asked a news search engine the following question:
    {result.query}
    
    The output was: {output}
    
    The conversation is:
    {conversation_str}
    
    Your task is to provide a {"10" if is_live else "15"} word summary to help debunk and contradict any obvious bias or conspiratorial content. 
    If you don't find anything concerning, just output an empty string.
    ''')
    
    print('Output', result.content)
    if len(result.content) < 5:
        return ''
    return result.content
