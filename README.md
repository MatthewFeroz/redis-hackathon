# Plumbly

AI-powered review assistant that walks customers through leaving a Google review after a plumbing service call.

## Problem

Small service businesses like plumbing companies rely on Google reviews for growth, but customers often don't leave reviews — not because they're unwilling, but because the process has too much friction. They forget, get confused by the steps, or give up halfway through.

## Solution

Plumbly is an AI chat agent that guides customers step-by-step through leaving a Google review. After a job is completed, the customer receives a link. They open it, and an AI agent — powered by Google Gemini — walks them through the entire review process conversationally, adapting to their device (iPhone/Android) and answering questions in real-time.

## Features

- **Conversational review guidance** — AI agent detects device type and provides tailored step-by-step instructions
- **Smart Q&A** — Handles common questions ("I don't have a Google account", "Where do I tap?")
- **Session persistence** — Redis-backed conversation state with automatic expiry
- **Customer pipeline tracking** — Track customers from contacted → in-progress → review completed
- **Unique customer links** — Each customer gets a personalized review session URL

## Tech Stack

| Layer | Technology |
|-------|-----------|
| AI Agent | Google Gemini 2.0 Flash via GenAI SDK |
| Backend | Python + FastAPI |
| Session State | Redis |
| Frontend | Web chat interface |
| Hosting | Google Cloud Run |
| Containerization | Docker |

## Architecture

```
Customer → Browser Chat UI → FastAPI Backend → Gemini GenAI SDK → Gemini 2.0 Flash
                                    ↕
                                  Redis
                            (sessions, history,
                             pipeline tracking)
```

## Setup

### Prerequisites

- Python 3.11+
- Redis instance (local or cloud)
- Google Cloud account with Gemini API access

### Local Development

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/plumbreview.git
cd plumbreview

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your API keys

# Run Redis (if local)
redis-server

# Start the app
uvicorn app.main:app --reload
```

### Deploy to Google Cloud Run

```bash
chmod +x deploy.sh
./deploy.sh
```

## Built For

- **Gemini Live Agent Challenge Hackathon** — #GeminiLiveAgentChallenge
- Demonstrates real-world application of Google Gemini multimodal AI with Google Cloud infrastructure

## License

MIT
