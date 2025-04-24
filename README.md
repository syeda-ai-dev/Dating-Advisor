# Date Mate - AI Dating Advisor

Date Mate is an AI-powered dating advisor and matchmaking application built with FastAPI and Streamlit. It helps users navigate relationships, practice dating conversations, and find potential matches based on compatibility.

## Features

- 💬 AI Dating Advisor - Get expert advice on relationships and dating
- 🤖 Practice Chat - Simulate conversations with potential partners
- 👥 Profile Management - Create and manage your dating profile
- ❤️ Smart Matching - Find compatible matches based on multiple factors
- 🔒 Secure - JWT authentication and rate limiting
- 🚀 Fast - Async API with FastAPI

## Project Structure

```
date-mate/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app initialization
│   │   ├── config.py            # Pydantic settings configuration
│   │   ├── dependencies.py      # Shared dependencies
│   │   ├── models/
│   │   │   ├── schemas.py       # Pydantic request/response models
│   │   │   └── chat.py         # Chat-related models
│   │   ├── routers/
│   │   │   ├── chat_router.py   # Chat endpoints
│   │   │   ├── profile_router.py # Profile endpoints
│   │   │   └── matches_router.py # Matches endpoints
│   │   └── networks/
│   │       ├── exceptions.py    # Custom exceptions
│   │       ├── handlers.py      # Error handlers
├── frontend/
│   ├── app.py                   # Streamlit UI
│   └── utils/
│       ├── api_client.py        # API communication
│       └── helpers.py           # UI helpers
├── .env.example                 # Environment template
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/date-mate.git
   cd date-mate
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

4. Set up environment variables:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your configuration values.

5. Start the backend server:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

6. Start the frontend (in a new terminal):
   ```bash
   cd frontend
   streamlit run app.py
   ```

## API Documentation

Once the backend server is running, you can access:
- Interactive API docs: http://localhost:8000/docs
- Alternative API docs: http://localhost:8000/redoc

## Environment Variables

Required environment variables:
- `GROQ_API_KEY`: Your Groq API key
- `APP_ENV`: Application environment (development/production)
- `JWT_SECRET_KEY`: Secret key for JWT token generation
- `CORS_ORIGINS`: Allowed CORS origins

## Features in Detail

### AI Dating Advisor
- Get personalized dating advice
- Discuss relationship challenges
- Receive guidance on dating etiquette

### Practice Chat
- Simulate dating conversations
- Practice communication skills
- Get feedback on your approach

### Profile Management
- Create detailed dating profiles
- Update preferences and information
- Control privacy settings

### Smart Matching
- Advanced compatibility scoring
- Filter matches by preferences
- View detailed match profiles

## Security Features

- JWT Authentication
- Rate limiting (100 requests/hour)
- CORS protection
- Input validation
- Secure password handling
- Environment-based security

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a pull request

## License

MIT License - Feel free to use this project for learning purposes.

## Contact

For questions or support, please open an issue in the GitHub repository.