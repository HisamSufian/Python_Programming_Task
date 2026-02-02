# 🚀 Python Programming Project

---

## 📁 Overview
Two independent Python projects:
- **Task-1:** Algorithmic Trading Adventure, simulates a simple Golden-Cross Trading Strategy using Python and historical stock data fetched via yfinance. The algorithm automatically buys when a Golden Cross occur (50-day MA > 200-day MA) and sells when a Death Cross occurs. It starts with a capital and reports the final profit / loss.
- **Task-2:** Samsung Phone Advisor API, An intelligent FastAPI-based service for Samsung phone queries. Uses PostgreSQL for data storage and sentence-transformers for semantic similarity. Supports comparison, specification lookup, best-feature search, and recommendations. Fully tested with sample inputs from the assignment and produces correct structured JSON outputs.

| # | Project | Domain | Description |
|--|--|--|--|
| __1__ | __Algorithmic Trading Adventure__ | Finance + Data Science | Golden-Cross trading strategy using yfinance & pandas |
| __2__ | __Samsung Phone Advisor API__ | AI + Web + NLP | FastAPI service that answers Samsung-related questions intelligently |

---

### 🛠 Common Requirements
- Python 3.11+
- `pip`
- (PostgreSQL required only for Task 2)

---

### ▶️ Run Each Task

**Task 1:**
```bash
cd task_1_algorithmic_trading
pip install -r requirements.txt
python task_1_gcse.py
```

---

**Task 2:**
```bash
cd task_2_samsung_advisor_api
pip install -r requirements.txt
python insert_to_postgres.py
uvicorn samsung_advisor_api:app --reload
```

---

Then open: http://127.0.0.1:8000/docs

---
📂 Folder Structure
Python_Programming_Task/
 ├── task_1_algorithmic_trading/
 ├── task_2_samsung_advisor_api/
 └── README.md

---

Author: Md. Abu Sufian — hisamsufian@gmail.com
---
