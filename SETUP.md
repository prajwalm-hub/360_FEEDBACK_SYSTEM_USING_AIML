# NewsScope India - Setup Guide

## Overview
360-Degree Feedback Software for Government of India Related News Stories in Regional Media using AI/ML.

## Features
- Multi-language news collection (13 languages: English, Hindi, Kannada, Tamil, Telugu, Bengali, Malayalam, Marathi, Gujarati, Punjabi, Odia, Urdu, Assamese)
- AI-powered sentiment analysis
- Automatic translation
- Content classification
- Geographic view
- PIB alerts system
- RAG-based AI assistant

## Prerequisites
- Python 3.8+ (Anaconda recommended)
- Node.js 16+
- 4GB+ RAM

## Quick Start

### 1. Backend Setup
```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Run the backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will run at: http://localhost:8000

### 2. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Run the frontend
npm run dev
```

Frontend will run at: http://localhost:5173

### 3. Access the Application
Open your browser and go to: http://localhost:5173

## Configuration

### Backend (.env)
Create `backend/.env` file:
```
DB_PROVIDER=sqlite
DATABASE_URL=sqlite:///./newsdb.sqlite
LOG_LEVEL=info
COLLECT_INTERVAL_MIN=60

# Required for IndicTrans2 translation model
HUGGINGFACE_TOKEN=your_huggingface_token_here
```

**Note:** Get your Hugging Face token from https://huggingface.co/settings/tokens

### Frontend
Frontend automatically connects to backend at http://localhost:8000/api

## Project Structure
```
INDIA/
├── backend/          # FastAPI backend
│   ├── app/         # Main application
│   ├── collectors/  # News collection modules
│   └── migrations/  # Database migrations
├── frontend/        # React frontend
│   └── src/        # Source code
├── docker-compose.yml
└── README.md
```

## News Collection
News is automatically collected every 60 minutes from 97 RSS feeds covering:
- Government news sources
- Regional language media
- PIB press releases
- Google News (government-filtered)

## Technologies Used
- **Backend**: FastAPI, SQLAlchemy, Transformers (Hugging Face)
- **Frontend**: React, TypeScript, Vite, TailwindCSS
- **AI/ML**: MuRIL (sentiment), IndicTrans2 (translation)
- **Database**: SQLite (default), PostgreSQL (optional)

## Troubleshooting

### Backend not starting?
- Check if port 8000 is available
- Verify all dependencies are installed: `pip list`
- Check Python version: `python --version`

### Frontend not starting?
- Delete `node_modules` and run `npm install` again
- Check if port 5173 is available
- Verify Node.js version: `node --version`

### No data showing?
- Wait for first collection cycle (up to 60 minutes)
- Or manually trigger collection via API: http://localhost:8000/docs

## Support
For issues or questions, check the logs:
- Backend logs: Terminal where uvicorn is running
- Frontend logs: Browser console (F12)

## License
Proprietary - Government of India News Monitoring System
