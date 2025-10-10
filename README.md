# Computer Science Research Article Subject Classifier

A **multi-label classification project** that predicts Computer Science subjects (e.g., _Machine Learning (cs.LG)_, _Artificial Intelligence (cs.AI)_) based on paper abstracts.

The pipeline includes:
- Scraping **~30,000 papers (2023–2025)** using Selenium  
- Training **SciBERT**, **DistilBERT**, and **DeBERTa-v3-small**
- Selecting **SciBERT** for deployment due to superior performance
- Converting the model to **ONNX** for optimized inference
- Deploying via **Flask on Render** and **Gradio on Hugging Face Spaces**

---

## Table of Contents

- [Project Overview](#project-overview)
- [Branches](#branches)
- [Dataset](#dataset)
- [Model Training](#model-training)
- [Model Performance](#model-performance)
- [ONNX Conversion](#onnx-conversion)
- [Flask Web App](#flask-web-app)
- [Deployment](#deployment)
- [Installation](#installation)
- [Usage](#usage)
- [Directory Structure](#directory-structure)
- [Contributing](#contributing)
- [License](#license)

---

## Project Overview

This project classifies arXiv papers into multiple Computer Science subjects using their **abstracts**.

### Key Steps

1. **Data Collection** — Scraped ~30,000 papers using Selenium  
2. **Preprocessing** — Cleaned abstracts and subjects, filtered rare subjects  
3. **Model Training** — Trained SciBERT, DistilBERT, DeBERTa-v3-small  
4. **Model Selection** — Chose SciBERT for best performance  
5. **ONNX Conversion** — Exported model for optimized inference (reduced size from 421 MB to 110 MB)  
6. **Deployment** — Hosted on Render and Hugging Face Spaces

---

## Branches

| Branch | Description |
|:--|:--|
| **main** | Data scraping, preprocessing, model training, ONNX conversion and Deploying on Gradio on Hugging Face Spaces |
| **flask** | Flask web app for inference using the Hugging Face API |

---

## Dataset

- **Source:** [arXiv.org](https://arxiv.org)  
- **Category:** Computer Science (cs)  
- **Years:** 2023–2025 (~10,000 papers/year, total ~30,000)  

**Fields:** `title`, `abstract`, `subjects`, `url`, `authors`

**Preprocessing:**
- Removed LaTeX, URLs, punctuation; converted to lowercase  
- Parsed subjects into full names (e.g., *Computation and Language (cs.CL)*)  
- Filtered rare subjects:
  - **Initial subjects:** 141
  - **Rare subjects removed:** 103
  - **Final subjects:** 38 (threshold = 0.005)
- Saved subject encodings to `subject_types_encoded.json`


**Scripts:**
- `src/scraper.py` — Scrapes arXiv papers using Selenium  
- `src/merge_data.py` — Merges yearly CSV files into one  

---

##  Model Training

Trained three models using **FastAI** + **blurr**:

| Model | Parameters | Source |
|:--|:--:|:--|
| **SciBERT** | ~110M | `allenai/scibert_scivocab_uncased` |
| **DistilBERT** | ~66M | `distilbert-base-uncased` |
| **DeBERTa-v3-small** | ~44M | `microsoft/deberta-v3-small` |

### Training Configuration

- **Max length:** 512 tokens  
- **Loss:** `BCEWithLogitsLossFlat`
- **Metrics:** Accuracy (thresh=0.2), F1 (micro/macro)
- **Training Stages:**
  - **Stage 0:** Train classifier head (frozen) — 2 epochs  
  - **Stage 1:** Fine-tune entire model — 3–5 epochs  

---

## Model Performance

| Model | Parameters | Valid Loss | Accuracy | F1 Score (Micro) | Training Time/Epoch |
|:--|:--:|:--:|:--:|:--:|:--:|
| **SciBERT** ✅ | ~110M | **0.0672** | **0.9743** | **0.5513** | ~4m 22s |
| **DistilBERT** | ~66M | 0.0761 | 0.9708 | 0.3881 | ~2m 23s |
| **DeBERTa-v3-small** | ~44M | 0.0764 | 0.9707 | 0.3867 | ~2m 23s |

### Why SciBERT?

**SciBERT** was selected for deployment based on:

1. **Domain-Specific Pretraining** — Trained on 1.14M scientific papers, providing better understanding of academic abstracts
2. **Superior F1 Score** — 0.5513 vs 0.3881 (DistilBERT) and 0.3867 (DeBERTa), representing **42-43% improvement**
3. **Lowest Validation Loss** — 0.0672 indicates better generalization
4. **Specialized Vocabulary** — Scientific terms and notation for better technical concept representation

**Trade-off:** Longer training time (4m 22s vs ~2m 23s), justified by substantial performance gains for classifying 38 Computer Science subjects.

---

##  ONNX Conversion

Converted SciBERT to ONNX for efficient inference with quantization.

### File Size Comparison

| Format | Size | Reduction |
|:--|:--:|:--:|
| **PyTorch Model** | 421.3 MB | - |
| **ONNX (FP32)** | 424.7 MB | - |
| **ONNX Quantized (INT8)** | 110.3 MB | **74%** |

### Benefits

- **Faster Inference** — Optimized runtime performance
- **Reduced Size** — INT8 quantization (424.7 MB → 110.3 MB)
- **Cross-Platform** — Deploy on various frameworks and devices
- **Production Ready** — Industry-standard format

**Script:** ``

---

## Flask Web App

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

---

## Deployment

### Deployment on Hugging Face Spaces

Deploy a Gradio interface on Hugging Face Spaces for interactive demos.

**Steps:**

1. Create a new Space on [Hugging Face Spaces](https://huggingface.co/spaces)
2. Select **Gradio** as the SDK
3. Use files from `deployment/` folder:

```
deployment/
├── app.py                    # Gradio application
├── requirements.txt          # Dependencies
├── README.md                 # Space documentation
```

🔗 ****Try it here**:** 👉 [Live Demo](https://huggingface.co/spaces/yeager07/multi-label-cs-article-classification)

<img src="assets/images/gradio_app.png" width="900" height="450">

---

### Deployment on Render

Deploy the Flask app on Render for production use.

**Steps:**

1. Push `flask` branch to GitHub  
2. Connect to Render → New Web Service  
3. Configure build and start commands:

```yaml
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app
```

4. Set environment variable:
   - **HUGGINGFACE_API_TOKEN** (your Hugging Face API token)

5. Deploy with **Python 3** environment

🔗 **Check it here** 👉 [Live App](https://multi-label-computer-science-article.onrender.com)

<img src="assets/images/demo1.png" width="900" height="450">
<img src="assets/images/demo2.png" width="900" height="450">

---



## Installation

### Prerequisites
- Python ≥ 3.8    
- Git  
- Hugging Face account

### Steps

```bash
# Clone repository
git clone https://github.com/your-username/arxiv-subject-classifier.git
cd arxiv-subject-classifier

# Install dependencies
pip install -r requirements.txt

# Set Hugging Face token
export HUGGINGFACE_API_TOKEN='your-token'
```

**requirements.txt**
```
pandas
selenium
fastai==2.7.17
torch
transformers[sentencepiece]
evaluate
onnxruntime
onnx
flask
requests
gunicorn
```

---

## Usage

### Data Collection & Training (main branch)

```bash
# Scrape arXiv data
python scraper.py

# Merge yearly CSV files
python merge_data.py

# Train and export model
jupyter notebook 
```

### Flask App (flask branch)

```bash
git checkout flask
python app.py
```

Visit `http://localhost:5000` to test locally.

---

## Directory Structure

```
Multi-Label-Computer-Science-Article-Classifier/
├── main (branch)
│   ├── data/                     # Dataset files
│   ├── deployment/               # Hugging Face Spaces deployment
│   │   ├── app.py
│   │   ├── requirements.txt
│   │   ├── README.md
│   │   
│   ├── models/                   # Trained models
│   │   
│   │   
│   ├── notebooks/                # Training notebooks
│   │   
│   ├── src/                      # Source code
│   │   ├── scraper.py
│   │   └── merge_data.py
│   ├── README.md
│   └── requirements.txt
│
└── flask (branch)
    ├── static/                   # CSS and assets
    ├── templates/                # HTML templates
    │   └── index.html
    ├── .gitignore
    ├── app.py                    # Flask application
    ├── README.md
    └── requirements.txt
```

---

## Contributing

Contributions are welcome!

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-branch`
3. Commit changes: `git commit -m "Add new feature"`
4. Push and create PR: `git push origin feature-branch`

---

## 📄 License

This project is licensed under the MIT License.

---

🌟 **If you like this project, give it a star on GitHub!**










