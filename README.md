# Call Rating AI Assistant

This application analyzes customer service calls and provides insights about agent performance and customer behavior.

## Features

- Customer and agent call analysis
- Agent performance rating
- Customer interest level assessment
- Test drive readiness scoring
- Customer preference analysis
- Database storage for all interactions

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file with:
```
DATABASE_URL=postgresql://user:password@localhost/call_rating_db
OPENAI_API_KEY=your_openai_api_key
```

4. Initialize the database:
```bash
alembic upgrade head
```

5. Run the application:
```bash
uvicorn app.main:app --reload
```

## API Documentation

Once the application is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Running Tests

```bash
pytest
``` 