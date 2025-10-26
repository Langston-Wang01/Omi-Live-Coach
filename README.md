# Omi Live Conversation Processing System

A real-time conversation analysis system designed to work with Omi's live transcription feature. This system provides intelligent insights, fact-checking, and recommendations during ongoing conversations, sending updates to users every 5-10 seconds.

## 🚀 Features

- **Real-time Analysis**: Processes live conversation segments as they're transcribed
- **Fact-checking**: Automatically detects and debunks misinformation using news search
- **Book Recommendations**: Identifies and suggests books mentioned in conversations
- **Live Insights**: Provides key insights and action items from ongoing discussions
- **Scalable Architecture**: Built with FastAPI and Modal for serverless deployment
- **Redis Caching**: Fast session state management for multiple concurrent conversations

## 🏗️ Architecture

```
Omi Transcription → Live Updates API → GPT Analysis → User Notifications
                                      ↓
                              Redis Session Storage
```

## 📋 Prerequisites

- Python 3.8+
- Redis database
- OpenAI API key
- AskNews API credentials
- Modal account (for deployment)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd omi-live-conversation
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file with:
   ```env
   OPENAI_API_KEY=your_openai_api_key
   MULTION_API_KEY=your_multion_api_key
   REDIS_DB_HOST=your_redis_host
   REDIS_DB_PORT=6379
   REDIS_DB_PASSWORD=your_redis_password
   ASKNEWS_CLIENT_ID=your_asknews_client_id
   ASKNEWS_CLIENT_SECRET=your_asknews_client_secret
   ```

4. **Start Redis server**
   ```bash
   redis-server
   ```

## 🚀 Quick Start

### Local Development

1. **Run the FastAPI server**
   ```bash
   uvicorn main:app --reload --port 8000
   ```

2. **Test the live updates endpoint**
   ```bash
   python live_conversation_example.py
   ```

### Production Deployment

1. **Deploy to Modal**
   ```bash
   modal deploy main.py
   ```

2. **Your API will be available at the Modal URL**

## 📡 API Endpoints

### Core Live Conversation Endpoints

#### `POST /live-updates`
Main endpoint for processing live conversation segments.

**Request:**
```json
{
  "uid": "user123",
  "data": {
    "session_id": "session456",
    "segments": [
      {
        "text": "Hello, how are you?",
        "speaker": "User",
        "speaker_id": 1,
        "is_user": true,
        "start": 0.0,
        "end": 2.5
      }
    ]
  }
}
```

**Response:**
```json
{
  "updates": [
    {
      "type": "insight",
      "content": "User is asking about well-being",
      "priority": "normal",
      "timestamp": 2.5
    }
  ],
  "session_id": "session456",
  "total_segments": 1
}
```

#### `GET /conversation-state/{uid}/{session_id}`
Get current conversation state.

#### `POST /end-conversation/{uid}/{session_id}`
End a live conversation session.

### Legacy Endpoints (Preserved)

- `POST /news-checker` - Fact-checking for completed conversations
- `POST /notion-crm` - Store conversation memories in Notion
- `GET /setup-notion-crm` - Notion CRM setup
- `POST /creds/notion-crm` - Store Notion credentials

## 🔄 Integration with Omi

### Integration Flow

1. **Omi starts transcription** → Calls `/live-updates` with initial segments
2. **Every 5-10 seconds** → Omi sends new segments to `/live-updates`
3. **System processes segments** → Returns relevant updates
4. **Omi displays updates** → Shows insights, news checks, book recommendations
5. **Conversation ends** → Call `/end-conversation` to clean up

### Update Types

The system generates different types of updates:

- **`insight`**: Key insights from conversation analysis
- **`news_check`**: Fact-checking alerts for misinformation
- **`book_recommendation`**: Books mentioned in conversation
- **`action_item`**: Tasks or follow-ups identified

### Priority Levels

- **`urgent`**: Critical misinformation detected
- **`high`**: Important news checks or insights
- **`normal`**: Regular conversation insights
- **`low`**: Background information

## ⚡ Performance Optimizations

### For Live Conversations

- **Segment Processing**: Only processes recent segments (last 10-15)
- **Reduced API Calls**: Limits news search results for live processing
- **Efficient Caching**: Uses Redis for fast session state management
- **Batch Processing**: Groups updates to reduce API overhead

### Update Frequency

- **News Checking**: Every 5+ segments (when significant content detected)
- **Insights**: Every 3+ segments (continuous analysis)
- **Book Recommendations**: Every 10 segments (periodic check)

## 🧪 Testing

### Run the example simulation
```bash
python live_conversation_example.py
```

### Test individual endpoints
```bash
# Test conversation state
curl "http://localhost:8000/conversation-state/user123/session456"

# Test live updates
curl -X POST "http://localhost:8000/live-updates" \
  -H "Content-Type: application/json" \
  -d '{"uid": "user123", "data": {"session_id": "session456", "segments": []}}'
```

## 📊 Monitoring

The system tracks:
- Conversation duration and segment count
- Update frequency and types
- Error rates and performance metrics
- User engagement with different update types

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for GPT models | Yes |
| `MULTION_API_KEY` | MultiOn API key for automation | Yes |
| `REDIS_DB_HOST` | Redis database host | Yes |
| `REDIS_DB_PORT` | Redis database port | No (default: 6379) |
| `REDIS_DB_PASSWORD` | Redis database password | Yes |
| `ASKNEWS_CLIENT_ID` | AskNews API client ID | Yes |
| `ASKNEWS_CLIENT_SECRET` | AskNews API client secret | Yes |

### Modal Configuration

The system is configured for Modal deployment with:
- **Memory**: 1-2GB RAM
- **CPU**: 4 cores
- **Concurrent Inputs**: 10
- **Keep Warm**: 1 instance

## 📁 Project Structure

```
├── main.py                    # FastAPI application and endpoints
├── llm.py                     # LLM functions for conversation analysis
├── models.py                  # Pydantic models for data validation
├── db.py                      # Database operations and Redis functions
├── notion_utils.py            # Notion CRM integration
├── requirements.txt           # Python dependencies
├── live_conversation_example.py # Example usage script
└── README.md                  # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the example script for usage patterns
- Review the API documentation above

## 🔄 Changelog

### v1.0.0 - Live Conversation Support
- Added real-time conversation processing
- Implemented live updates endpoint
- Enhanced LLM functions for live analysis
- Added conversation state management
- Optimized for 5-10 second update intervals

---

**Built with ❤️ for Omi users**
