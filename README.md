# Call Analysis System
## AI-Powered Call Center Analytics for Mercedes-Benz Dealership

This application analyzes customer service calls in real-time using Google's Gemini AI to provide insights about agent performance and customer behavior.

## Features

- Real-time call analysis and scoring
- Agent performance metrics tracking
- Customer interest level assessment
- Test drive readiness scoring
- Customer preference analysis
- Comprehensive database storage

## Prerequisites

- Python 3.8 or higher
- Google Cloud account with Gemini API access
- Git

## Setup Instructions

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create and activate a virtual environment:
```bash
# On macOS/Linux
python -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory with the following content:
```
DATABASE_URL=sqlite:///./call_analysis.db
GOOGLE_API_KEY=your_google_api_key
```

5. Initialize the database:
```bash
# Create the database tables
alembic upgrade head
```

6. Run the application:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The application will be available at http://localhost:8000

## API Documentation

Once the application is running, you can access:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
├── app/
│   ├── main.py
│   ├── models/
│   ├── schemas/
│   ├── services/
│   └── utils/
├── alembic/
├── tests/
├── .env
├── requirements.txt
└── README.md
```

## Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=app tests/
```

## Development

1. Make sure you're in the virtual environment
2. Install development dependencies:
```bash
pip install -r requirements.txt
```

3. Run the development server with hot reload:
```bash
uvicorn app.main:app --reload
```

## Troubleshooting

1. If you encounter database issues:
   - Delete the existing database file (if using SQLite)
   - Run `alembic upgrade head` again

2. If you get API key errors:
   - Verify your Google API key in the `.env` file
   - Ensure you have enabled the Gemini API in your Google Cloud Console

3. For port conflicts:
   - Change the port in the uvicorn command:
   ```bash
   uvicorn app.main:app --reload --port 8001
   ```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 