# Frontdesk AI Supervisor

A human-in-the-loop system for AI receptionists that allows escalation to human supervisors when the AI doesn't know the answer, followed by customer follow-up and automatic knowledge base updates.

## Features

- LiveKit integration for handling voice calls
- AI agent with basic salon knowledge
- Automated escalation to human supervisors
- Knowledge base that grows over time
- Supervisor UI for handling pending requests
- Request lifecycle management (pending → resolved/unresolved)
- Simulated call capability for testing

## Project Structure

```
frontdesk-ai-supervisor/
├── app/
│   ├── __init__.py           # Flask application factory
│   ├── agent.py              # AI agent and LiveKit integration
│   ├── db.py                 # Database models and operations
│   ├── knowledge_base.py     # Knowledge management
│   ├── routes.py             # API endpoints
│   └── templates/            # HTML templates
├── static/                   # Static assets (CSS, JS)
├── config.py                 # Configuration settings
├── requirements.txt          # Project dependencies
└── run.py                    # Application entry point
```

## Setup Instructions

### Prerequisites

- Python 3.7+
- LiveKit account (for voice capabilities)
- OpenAI API key (for the AI agent)

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/frontdesk-ai-supervisor.git
   cd frontdesk-ai-supervisor
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your configuration:
   ```bash
   cp .env.example .env
   ```

5. Edit the `.env` file with your API keys and configuration.

### Running the Application

1. Start the Flask development server:
   ```bash
   python run.py
   ```

2. Access the supervisor dashboard at `http://localhost:5000`

### Testing with Simulated Calls

1. Navigate to the Help Requests page
2. Click "Simulate Call" button
3. Enter a customer phone number and question
4. Click "Simulate" to test the AI agent

## API Endpoints

- `GET /api/help-requests` - Get all help requests
- `POST /api/help-requests/<id>/resolve` - Resolve a help request
- `POST /api/help-requests/<id>/unresolve` - Mark a request as unresolved
- `GET /api/knowledge` - Get all knowledge items
- `POST /api/knowledge` - Add a new knowledge item
- `POST /api/simulate-call` - Simulate an incoming call
- `POST /webhook/livekit` - LiveKit webhook endpoint

## Design Decisions

### Help Request Model

Help requests have a clear lifecycle:
- **Pending**: Awaiting supervisor response
- **Resolved**: Answered by supervisor, customer notified
- **Unresolved**: Marked as cannot be answered or timed out

Fields include:
- `customer_phone`: For follow-up communication
- `question`: The original question asked
- `status`: Current state in the lifecycle
- `created_at`: Timestamp for request creation
- `resolved_at`: Timestamp when resolved
- `answer`: Supervisor's response
- `call_session_id`: Reference to LiveKit session

### Knowledge Base Design

The knowledge base is designed to grow over time:
- Each item stores a question/answer pair
- Items are linked to originating help requests
- Simple but effective keyword matching for response
- Confidence scoring to determine when to escalate

### Scaling Considerations

The system is designed to scale from 10 to 1,000+ requests per day:
- Separate modules for agent, database, and knowledge management
- Database queries optimized with indexes
- Asynchronous processing for LiveKit integration
- Polling instead of WebSockets for simplicity in this MVP
- Could be extended with message queues for higher scale

### Error Handling

- Timeout mechanism for unresolved requests
- Error logging for all API operations
- Graceful degradation if LiveKit is unavailable

## Future Improvements

- **Live Call Transfer**: Implement Phase 2 to transfer calls live if supervisor is available
- **Better NLU**: Integrate more sophisticated natural language understanding
- **Authentication**: Add user authentication for supervisors
- **Metrics Dashboard**: Track resolution times and knowledge base growth
- **Automated Testing**: Add comprehensive test suite