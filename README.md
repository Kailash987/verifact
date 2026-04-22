# Fake News Detection Web Application

A production-ready web application for detecting fake news and misinformation using modern ML/NLP techniques.

## 🎯 Features

- **Text Classification**: Classify text as FAKE or REAL with confidence scores
- **Explainability**: Highlight important words contributing to predictions using LIME/SHAP
- **Modern Stack**: React.js frontend, FastAPI backend, BERT-based ML model
- **Database**: PostgreSQL for storing prediction history
- **Production Ready**: Clean architecture, proper error handling, logging, and testing

## 🏗️ Architecture

```
├── backend/          # FastAPI REST API
├── ml/              # ML model training and inference
├── frontend/        # React.js frontend
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL

### Setup

1. **Clone and setup environment**
🔹Backend setup (with virtual environment)

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

🔹 ML setup (recommended: separate virtual environment)

```bash
cd ../ml
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
🔹 Frontend setup

```bash
cd ../frontend
npm install
```

2. **Train the ML model**
```bash
cd ml
venv\Scripts\activate
python train.py
```

3. **Start PostgreSQL and run migrations**
```bash
# Start PostgreSQL service
cd backend
python -m app.database.init_db
```

4. **Run the services**
```bash
# Backend (Terminal 1)
cd backend
uvicorn app.main:app --reload --port 8000

# Frontend (Terminal 2)
cd frontend
npm start
```

5. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📡 API Usage

### Predict Endpoint
```bash
POST /predict
Content-Type: application/json

{
  "text": "Breaking: Scientists discover cure for all diseases!"
}
```

Response:
```json
{
  "label": "FAKE",
  "confidence": 0.92,
  "explanation": ["breaking", "scientists", "discover", "cure"]
}
```

## 🧠 ML Model

- **Base Model**: DistilBERT for sequence classification
- **Training**: Binary classification (FAKE vs REAL)
- **Explainability**: LIME for feature importance
- **Dataset**: ISOT Fake News Dataset

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# ML tests
cd ml
pytest

# Frontend tests
cd frontend
npm test
```

## 📈 Advanced Features

- Multilingual support (English + Hindi)
- Batch prediction endpoint
- Prediction history dashboard
- Confidence threshold warnings
- Rate limiting

## 📝 Project Structure

```
fake-news-detector/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── routes/
│   │   ├── services/
│   │   ├── models/
│   │   └── utils/
│   └── requirements.txt
├── ml/
│   ├── train.py
│   ├── inference.py
│   ├── preprocessing.py
│   ├── model/
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── components/
    │   ├── pages/
    │   └── services/
    └── package.json
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License
