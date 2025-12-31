# 🇮🇳 NewsScope India - 360-Degree Feedback System

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6.svg)](https://www.typescriptlang.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)

**360-Degree Feedback Software for Government of India-Related News Stories in Regional Media using Artificial Intelligence and Machine Learning**

A production-ready, AI-powered multilingual news intelligence platform that collects, analyzes, and visualizes Indian government-related news from regional media sources in **10+ Indian languages** with real-time processing.

---

## 🌟 Key Features

### 🌐 Multilingual Support

- **10+ Indian Languages** - Hindi, Kannada, Tamil, Telugu, Bengali, Gujarati, Marathi, Punjabi, Malayalam, Odia, Urdu, English
- **Script Detection** - Auto-detect 9+ Indian scripts (Devanagari, Kannada, Tamil, Telugu, Bengali, Gujarati, Malayalam, Odia, Gurmukhi)
- **Language Detection** - Multi-method detection with confidence scoring (script-based + statistical)
- **Translation Ready** - Infrastructure for IndicTrans2 integration (English ↔ Indian languages)
- **50+ RSS Feeds** - Comprehensive coverage across all major regional newspapers

### 🤖 AI/ML Capabilities

- **Sentiment Analysis** - Multilingual XLM-RoBERTa (supports all Indian languages)
- **Topic Classification** - Zero-shot learning across 20+ categories (health, education, agriculture, policy, etc.)
- **Named Entity Recognition** - Dual NER (Transformer + spaCy + India-specific gazetteers):
  - 36 States/UTs
  - 40+ Ministries/Departments
  - 50+ Government Schemes
  - Cabinet Ministers & Officials
- **Real-time Processing** - Automatic enrichment of all incoming articles

### 📰 News Collection

**50+ Live RSS Feeds** - Comprehensive coverage:
- **English:** PIB, The Hindu, Indian Express, Times of India, Deccan Herald
- **Hindi:** PIB Hindi, Dainik Jagran, Amar Ujala, Navbharat Times, Live Hindustan, Patrika
- **Kannada:** Vijaya Karnataka, Prajavani, Kannada Prabha, Udayavani
- **Tamil:** Dinamalar, Dinamani, Daily Thanthi, The Hindu Tamil
- **Telugu:** Eenadu, Sakshi, Andhra Jyothy, Vaartha
- **Bengali:** Anandabazar Patrika, Ei Samay, Bartaman, Sangbad Pratidin
- **Gujarati:** Gujarat Samachar, Divya Bhaskar, Sandesh
- **Marathi:** Maharashtra Times, Loksatta, Sakal, Pudhari
- **Punjabi:** Jagbani, Ajit, Rozana Spokesman
- **Malayalam:** Malayala Manorama, Mathrubhumi, Madhyamam
- **Odia:** Samaja, Dharitri, Sambad
- **Urdu:** Inquilab, Sahafat

**Features:**
- Auto-refresh - Configurable intervals (default: 15 minutes)
- Deduplication - Content-based hashing
- Auto Language Detection - Every article is automatically analyzed for language and script

### 📊 Analytics & Visualization

- **Dashboard** - Real-time metrics and trends
- **Sentiment Trends** - Track positive/negative/neutral distribution
- **Geographic View** - State-wise news distribution
- **Category Analysis** - Topic-based filtering
- **Source Tracking** - Media outlet statistics

### 🔄 Real-time Features

- **Auto-refresh UI** - Frontend polls every 2 minutes
- **WebSocket Support** - Push notifications for new articles
- **Live Metrics** - System health and statistics

### 🗄️ Database Support

- **PostgreSQL** (default) - Full-text search, advanced indexing
- **MongoDB** (optional) - Document-based storage
- Easy toggle via environment variable

---

## 🏗️ Architecture

```
NewsScope_India/
├── frontend/              # React + TypeScript + Vite
│   ├── src/
│   │   ├── react-app/
│   │   │   ├── components/   # Reusable UI components
│   │   │   └── pages/        # Main application pages
│   │   └── shared/
│   │       └── types.ts      # TypeScript type definitions
│   ├── Dockerfile
│   ├── package.json
│   └── vite.config.ts
│
├── backend/               # FastAPI + Python AI/ML
│   ├── app/
│   │   ├── api.py          # REST API endpoints
│   │   ├── database.py     # PostgreSQL ORM
│   │   ├── nlp_model.py    # AI/ML models (Sentiment, Topic, NER)
│   │   ├── language_processor.py  # Translation & language detection
│   │   ├── news_collector.py     # RSS feed collection
│   │   └── feeds.yaml      # RSS feed configurations
│   ├── migrations/         # Database schema migrations
│   ├── Dockerfile
│   └── requirements.txt
│
└── docker-compose.yml     # Docker orchestration
```

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose (recommended) OR
- Node.js 20+ (for frontend)
- Python 3.11+ (for backend)
- PostgreSQL 15+ (for database)

### Option 1: Docker Compose (Recommended)

```powershell
# Clone the repository
git clone https://github.com/prajwalm-hub/360_FEEDBACK_SYSTEM_USING_AIML.git
cd 360_FEEDBACK_SYSTEM_USING_AIML

# Start all services (PostgreSQL + Backend + Frontend)
docker compose up --build -d

# View backend logs
docker compose logs -f backend

# Wait for models to download (first run: 3-5 minutes)

# Check health
curl http://localhost:8000/api/health

# Trigger initial news collection
curl -X POST http://localhost:8000/api/collect
```

**Access Points:**
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **PostgreSQL:** localhost:5432

---

### Option 2: Manual Setup

#### Backend Setup

```powershell
cd backend

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1  # On Linux/Mac: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up database (PostgreSQL)
# Create database: newsdb
# Run migrations
psql -U postgres -d newsdb -f migrations/1.sql
psql -U postgres -d newsdb -f migrations/8.sql

# Configure environment variables
cp .env.example .env
# Edit .env with your settings (including HUGGINGFACE_TOKEN)

# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

```powershell
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Access at http://localhost:5173
```

---

## 📡 API Endpoints

### Core
- `GET /api/health` - Health check
- `GET /api/metrics` - System statistics
- `GET /docs` - Interactive API documentation

### News
- `GET /api/news` - List/search articles
  - **Filters:** sentiment, region, category, source, language, script, q, date_from, date_to
  - **Example:** `GET /api/news?language=hi&limit=20` (Get Hindi articles)
- `GET /api/news/latest` - Recent articles
- `POST /api/collect` - Trigger collection

### Analytics
- `GET /api/analytics/sentiment` - Sentiment distribution
- `GET /api/analytics/category` - Topic counts
- `GET /api/analytics/region` - Geographic stats
- `GET /api/analytics/sources` - Source distribution
- `GET /api/analytics/languages` - Language distribution with script info
- `GET /api/analytics/scripts` - Script distribution (Devanagari, Tamil, etc.)

### Real-time
- `WS /api/ws/updates` - WebSocket live updates

---

## 📖 Usage

### News Feed
1. Navigate to **News Feed** page
2. Use filters to find specific news:
   - **Language:** Filter by 12 supported languages
   - **Category:** Health, Education, Policy, Governance, etc.
   - **Sentiment:** Positive, Neutral, Negative
   - **Region:** North, South, East, West, Central, Northeast India
3. Click article cards to read full stories
4. Toggle translations using the translation badge

### Language Insights
1. Go to **Language Insights** page
2. View:
   - Total languages and regional language count
   - Translation rate percentage
   - Average language detection confidence
   - Language distribution pie chart
   - Script distribution across 9 Indian scripts
   - Detailed language breakdown table

### Dashboard
1. Access **Dashboard** for real-time metrics:
   - Total articles collected
   - Sentiment distribution (positive/negative/neutral)
   - Top categories
   - Language distribution chart
   - Sentiment trends over time

### Advanced Filters
1. Navigate to **Advanced Filters** page
2. Apply complex filters:
   - Date range selection
   - Sentiment score range
   - Multiple tags/keywords
   - Source-specific filtering
3. Export results as CSV

---

## ⚙️ Configuration

### Environment Variables (`backend/.env`)

```env
# Database
DB_PROVIDER=postgres  # or "mongodb"
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/newsdb

# AI/ML
NLP_ENABLED=true
USE_GPU=false
HUGGINGFACE_TOKEN=your_token_here  # Required for IndicTrans2
SENTIMENT_MODEL=cardiffnlp/twitter-xlm-roberta-base-sentiment
ZERO_SHOT_MODEL=joeddav/xlm-roberta-large-xnli
NER_MODEL=xlm-roberta-large-finetuned-conll03-english

# Collection
COLLECT_INTERVAL_MIN=15
FEEDS_FILE=app/feeds.yaml

# API
CORS_ORIGINS=["http://localhost:5173"]
```

**Note:** Get your Hugging Face token from https://huggingface.co/settings/tokens

### RSS Feeds (`backend/app/feeds.yaml`)

Add new RSS feeds with language and script metadata:

```yaml
feeds:
  - name: "Your News Source"
    url: "https://example.com/rss"
    category: "Policy"
    region: "National"
    language: "hi"
    script: "Devanagari"
```

---

## 🎯 Supported Languages & Scripts

| Language | ISO Code | Script | Font Family |
|----------|----------|--------|-------------|
| Hindi | hi | Devanagari | Noto Sans Devanagari |
| Kannada | kn | Kannada | Noto Sans Kannada |
| Tamil | ta | Tamil | Noto Sans Tamil |
| Telugu | te | Telugu | Noto Sans Telugu |
| Bengali | bn | Bengali | Noto Sans Bengali |
| Gujarati | gu | Gujarati | Noto Sans Gujarati |
| Marathi | mr | Devanagari | Noto Sans Devanagari |
| Punjabi | pa | Gurmukhi | Noto Sans Gurmukhi |
| Malayalam | ml | Malayalam | Noto Sans Malayalam |
| Odia | or | Odia | Noto Sans Oriya |
| Urdu | ur | Arabic | Noto Nastaliq Urdu |
| English | en | Latin | Inter |

---

## 🔍 AI Models Used

| Task | Model | Size |
|------|-------|------|
| Sentiment | `twitter-xlm-roberta-base-sentiment` | ~550MB |
| Topics | `xlm-roberta-large-xnli` | ~900MB |
| NER | `xlm-roberta-large-finetuned-conll03` | ~900MB |
| spaCy NER | `en_core_web_sm` | ~40MB |

**Total:** ~2.4GB (cached after first download)

---

## 🐛 Troubleshooting

### Models not loading
```powershell
# Check cache
ls ~/.cache/huggingface/

# Force re-download
docker compose down -v
docker compose up --build
```

### Database errors
```powershell
# Check PostgreSQL
docker compose ps db

# Verify connection
psql postgresql://postgres:postgres@localhost:5432/newsdb
```

### Memory issues
- Reduce `BATCH_SIZE`
- Set `NLP_ENABLED=false`
- Use CPU instead of GPU

---

## 📊 Database Schema

```sql
CREATE TABLE articles (
    id VARCHAR PRIMARY KEY,
    url TEXT UNIQUE,
    hash VARCHAR(64) UNIQUE,
    title TEXT,
    summary TEXT,
    content TEXT,
    source VARCHAR(255),
    region VARCHAR(255),
    language VARCHAR(64),
    script VARCHAR(64),
    published_at TIMESTAMP,
    collected_at TIMESTAMP,
    sentiment_label VARCHAR(32),
    sentiment_score FLOAT,
    topic_labels TEXT[],
    entities JSONB
);
```

---

## 🧪 Testing

```powershell
# Backend
cd backend
pytest tests/

# Frontend
cd frontend
npm test
```

---

## 🛠️ Technology Stack

### Backend
- FastAPI 0.115
- Transformers 4.45 + spaCy 3.7 + PyTorch 2.3
- SQLAlchemy 2.0 + psycopg2 + pymongo
- Uvicorn with websockets

### Frontend
- React 18 + TypeScript 5
- TailwindCSS 3 + Lucide Icons
- Vite 5

### DevOps
- Docker + Docker Compose
- PostgreSQL 15 / MongoDB 7
- HuggingFace model cache

---

## 📈 Production Deployment

1. Use managed PostgreSQL (AWS RDS, Azure)
2. Set up reverse proxy (nginx/Caddy) with HTTPS
3. Change database credentials
4. Restrict CORS origins
5. Enable rate limiting
6. Add authentication for admin endpoints
7. Monitor with `/api/metrics`

---

## 📝 Future Enhancements

- [ ] JWT Authentication
- [ ] Redis caching
- [ ] Celery async tasks
- [ ] More regional feeds
- [ ] Fine-tuned Indian models
- [ ] Email/SMS alerts
- [ ] Export to CSV/PDF
- [ ] Elasticsearch integration

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📄 License

Research/Educational Project

---

## 🙏 Acknowledgments

- **IndicTrans2:** AI4Bharat translation models
- **MuRIL:** L3Cube Pune sentiment analysis for Indian languages
- **Hugging Face:** Transformers library and model hosting
- **PIB India:** Press Information Bureau RSS feeds
- **Google Noto Fonts:** Script-specific font families

---

## 📧 Support

For questions or support:
1. Check `/api/health`
2. Review `docker compose logs`
3. Verify database connection
4. Ensure models downloaded
5. Check RSS feed URLs
6. Open an issue on GitHub

See [SETUP.md](SETUP.md) for detailed setup documentation.

---

**Built with ❤️ for India's Digital Governance**
