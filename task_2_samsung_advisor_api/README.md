# 🤖 Task 2 — Samsung Phone Advisor API  

---

## 📘 Project Overview
This project creates an **AI-powered API** that intelligently answers questions about Samsung smartphones — including specifications, comparisons, and buying suggestions.  
It uses:
- **FastAPI** for serving responses  
- **PostgreSQL** to store the phone dataset  
- **SentenceTransformer** for semantic retrieval and Transformer-based text generation for response synthesis  

---

## ⚙️ Requirements
```bash
pip install -r requirements.txt
```

### requirements.txt
```
fastapi
uvicorn
sqlalchemy
psycopg2
pandas
sentence-transformers==2.7.0
transformers==4.41.0
torch==2.2.2+cpu
```

*(You can remove `+cpu` if you have GPU support.)*

---

## 🧱 Database Setup
1. Make sure PostgreSQL is running.  
2. Create a database named **samsungdb**:  
   ```sql
   CREATE DATABASE samsungdb;
   ```
3. Open `insert_to_postgres.py` — it automatically creates a table `samsung_phones` and inserts phone specs.  
   ```bash
   python insert_to_postgres.py
   ```

---

## ▶️ Run the API
```bash
uvicorn samsung_advisor_api:app --reload
```

Then open your browser at:  
👉 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 💬 Example Queries

| Example Question | Expected Response |
|------------------|------------------|
| `{ "question": "What are the specs of Samsung Galaxy S23 Ultra?" }` | Returns the phone’s display, camera, battery, and memory specs. |
| `{ "question": "Compare Samsung Galaxy S23 Ultra and S22 Ultra" }` | Compares both models and recommends one. |
| `{ "question": "Which Samsung phone has the best battery under $1000?" }` | Returns the model with the highest battery capacity within that range. |

---

## ⚙️ Internal Logic (RAG + Multi-Agent Design)

The system follows a unified Retrieval-Augmented Generation (RAG) and multi-agent architecture:

- **RAG Module**
  - Retrieves structured phone specifications from PostgreSQL
  - Uses semantic similarity to identify the most relevant Samsung models
  - Answers direct factual questions (e.g., specifications, prices)

- **Agent 1 — Data Extraction Agent**
  - Fetches relevant phone records from PostgreSQL based on the query
  - Handles filtering, comparison candidates, and constraints (e.g., price limit)

- **Agent 2 — Review & Recommendation Agent**
  - Generates natural-language comparisons and recommendations
  - Uses retrieved data as context to produce human-like explanations

- **Response Composer**
  - Combines structured facts with generated insights
  - Returns a single unified response to the user
  

---

## 📂 Folder Structure
```
task_2_samsung_advisor_api/
 ├── samsung_scraper.py
 ├── samsung_phones.csv
 ├── insert_to_postgres.py
 ├── samsung_advisor_api.py
 ├── test_selenium.py
 ├── requirements.txt
 └── README.md
```

---

## 🧑‍💻 Author
**Md. Abu Sufian** — hisamsufian@gmail.com  
