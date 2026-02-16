# 🧠 Cyber Intel PDF Metric Extraction Pipeline

Production-grade FastAPI pipeline that extracts structured economic metrics from complex PDFs including:

* ✅ Multi-line high fidelity tables
* ✅ Vector-based bar charts (path parsing)
* ✅ Semantic metric classification
* ✅ Taxonomy mapping
* ✅ GVA & longitudinal dataset reconstruction

Outputs structured JSON suitable for economic analysis.

---

# 📐 Architecture Overview

```
FastAPI → Upload PDF
        → Extract Tables
        → Extract Vector Charts
        → Semantic Classification
        → Taxonomy Mapping
        → Store Structured Metrics
```

Optional:

```
FastAPI → Celery → Redis → Background Processing
```

---

# 📦 Project Structure

```
app/
│
├── main.py
├── tasks.py
│
├── api/
│   └── upload.py
│
├── core/
│   ├── config.py
│   └── logging.py
│
├── db/
│   ├── database.py
│   └── models.py
│
├── extractors/
│   ├── table_engine.py
│   ├── chart_engine.py
│   └── text_engine.py
│
├── classification/
│   ├── semantic_classifier.py
│   └── taxonomy_mapper.py
│
├── services/
│   └── pipeline_service.py
│
uploads/
```

---

# 🛠 DEVELOPMENT SETUP (Recommended)

This mode:

* Uses SQLite
* Does NOT use Celery
* Processes synchronously
* Best for debugging extraction logic

---

## ✅ Step 1 — Create `.env`

```
UPLOAD_DIR=uploads
ENVIRONMENT=development
DATABASE_URL=sqlite:///./test.db
REDIS_URL=redis://localhost:6379/0
```

---

## ✅ Step 2 — Fix requirements.txt (Python 3.12 Safe)

Remove this line:

```
torch==2.2.2+cpu --index-url https://download.pytorch.org/whl/cpu
```

Keep:

```
sentence-transformers==5.2.2
```

---

## ✅ Step 3 — Create Virtual Environment

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install --upgrade pip
```

---

## ✅ Step 4 — Install CPU Torch FIRST

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

This installs CPU-only torch.

No CUDA.
No NVIDIA.

---

## ✅ Step 5 — Install Requirements

```bash
pip install -r requirements.txt
```

---

## ✅ Step 6 — Run Application

```bash
uvicorn app.main:app --reload
```

App runs at:

```
http://localhost:8000
```

---

## ✅ Upload PDF (Development Mode)

Use:

```
POST http://localhost:8000/upload?celery=false
```

Example:

```bash
curl -X POST "http://localhost:8000/upload?celery=false" \
  -F "file=@report.pdf"
```

Processing runs immediately in terminal.

You will see logs like:

```
--- PAGE 30 ---
Y TICKS:
X YEARS:
BARS:
```

---

# 🚀 PRODUCTION SETUP

Production mode uses:

* PostgreSQL
* Redis
* Celery worker
* Async processing

---

## ✅ Environment Variables (.env)

```
UPLOAD_DIR=/var/data/uploads
ENVIRONMENT=production
DATABASE_URL=postgresql://user:password@localhost:5432/cyberintel
REDIS_URL=redis://localhost:6379/0
```

---

## ✅ Install Dependencies

Same torch CPU process as above.

Then:

```bash
pip install -r requirements.txt
```

---

## ✅ Start PostgreSQL

Ensure database exists:

```sql
CREATE DATABASE cyberintel;
```

---

## ✅ Start Redis

```bash
redis-server
```

---

## ✅ Start FastAPI

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## ✅ Start Celery Worker

```bash
celery -A app.core.celery_app worker --pool=threads --concurrency=2 --loglevel=info
```

---

## ✅ Upload PDF (Production Mode)

```
POST http://localhost:8000/upload
```

(Processing runs in background worker. `?celery=true`)
(No Processing in background `?celery=false`)


---

# 📊 What the System Extracts

### Tables

* Multi-line headers reconstructed
* Column-to-metric inference
* Year extraction
* Currency normalization
* Source page tagging

### Vector Charts

* Y-axis tick detection
* X-year alignment
* Bar height scaling
* Chart title extraction
* Numeric value reconstruction

### Classification

* Employment
* Company count
* Revenue
* GVA
* Investment
* Growth rate

### Output Fields

```
{
  metric_key,
  value,
  unit,
  year,
  page_number,
  category,
  source_type,
  confidence_score,
  raw_text
}
```

---

# 🧪 Testing Torch

```bash
python
```

```python
import torch
print(torch.cuda.is_available())
```

Expected:

```
False
```

---

# 🧯 Troubleshooting

---

### ❌ Torch install error

Cause:
Pinned incompatible version

Fix:
Remove pinned torch
Install CPU torch first

---

### ❌ Redis connection error

Cause:
Celery enabled but Redis not running

Fix:
Use:

```
/upload?celery=false
```

for dev

---

### ❌ Chart values look wrong

Check:

* Y ticks sorted
* X years sorted
* Linear scaling calculation

---

### ❌ Tables misclassified

Improve:
`infer_metric_key_from_header()`

---

# 🧠 Performance Notes

Development mode:

* Suitable for debugging
* Not scalable

Production mode:

* Handles large PDFs
* Background job execution
* Suitable for multi-document ingestion

---

# 📦 Optional: Docker (Production)

You can containerize:

* FastAPI
* Celery
* Redis
* Postgres

If you want, I can generate full Docker Compose next.

---

# 🎯 Current Capability Status

| Feature                         | Status |
| ------------------------------- | ------ |
| Multi-line table reconstruction | ✅      |
| Vector bar chart extraction     | ✅      |
| Year alignment                  | ✅      |
| Semantic metric classification  | ✅      |
| Taxonomy mapping                | ✅      |
| Longitudinal dataset ready      | ✅      |
| Async background processing     | ✅      |

---