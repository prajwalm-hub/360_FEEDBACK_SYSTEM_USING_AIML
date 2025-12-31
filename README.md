# NewsScope India# 🇮🇳 NewsScope India - 360-Degree Feedback System



**Real-time Government of India News Monitoring System with AI/ML**[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com)

A comprehensive multilingual news aggregation and analysis platform that monitors 50+ Indian news sources across 12 languages, providing AI-powered sentiment analysis, topic categorization, and entity recognition for government-related news stories.[![React](https://img.shields.io/badge/React-19-61DAFB.svg)](https://reactjs.org/)

[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6.svg)](https://www.typescriptlang.org/)

---[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)



## 🌟 Features**360-Degree Feedback Software for Government of India-Related News Stories in Regional Media using Artificial Intelligence and Machine Learning**



### Multilingual Support (12 Languages)A production-ready, AI-powered multilingual news intelligence platform that collects, analyzes, and visualizes Indian government-related news from regional media sources in **10+ Indian languages** with real-time processing.

- **Indian Languages:** Hindi, Kannada, Tamil, Telugu, Bengali, Gujarati, Marathi, Punjabi, Malayalam, Odia, Urdu

- **English:** For pan-India coverage---

- **Real-time Translation:** IndicTrans2 model for 11 Indian languages → English

- **Script-Specific Fonts:** Native rendering for 9 Indian scripts (Devanagari, Tamil, Telugu, Kannada, Bengali, Gujarati, Malayalam, Odia, Gurmukhi, Arabic)## 🌟 Key Features



### AI/ML Capabilities### 🌐 **Multilingual Support (NEW!)**

- **Sentiment Analysis:** MuRIL model for Indian languages (88-92% accuracy), XLM-RoBERTa for English- **10+ Indian Languages** - Hindi, Kannada, Tamil, Telugu, Bengali, Gujarati, Marathi, Punjabi, Malayalam, Odia, Urdu, English

- **Topic Classification:** Zero-shot classification across 20+ categories (Health, Education, Policy, Governance, Economy, etc.)- **Script Detection** - Auto-detect 9+ Indian scripts (Devanagari, Kannada, Tamil, Telugu, Bengali, Gujarati, Malayalam, Odia, Gurmukhi)

- **Named Entity Recognition (NER):** Extract organizations, people, locations with regional variations- **Language Detection** - Multi-method detection with confidence scoring (script-based + statistical)

- **Language Detection:** Automatic script and language detection with confidence scores- **Translation Ready** - Infrastructure for IndicTrans2 integration (English ↔ Indian languages)

- **50+ RSS Feeds** - Comprehensive coverage across all major regional newspapers

### Real-time News Collection

- **50+ RSS Feeds:** Major Indian news sources including PIB, The Hindu, Times of India, regional media### 🤖 **AI/ML Capabilities**

- **Auto-refresh:** Configurable polling intervals (default: 15 minutes)- **Sentiment Analysis** - Multilingual XLM-RoBERTa (supports all Indian languages)

- **Deduplication:** Smart filtering to avoid duplicate articles- **Topic Classification** - Zero-shot learning across 20+ categories (health, education, agriculture, policy, etc.)

- **Named Entity Recognition** - Dual NER (Transformer + spaCy + India-specific gazetteers)

### Advanced Analytics  - 36 States/UTs

- **Language Distribution:** Pie charts showing article breakdown by language  - 40+ Ministries/Departments

- **Sentiment Trends:** Time-series sentiment analysis across categories  - 50+ Government Schemes

- **Geographic View:** State/region-wise news distribution  - Cabinet Ministers & Officials

- **Category Analytics:** Top topics and trending issues- **Real-time Processing** - Automatic enrichment of all incoming articles



### Interactive Dashboard### 📰 **News Collection**

- **Real-time Metrics:** Total articles, sentiment distribution, top categories- **50+ Live RSS Feeds** - Comprehensive coverage:

- **Multilingual UI:** Language selector with native names and flags  - **English:** PIB, The Hindu, Indian Express, Times of India, Deccan Herald

- **Translation Toggle:** Switch between original and translated text  - **Hindi:** PIB Hindi, Dainik Jagran, Amar Ujala, Navbharat Times, Live Hindustan, Patrika

- **Dark Mode:** Full dark mode support across all components  - **Kannada:** Vijaya Karnataka, Prajavani, Kannada Prabha, Udayavani

- **Responsive Design:** Mobile, tablet, and desktop optimized  - **Tamil:** Dinamalar, Dinamani, Daily Thanthi, The Hindu Tamil

  - **Telugu:** Eenadu, Sakshi, Andhra Jyothy, Vaartha

---  - **Bengali:** Anandabazar Patrika, Ei Samay, Bartaman, Sangbad Pratidin

  - **Gujarati:** Gujarat Samachar, Divya Bhaskar, Sandesh

## 🏗️ Architecture  - **Marathi:** Maharashtra Times, Loksatta, Sakal, Pudhari

  - **Punjabi:** Jagbani, Ajit, Rozana Spokesman

```  - **Malayalam:** Malayala Manorama, Mathrubhumi, Madhyamam

NewsScope_India_Fixed/  - **Odia:** Samaja, Dharitri, Sambad

├── frontend/              # React + TypeScript + Vite  - **Urdu:** Inquilab, Sahafat

│   ├── src/- **Auto-refresh** - Configurable intervals (default: 15 minutes)

│   │   ├── react-app/- **Deduplication** - Content-based hashing

│   │   │   ├── components/   # Reusable UI components- **Auto Language Detection** - Every article is automatically analyzed for language and script

│   │   │   └── pages/        # Main application pages

│   │   └── shared/### 📊 **Analytics & Visualization**

│   │       └── types.ts      # TypeScript type definitions- **Dashboard** - Real-time metrics and trends

│   ├── Dockerfile- **Sentiment Trends** - Track positive/negative/neutral distribution

│   ├── package.json- **Geographic View** - State-wise news distribution

│   └── vite.config.ts- **Category Analysis** - Topic-based filtering

│- **Source Tracking** - Media outlet statistics

├── backend/               # FastAPI + Python AI/ML

│   ├── app/### 🔄 **Real-time Features**

│   │   ├── api.py          # REST API endpoints- **Auto-refresh UI** - Frontend polls every 2 minutes

│   │   ├── database.py     # PostgreSQL ORM- **WebSocket Support** - Push notifications for new articles

│   │   ├── nlp_model.py    # AI/ML models (Sentiment, Topic, NER)- **Live Metrics** - System health and statistics

│   │   ├── language_processor.py  # Translation & language detection

│   │   ├── news_collector.py     # RSS feed collection### 🗄️ **Database Support**

│   │   └── feeds.yaml      # RSS feed configurations- **PostgreSQL** (default) - Full-text search, advanced indexing

│   ├── migrations/         # Database schema migrations- **MongoDB** (optional) - Document-based storage

│   ├── Dockerfile- Easy toggle via environment variable

│   └── requirements.txt

│---

├── docs/                  # Documentation

│   ├── MULTILINGUAL_SENTIMENT.md## 🚀 Quick Start with Docker

│   ├── MULTILINGUAL_UI_SETUP.md

│   └── QUICK_START_MULTILINGUAL.md**Prerequisites:**

│- Docker & Docker Compose installed

└── docker-compose.yml     # Docker orchestration- 4GB+ RAM available

```- 10GB+ disk space (for AI models)



---```powershell

# Navigate to project

## 🚀 Quick Startcd NewsScope_India_Fixed



### Prerequisites# Start all services (PostgreSQL + Backend + Frontend)

- **Docker & Docker Compose** (recommended) ORdocker compose up --build -d

- **Node.js 20+** (for frontend)

- **Python 3.11+** (for backend)# View backend logs

- **PostgreSQL 15+** (for database)docker compose logs -f backend



### Option 1: Docker Compose (Recommended)# Wait for models to download (first run: 3-5 minutes)



```bash# Check health

# Clone the repositorycurl http://localhost:8000/api/health

git clone <repository-url>

cd NewsScope_India_Fixed# Trigger initial news collection

curl -X POST http://localhost:8000/api/collect

# Start all services

docker-compose up --build# Open frontend in browser

# http://localhost:5173

# Access the application```

# Frontend: http://localhost:5173

# Backend API: http://localhost:8000**Access Points:**

# API Docs: http://localhost:8000/docs- **Frontend:** http://localhost:5173

```- **Backend API:** http://localhost:8000

- **API Docs:** http://localhost:8000/docs

### Option 2: Manual Setup- **PostgreSQL:** localhost:5432



#### Backend Setup---

```bash

cd backend## 📡 API Endpoints



# Create virtual environment### Core

python -m venv venv- `GET /api/health` - Health check

source venv/bin/activate  # On Windows: venv\Scripts\activate- `GET /api/metrics` - System statistics

- `GET /docs` - Interactive API documentation

# Install dependencies

pip install -r requirements.txt### News

- `GET /api/news` - List/search articles

# Set up database (PostgreSQL)  - **Filters:** sentiment, region, category, source, **language**, script, q, date_from, date_to

# Create database: newsdb  - **Example:** `GET /api/news?language=hi&limit=20` (Get Hindi articles)

# Run migrations- `GET /api/news/latest` - Recent articles

psql -U postgres -d newsdb -f migrations/1.sql- `POST /api/collect` - Trigger collection

psql -U postgres -d newsdb -f migrations/8.sql

### Analytics

# Configure environment variables- `GET /api/analytics/sentiment` - Sentiment distribution

cp .env.example .env- `GET /api/analytics/category` - Topic counts

# Edit .env with your settings- `GET /api/analytics/region` - Geographic stats

- `GET /api/analytics/sources` - Source distribution

# Start backend server- `GET /api/analytics/languages` - **NEW!** Language distribution with script info

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000- `GET /api/analytics/scripts` - **NEW!** Script distribution (Devanagari, Tamil, etc.)

```

### Real-time

#### Frontend Setup- `WS /api/ws/updates` - WebSocket live updates

```bash

cd frontend---



# Install dependencies## 🏗️ Architecture

npm install

```

# Start development serverNewsScope_India/

npm run dev├── backend/                    # Python FastAPI Backend

│   ├── app/

# Access at http://localhost:5173│   │   ├── config.py          # Settings

```│   │   ├── database.py        # PostgreSQL ORM

│   │   ├── mongodb.py         # MongoDB (optional)

---│   │   ├── nlp_model.py       # AI/ML pipelines (sentiment, topic, NER)

│   │   ├── language_processor.py  # **NEW!** Multilingual detection/translation

## 📖 Usage│   │   ├── news_collector.py  # RSS collection with auto language detection

│   │   ├── api.py             # REST + WebSocket endpoints

### News Feed│   │   ├── main.py            # App factory

1. Navigate to **News Feed** page│   │   ├── feeds.yaml         # **50+ RSS sources** (all languages)

2. Use filters to find specific news:│   │   ├── schemas.py         # Pydantic models

   - **Language:** Filter by 12 supported languages│   │   ├── utils.py           # Helpers

   - **Category:** Health, Education, Policy, Governance, etc.│   │   └── resources/

   - **Sentiment:** Positive, Neutral, Negative│   │       └── gazetteers.py  # India entities (States, Ministries, Schemes)

   - **Region:** North, South, East, West, Central, Northeast India│   ├── Dockerfile

3. Click article cards to read full stories│   └── requirements.txt       # **Updated with langdetect, indicnlp, fasttext**

4. Toggle translations using the translation badge│

├── src/react-app/             # React Frontend

### Language Insights│   ├── components/            # UI components

1. Go to **Language Insights** page│   ├── pages/                 # Pages (Dashboard, NewsFeed, etc.)

2. View:│   └── hooks/                 # Custom hooks (useApi)

   - Total languages and regional language count│

   - Translation rate percentage├── migrations/                # Database migrations

   - Average language detection confidence│   ├── 8.sql                  # **NEW!** Multilingual schema changes

   - Language distribution pie chart│   └── 8/down.sql             # Rollback script

   - Script distribution across 9 Indian scripts│

   - Detailed language breakdown table├── docker-compose.yml         # Orchestration (PostgreSQL + Backend + Frontend)

└── README.md                  # This file

### Dashboard```

1. Access **Dashboard** for real-time metrics:

   - Total articles collected---

   - Sentiment distribution (positive/negative/neutral)

   - Top categories## ⚙️ Configuration

   - Language distribution chart

   - Sentiment trends over time### Environment Variables (`backend/.env`)



### Advanced Filters```env

1. Navigate to **Advanced Filters** page# Database

2. Apply complex filters:DB_PROVIDER=postgres  # or "mongodb"

   - Date range selectionDATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/newsdb

   - Sentiment score range

   - Multiple tags/keywords# AI/ML

   - Source-specific filteringNLP_ENABLED=true

3. Export results as CSVUSE_GPU=false

SENTIMENT_MODEL=cardiffnlp/twitter-xlm-roberta-base-sentiment  # Multilingual

---ZERO_SHOT_MODEL=joeddav/xlm-roberta-large-xnli  # Supports 100+ languages

NER_MODEL=xlm-roberta-large-finetuned-conll03-english

## 🔧 Configuration

# Collection

### Backend Configuration (`backend/app/config.py`)COLLECT_INTERVAL_MIN=15

FEEDS_FILE=app/feeds.yaml  # Now includes 50+ regional feeds

```python

# NLP Settings# API

NLP_ENABLED = TrueCORS_ORIGINS=["http://localhost:5173"]

USE_GPU = False  # Set to True if CUDA available```

SENTIMENT_MODEL = "l3cube-pune/mbert-base-indian-sentiment"  # MuRIL

ZERO_SHOT_MODEL = "joeddav/xlm-roberta-large-xnli"### RSS Feeds (`backend/app/feeds.yaml`)

NER_MODEL = "xlm-roberta-large-finetuned-conll03-english"

**Now includes 50+ feeds across 12 languages:**

# Multilingual Settings

TRANSLATION_ENABLED = True```yaml

TRANSLATION_MODEL = "ai4bharat/indictrans2-indic-en-1B"feeds:

MURIL_SENTIMENT_ENABLED = True  # English

REGIONAL_ENTITY_NORMALIZATION = True  - name: Press Information Bureau (English)

    url: https://pib.gov.in/PressReleaseSite/Rss.aspx?Lang=1

# News Collection    region: India

COLLECT_INTERVAL_MIN = 15  # Polling interval in minutes    language: en

    script: Latin

# Database  

DB_PROVIDER = "postgres"  # or "mongodb"  # Hindi (हिन्दी)

DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/newsdb"  - name: Dainik Jagran

```    url: https://www.jagran.com/rss/news-national.xml

    region: India

### RSS Feeds (`backend/app/feeds.yaml`)    language: hi

    script: Devanagari

Add new RSS feeds with language and script metadata:  

  # Kannada (ಕನ್ನಡ)

```yaml  - name: Vijaya Karnataka

- name: "Your News Source"    url: https://www.vijaykarnataka.com/rss

  url: "https://example.com/rss"    region: Karnataka

  category: "Policy"    language: kn

  region: "National"    script: Kannada

  language: "hindi"  

  script: "Devanagari"  # Tamil (தமிழ்)

```  - name: Dinamalar

    url: https://www.dinamalar.com/rss/

---    region: Tamil Nadu

    language: ta

## 📊 API Endpoints    script: Tamil

  

### News Articles  # ... and 40+ more regional feeds

- `GET /news` - Get all news articles with filters```

- `GET /news/{id}` - Get specific article by ID

- `POST /news/collect` - Trigger manual news collection## 🛠️ Local Development (Without Docker)



### Analytics### Backend

- `GET /analytics/languages` - Language distribution statistics

- `GET /analytics/scripts` - Script distribution statistics```powershell

- `GET /metrics` - Dashboard metrics (sentiment, categories, trends)# Python 3.11+ required

python -m venv .venv

### Alerts.\.venv\Scripts\Activate.ps1

- `GET /alerts` - Get sentiment/keyword alerts

- `POST /alerts` - Create new alertcd backend

- `DELETE /alerts/{id}` - Delete alertpip install -r requirements.txt

python -m spacy download en_core_web_sm

**Full API Documentation:** http://localhost:8000/docs

$env:DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/newsdb"

---$env:NLP_ENABLED="true"



## 🧪 Testingcd ..

uvicorn app.main:app --reload --app-dir backend --host 0.0.0.0 --port 8000

### Backend Tests```

```bash

cd backend### Frontend

pytest tests/ -v

``````powershell

# Node 20+ required

### Frontend Testsnpm install

```bashnpm run dev

cd frontend```

npm run test

```---



---## 🔍 AI Models Used



## 🎯 Supported Languages & Scripts| Task | Model | Size |

|------|-------|------|

| Language | ISO Code | Script | Font Family || Sentiment | `twitter-xlm-roberta-base-sentiment` | ~550MB |

|----------|----------|--------|-------------|| Topics | `xlm-roberta-large-xnli` | ~900MB |

| Hindi | hi | Devanagari | Noto Sans Devanagari || NER | `xlm-roberta-large-finetuned-conll03` | ~900MB |

| Kannada | kn | Kannada | Noto Sans Kannada || spaCy NER | `en_core_web_sm` | ~40MB |

| Tamil | ta | Tamil | Noto Sans Tamil |

| Telugu | te | Telugu | Noto Sans Telugu |**Total:** ~2.4GB (cached after first download)

| Bengali | bn | Bengali | Noto Sans Bengali |

| Gujarati | gu | Gujarati | Noto Sans Gujarati |---

| Marathi | mr | Devanagari | Noto Sans Devanagari |

| Punjabi | pa | Gurmukhi | Noto Sans Gurmukhi |## 🐛 Troubleshooting

| Malayalam | ml | Malayalam | Noto Sans Malayalam |

| Odia | or | Odia | Noto Sans Oriya |### Models not loading

| Urdu | ur | Arabic | Noto Nastaliq Urdu |```powershell

| English | en | Latin | Inter |# Check cache

ls ~/.cache/huggingface/

---

# Force re-download

## 🤝 Contributingdocker compose down -v

docker compose up --build

1. Fork the repository```

2. Create feature branch (`git checkout -b feature/AmazingFeature`)

3. Commit changes (`git commit -m 'Add AmazingFeature'`)### Database errors

4. Push to branch (`git push origin feature/AmazingFeature`)```powershell

5. Open Pull Request# Check PostgreSQL

docker compose ps db

---

# Verify connection

## 📝 Licensepsql postgresql://postgres:postgres@localhost:5432/newsdb

```

This project is licensed under the MIT License - see the LICENSE file for details.

### Memory issues

---- Reduce `BATCH_SIZE`

- Set `NLP_ENABLED=false`

## 🙏 Acknowledgments- Use CPU instead of GPU



- **IndicTrans2:** AI4Bharat translation models---

- **MuRIL:** L3Cube Pune sentiment analysis for Indian languages

- **Hugging Face:** Transformers library and model hosting## 📊 Database Schema

- **PIB India:** Press Information Bureau RSS feeds

- **Google Noto Fonts:** Script-specific font families```sql

CREATE TABLE articles (

---    id VARCHAR PRIMARY KEY,

    url TEXT UNIQUE,

## 📧 Contact    hash VARCHAR(64) UNIQUE,

    title TEXT,

For questions or support, please open an issue on GitHub.    summary TEXT,

    content TEXT,

---    source VARCHAR(255),

    region VARCHAR(255),

**Built with ❤️ for monitoring Government of India news across all Indian languages**    language VARCHAR(64),

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

## 📄 License

Research/Educational Project

---

## 🤝 Support

1. Check `/api/health`
2. Review `docker compose logs`
3. Verify database connection
4. Ensure models downloaded
5. Check RSS feed URLs

See `backend/README.md` for detailed documentation.

---

**Built with ❤️ for India's Digital Governance**
