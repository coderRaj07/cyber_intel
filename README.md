# 🛡 Cyber Metric Extractor

Automated Data Extraction Pipeline for
**“State of the Cyber Security Sector in Ireland 2022”**

---

## 📌 Overview

This project implements an automated document intelligence pipeline that:

* Parses the target PDF
* Extracts all quantitative metrics (tables, charts, textual values)
* Assigns source-of-truth metadata
* Normalizes data for longitudinal economic analysis
* Exposes structured outputs via REST APIs
* Supports async processing with Celery

The system is designed to handle:

* High-fidelity tables
* Vector-based charts
* Narrative numeric statements
* Hierarchical document structures

---

# 🧠 Architecture Overview

```
PDF Upload
    ↓
Recursive Document Parser
    ↓
Extraction Engine
   ├── Table Extractor
   ├── Textual Metric Extractor
   ├── Chart Stub Extractor
   └── LLM-Assisted Interpretation
    ↓
Normalizer
    ↓
Confidence Scoring Engine
    ↓
Database Storage
    ↓
API Export (JSON / CSV)
```

---

# 📂 Project Structure

```
app/
 ├── api/
 │    ├── upload.py          # Upload endpoint
 │    ├── metrics.py         # Fetch structured metrics
 │    ├── export.py          # Export CSV
 │
 ├── services/
 │    ├── pdf_parser.py
 │    ├── recursive_parser.py
 │    ├── extractor.py
 │    ├── tokenizer.py
 │    ├── normalizer.py
 │    ├── confidence.py
 │    ├── chart_stub.py
 │    ├── llm_client.py
 │
 ├── workers/
 │    ├── celery_app.py
 │    ├── tasks.py
 │
 ├── utils/
 │    ├── file_utils.py
 │    ├── logger.py
 │
 ├── database.py
 ├── models.py
 ├── schemas.py
 ├── main.py
```

---

# 🚀 Features

### ✅ Recursive Parsing

Preserves document hierarchy for contextual metric extraction.

### ✅ Multi-Strategy Extraction

* Structured table parsing
* Numeric token extraction from text
* Vector chart parsing (stub support)
* LLM-based semantic interpretation

### ✅ Source-of-Truth Metadata

Each metric includes:

* Page number
* Source text snippet
* Extraction method
* Confidence score

### ✅ Confidence Scoring

Scores are computed based on:

* Structural reliability
* Extraction method
* Pattern matching certainty
* LLM response consistency

### ✅ Async Support

Optional Celery-based background processing.

---

# 📊 Output Schema

Example extracted metric:

```json
{
  "metric_name": "Total Cyber Security Exports",
  "value": 1.2,
  "unit": "Billion EUR",
  "year": 2022,
  "source": {
    "page": 14,
    "text_snippet": "Exports reached €1.2 billion in 2022",
    "confidence": 0.91,
    "method": "table_parser"
  }
}
```

---

# 🛠 Setup Instructions

## 1️⃣ Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate        # mac/linux
# venv\Scripts\activate         # windows
```

---

## 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 3️⃣ Configure Environment

Create a `.env` file:

```
UPLOAD_DIR=uploads
ENVIRONMENT=development
REDIS_URL=
DATABASE_URL=sqlite:///./test.db
USE_CELERY=false
CEREBRAS_API_KEY=your_key_here
CEREBRAS_MODEL=llama-3.1-8b
```

---

# ▶ Running the Application

## 🔹 Development Mode (Without Celery)

```bash
uvicorn app.main:app --reload
```

Access API docs:

```
http://localhost:8000/docs
```

---

## 🔹 Production Mode (With Celery)

Start worker:

```bash
celery -A app.workers.celery_app worker --pool=threads --concurrency=2 --loglevel=info
```

Start API:

```bash
uvicorn app.main:app --reload
```

---

# 📡 API Endpoints

## 📤 Upload PDF

**POST** `/upload`

Uploads and processes the PDF.

---

## 📥 Get Extracted Metrics

**GET** `/metrics`

Returns structured JSON dataset.

---

## 📁 Export CSV

**GET** `/export/csv`

Downloads extracted dataset in CSV format.

---

# 🏗 Design Decisions

### Why Recursive Parsing?

PDF documents contain nested structures (sections, subsections, tables).
Recursive traversal preserves context and improves semantic accuracy.

### Why LLM Integration?

Certain complex charts and ambiguous text require semantic interpretation beyond regex-based extraction.

### Why Confidence Scoring?

Downstream economic analysis requires traceability and reliability scoring.

---

# 📈 Scalability Considerations

* Celery for background processing
* Redis-backed task queue
* Modular extraction services
* Toggle-based async support
* Database abstraction layer

---

# 🧪 Future Enhancements

* True vector chart numeric extraction
* File hashing for idempotency
* Extraction versioning
* Model performance logging
* Structured economic taxonomy mapping

---

# 🧑‍💻 Author

Rajendra Bisoi
Backend Engineer | Document Intelligence | Data Systems

---