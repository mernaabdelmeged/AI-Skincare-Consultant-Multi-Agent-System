# 🌸 AI Skincare Consultant — Multi-Step Agent System

> **Final Project** — AI Agents & LLM Applications Training Program  
> Orange Digital Center Egypt × Digital Hub

---

## 📌 Overview

An intelligent skincare consultant powered by a **Multi-Step AI Agent System**. Analyzes skin condition via text and/or image, then delivers a complete personalized skincare routine through 3 specialized AI agents working in sequence.

---

## 🤖 3 AI Agents Pipeline

```
Patient Input (Text + Image)
        │
        ▼
🕵️ AGENT 1 — Skin Analyst       → Clinical skin assessment
        │
        ▼
🛍️ AGENT 2 — Product Researcher  → Searches 3 databases for best products
        │
        ▼
✍️ AGENT 3 — Routine Planner     → Full structured skincare report
        │
        ▼
📄 Auto-saved Prescription + 🗂️ Patient Data Logged
```

---

## ✨ Features

- 🔬 Multimodal Analysis — processes skin images + text descriptions
- 🗄️ Multi-Source Retrieval — 1,100+ products, Egyptian local alternatives, Kaggle dataset
- 🧬 Medical Knowledge Base — clinical ingredient rules and contraindications
- ⚙️ Automated Actions — auto-saves prescriptions, logs patient data to CSV
- 🌸 Premium UI — Streamlit with custom CSS and animated gradients
- 🇪🇬 Egyptian Local Alternatives — budget-friendly recommendations

---

## 🛠️ Tech Stack

| Technology | Usage |
|---|---|
| Python 3.10 | Core language |
| Google Gemini 2.5 Flash | LLM & Vision AI |
| Streamlit | Web interface |
| Pandas | Data handling |
| PIL (Pillow) | Image processing |

---

## ⚙️ Setup

### 1. Clone the repo
```bash
git clone https://github.com/your-username/ai-skincare-consultant.git
cd ai-skincare-consultant
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Create your data folder
```
data/
├── skincare_products.csv
├── egyptian_local_dupes.csv
├── skincare_knowledge.md
└── kaggle_data/skincare_products_clean.csv
```

### 4. Add your API key
Create `.env` file:
```
GEMINI_API_KEY=your_gemini_api_key_here
```
Get free key from [Google AI Studio](https://aistudio.google.com/)

### 5. Run
```bash
streamlit run app.py
```

---

## 📊 Report Output

| Section | Content |
|---|---|
| 🔍 Skin Analysis | Skin type, concerns, clinical observations |
| 💊 Recommended Ingredients | Active ingredients + contraindications |
| ☀️ Morning Routine | Step-by-step AM routine |
| 🌙 Night Routine | Step-by-step PM routine |
| 🛍️ Recommended Products | Products with prices |
| ⛔ What to Avoid | Ingredients & habits to avoid |
| 💡 Healing Tips | 3–5 practical tips |

---

## 👩‍💻 Developer

**Merna Mohamed** — Orange Digital Center Egypt | AI Agents Training Program

---

## ⚠️ Disclaimer

AI-generated suggestions only. Not a substitute for professional medical diagnosis. Always consult a licensed dermatologist.
