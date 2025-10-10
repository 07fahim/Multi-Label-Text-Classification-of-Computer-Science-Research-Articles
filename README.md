# 🧠 arXiv Subject Classifier

A **multi-label classification project** that predicts arXiv Computer Science subjects (e.g., _Machine Learning (cs.LG)_, _Artificial Intelligence (cs.AI)_) based on paper abstracts.

The pipeline includes:
- Scraping **~30,000 papers (2023–2025)** using Selenium  
- Training **SciBERT**, **DistilBERT**, and **DeBERTa-v3-small**
- Selecting **SciBERT** for deployment due to superior performance
- Converting the model to **ONNX**
- Deploying a **Flask web app** on Render using the **Hugging Face Inference API**

---

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Branches](#branches)
- [Dataset](#dataset)
- [Model Training](#model-training)
- [Model Performance](#model-performance)
- [ONNX Conversion](#onnx-conversion)
- [Flask Web App](#flask-web-app)
- [Deployment on Render](#deployment-on-render)
- [Installation](#installation)
- [Usage](#usage)
- [Directory Structure](#directory-structure)
- [Contributing](#contributing)
- [License](#license)

---

## 🚀 Project Overview

This project classifies arXiv papers into multiple Computer Science subjects using their **abstracts**.

### Workflow

- **Branch: `main`**
  - Data scraping, preprocessing, model training, and ONNX conversion  
- **Branch: `flask`**
  - Flask web app for inference using the Hugging Face API  

### Key Steps

1. **Data Collection** — Scraped ~30,000 papers using Selenium  
2. **Preprocessing** — Cleaned abstracts and subjects, filtered rare subjects (threshold = 0.01)  
3. **Model Training** — Trained SciBERT, DistilBERT, DeBERTa-v3-small  
4. **Model Selection** — Chose SciBERT for best performance  
5. **ONNX Conversion** — Exported model for optimized inference  
6. **Web App** — Flask app with subject prediction  
7. **Deployment** — Hosted on Render

---

## 🌐 Branches

| Branch | Description |
|:--|:--|
| **main** | Data scraping, preprocessing, model training, ONNX conversion |
| **flask** | Flask web app for inference using the Hugging Face API |

---

## 📚 Dataset

- **Source:** [arXiv.org](https://arxiv.org)  
- **Category:** Computer Science (cs)  
- **Years:** 2023–2025 (~10,000 papers/year, total ~30,000)  

**Fields:**  
`title`, `abstract`, `subjects`, `url`, `authors`

**Preprocessing:**
- Removed LaTeX, URLs, punctuation; converted to lowercase  
- Parsed subjects into full names (e.g., *Computation and Language (cs.CL)*)  
- Filtered rare subjects (occurrence threshold = 0.01, ≈31 subjects)

**Output:**  
`arxiv_cs_papers_combined.csv` (~30,000 rows)

**Scripts:**
- `scraper.py` — Scrapes arXiv papers using Selenium  
- `merge_data.py` — Merges yearly CSV files into one  

---

## 🧩 Model Training

Trained three models using **FastAI** + **blurr**:

| Model | Parameters | Source |
|:--|:--:|:--|
| **SciBERT** | ~110M | `allenai/scibert_scivocab_uncased` |
| **DistilBERT** | ~66M | `distilbert-base-uncased` |
| **DeBERTa-v3-small** | ~44M | `microsoft/deberta-v3-small` |

### ⚙️ Training Details

- **Dataset:** `cs_2025_papers_10k.csv` (extended to ~30,000)
- **Subjects threshold:** 0.01 (~31 subjects)
- **Max length:** 512 tokens  
- **Loss:** `BCEWithLogitsLossFlat` (unweighted)
- **Metrics:** Accuracy (thresh=0.2), F1 (micro/macro)
- **Training Stages:**
  - **Stage 0:** Train classifier head (frozen) — 2 epochs  
  - **Stage 1:** Fine-tune entire model — 3–5 epochs  

**Libraries:**  
`fastai`, `blurr`, `transformers`, `onnxruntime`

---

## 📊 Model Performance

| Model | Valid Loss | Accuracy (thresh=0.2) | F1 Score | Time/Epoch |
|:--|:--:|:--:|:--:|:--:|
| **SciBERT** | 0.0672 | 0.9743 | 0.5513 | ~4m 22s |
| **DistilBERT** | 0.0761 | 0.9708 | 0.3881 | ~2m 23s |
| **DeBERTa-v3-small** | 0.0764 | 0.9707 | 0.3867 | ~2m 23s |

✅ **Selected Model:** `SciBERT` — Highest accuracy and F1 score.

---

## ⚡ ONNX Conversion

Converted SciBERT (Stage 1) to ONNX for efficient inference.

| Type | Path | Details |
|:--|:--|:--|
| **Normal ONNX** | `models/allenai_scibert_scivocab_uncased_arxiv-classifier.onnx` | FP32 |
| **Quantized ONNX** | `models/allenai_scibert_scivocab_uncased_arxiv-classifier-quantized.onnx` | INT8 (QuantType.QUInt8) |

Script: `3_multilabel_classification_scibert_unweighted_onnx.ipynb`

Evaluated via accuracy, F1 (micro/macro), confusion matrix, and classification report.

---

## 🌍 Flask Web App

Flask app (in `flask` branch) allows users to input an **abstract** and receive **predicted subjects**.

### Features
- Input: Abstract via HTML form  
- Output: Subjects with confidence scores  
- API: Hugging Face Inference API  

**Files:**
```
flask/
├── app.py
├── templates/
│   └── index.html
└── static/
    └── style.css
```

**Dependencies:**  
`Flask`, `requests`, `transformers`

---

## ☁️ Deployment on Render

Steps:

1. Push `flask` branch to GitHub  
2. Connect to Render → New Web Service  
3. Configure:

```yaml
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app
```

4. Environment:
   - **Python 3**
   - **HUGGINGFACE_API_TOKEN** (set as environment variable)

🔗 **Example URL:**  
[https://arxiv-subject-classifier.onrender.com](https://arxiv-subject-classifier.onrender.com) *(replace with your actual deployment link)*

---

## 🧱 Installation

### Prerequisites
- Python ≥ 3.8  
- ChromeDriver (for Selenium)  
- Git  
- Hugging Face account

### Steps

```bash
# Clone repository
git clone https://github.com/your-username/arxiv-subject-classifier.git
cd arxiv-subject-classifier

# Switch branches
git checkout main  # for training
# or
git checkout flask  # for web app

# Install dependencies
pip install -r requirements.txt
```

**requirements.txt**

```
pandas
selenium
fastai==2.7.17
torch
transformers[sentencepiece]
nbdev
plum-dispatch
evaluate
seqeval
onnxruntime
onnx
flask
requests
gunicorn
```

Set your Hugging Face token:

```bash
export HUGGINGFACE_API_TOKEN='your-huggingface-api-token'
```

or create `.env`:

```ini
HUGGINGFACE_API_TOKEN=your-huggingface-api-token
```

---

## ▶️ Usage

### Main Branch

```bash
# Scrape arXiv data
python scraper.py

# Merge yearly CSV files
python merge_data.py
```

Outputs combined data:

```
output/arxiv_cs_papers_combined.csv
```

Then train & export:

```
jupyter notebook 3_multilabel_classification_scibert_unweighted_onnx.ipynb
```

### Flask Branch

```bash
git checkout flask
python app.py
```

Visit `http://localhost:5000` to test locally.

Deploy by pushing to Render as described above.

---

## 🤗 Hugging Face Model Hosting

Push your trained SciBERT model to Hugging Face Hub:

```python
from transformers import AutoModelForSequenceClassification

model = AutoModelForSequenceClassification.from_pretrained(
    "path/to/models/allenai_scibert_scivocab_uncased_arxiv-classifier-stage-1"
)
model.push_to_hub("your-username/arxiv-scibert-classifier", use_auth_token="your-huggingface-api-token")
```

---

## 🗂️ Directory Structure

```
arxiv-subject-classifier/
├── main (branch)
│   ├── output/
│   ├── models/
│   ├── scraper.py
│   ├── merge_data.py
│   ├── 3_multilabel_classification_scibert_unweighted_onnx.ipynb
│   ├── subject_types_encoded.json
│   └── requirements.txt
├── flask (branch)
│   ├── templates/
│   ├── static/
│   ├── app.py
│   └── requirements.txt
└── README.md
```

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repo
2. Create a branch:
   ```bash
   git checkout -b feature-branch
   ```
3. Commit changes:
   ```bash
   git commit -m "Add new feature"
   ```
4. Push and create PR:
   ```bash
   git push origin feature-branch
   ```

---

## 📄 License

This project is licensed under the MIT License.  
See the LICENSE file for details.

---

🌟 **If you like this project, give it a star on GitHub!**
