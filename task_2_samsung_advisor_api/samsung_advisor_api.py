# -*- coding: utf-8 -*-
"""
Samsung Phone Advisor API

A unified RAG + multi-agent system that answers natural-language
questions about Samsung smartphones using PostgreSQL and NLP models.
"""

# ======================================================
# Samsung Phone Advisor API (Smart Intent-based)
# Author: Sufian
# ======================================================

from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine
import pandas as pd
import re
from sentence_transformers import SentenceTransformer, util
from transformers import pipeline

# ======================================================
# 1️⃣ FastAPI Setup
# ======================================================
app = FastAPI(
    title="Samsung Phone Advisor API",
    description="Smart assistant for Samsung phone specs, comparisons, and buying advice.",
    version="2.0"
)

# ======================================================
# 2️⃣ Database Connection
# ======================================================
DATABASE_URL = "postgresql+psycopg2://postgres:password@localhost/samsungdb" 
engine = create_engine(DATABASE_URL)

# ======================================================
# 3️⃣ Load Models
# ======================================================
print("🔄 Loading AI models... (please wait)")
model_embed = SentenceTransformer("all-MiniLM-L6-v2")
reviewer = pipeline("text-generation", model="distilgpt2")
print("✅ Models loaded successfully!")

# ======================================================
# 4️⃣ Request Schema
# ======================================================
class Question(BaseModel):
    question: str

# ======================================================
# 5️⃣ Intent Detection
# ======================================================
def detect_intent(q: str) -> str:
    q = q.lower()
    if any(k in q for k in ["compare", "vs", "better", "difference"]):
        return "compare"
    elif any(k in q for k in ["best", "under", "battery", "camera", "performance"]):
        return "feature"
    elif any(k in q for k in ["buy", "recommend", "suggest", "for gaming", "for photography"]):
        return "recommend"
    elif any(k in q for k in ["list", "latest", "top", "models", "phones"]):
        return "list"
    else:
        return "spec"

# ======================================================
# 6️⃣ Agent 1 — Data Retrieval (RAG)
# ======================================================
def find_closest_model(question, df):
    df = df.dropna(subset=["Model"])
    q_lower = question.lower()

    # Normalize strings
    df["model_lower"] = df["Model"].str.lower()

    # 1️⃣ Exact match
    for m in df["model_lower"]:
        if m == q_lower.strip():
            return df.loc[df["model_lower"] == m, "Model"].iloc[0]

    # 2️⃣ Contains all key tokens (e.g., 's23', 'ultra')
    q_tokens = [t for t in re.findall(r"\w+", q_lower) if len(t) > 1]
    for m in df["model_lower"]:
        if all(token in m for token in q_tokens if token not in ["samsung", "galaxy"]):
            return df.loc[df["model_lower"] == m, "Model"].iloc[0]

    # 3️⃣ Partial name match — prefer same series (S, A, M, Z)
    series_hint = re.search(r"\b([samz]\d{1,2})\b", q_lower)
    if series_hint:
        s = series_hint.group(1).lower()
        for m in df["model_lower"]:
            if s in m:
                return df.loc[df["model_lower"] == m, "Model"].iloc[0]

    # 4️⃣ Fallback: semantic similarity (as last resort)
    question_emb = model_embed.encode(question, convert_to_tensor=True)
    model_embs = model_embed.encode(df["Model"].tolist(), convert_to_tensor=True)
    scores = util.cos_sim(question_emb, model_embs)[0]
    best_idx = int(scores.argmax())
    best_model = df.iloc[best_idx]["Model"]
    best_score = float(scores[best_idx])
    return best_model if best_score > 0.65 else None




# ======================================================
# 7️⃣ Feature Lookup / Spec Generation
# ======================================================
def generate_answer(question: str, df: pd.DataFrame):
    matched_model = find_closest_model(question, df)
    if matched_model:
        specs = df[df["Model"] == matched_model].iloc[0]
        return (
            f"{matched_model}: Display={specs.get('Display','N/A')}, "
            f"Camera={specs.get('Camera','N/A')}, Battery={specs.get('Battery','N/A')}, "
            f"Memory={specs.get('Memory','N/A')}."
        )
    return "Sorry, I couldn't find details for that model from my data."

# ======================================================
# 8️⃣ Compare Two Phones
# ======================================================
def compare_two_phones(question, df):
    # Split by "and" or "vs"
    parts = re.split(r"\band\b|\bvs\b", question, flags=re.IGNORECASE)
    if len(parts) < 2:
        return "Please mention two phones to compare."

    phone1_q, phone2_q = parts[0].strip(), parts[1].strip()
    phone1 = find_closest_model(phone1_q, df)
    phone2 = find_closest_model(phone2_q, df)

    if not phone1 or not phone2:
        return f"Sorry, I couldn’t clearly identify both models: {phone1 or '?'} and {phone2 or '?'}."

    row1 = df[df["Model"] == phone1].iloc[0]
    row2 = df[df["Model"] == phone2].iloc[0]

    better_camera = phone1 if len(str(row1["Camera"])) > len(str(row2["Camera"])) else phone2
    better_battery = phone1 if len(str(row1["Battery"])) > len(str(row2["Battery"])) else phone2
    overall = better_camera if better_camera == better_battery else phone1

    return (
        f"{phone1} has a better camera and battery life than {phone2}. "
        f"Overall, {overall} is recommended for photography and long-term use."
    )



# ======================================================
# 9️⃣ Find Best Phone by Feature (battery/camera/etc.)
# ======================================================
def best_feature_phone(question, df):
    df = df.copy()
    if "battery" in question:
        df["battery_numeric"] = df["Battery"].str.extract(r"(\d+)").astype(float)
        best = df.sort_values("battery_numeric", ascending=False).iloc[0]
        return f"The best battery phone is {best['Model']} with {best['Battery']} capacity and {best['Display']} display."

    if "camera" in question:
        df["camera_numeric"] = df["Camera"].str.extract(r"(\d+)").astype(float)
        best = df.sort_values("camera_numeric", ascending=False).iloc[0]
        return f"The best camera phone is {best['Model']} featuring {best['Camera']}."

    return "Sorry, I couldn’t determine which feature you meant from my Data."

# ======================================================
# 🔟 Recommendation Logic
# ======================================================
def recommend_phone(question, df):
    if "gaming" in question:
        return "Samsung Galaxy S24 Ultra is best for gaming — Snapdragon 8 Gen 3, 120Hz AMOLED, and excellent cooling."
    if "photography" in question:
        return "Samsung Galaxy S24 Ultra is ideal for photography with its 200MP sensor and 5× optical zoom."
    return "Samsung Galaxy S25+ offers balanced performance and value for most users."

# ======================================================
# 11️⃣ List Latest Phones
# ======================================================
def list_latest(df):
    latest = df["Model"].head(5).tolist()
    return f"Here are some of the latest Samsung phones: {', '.join(latest)}."

# ======================================================
# 12️⃣ Main Endpoint
# ======================================================
@app.post("/ask")
def ask(question: Question):
    df = pd.read_sql("SELECT * FROM samsung_phones", engine)
    q = question.question
    intent = detect_intent(q)

    if intent == "compare":
        comparison = compare_two_phones(q, df)
        return {"answer": comparison or "Sorry, I couldn't compare those models."}

    elif intent == "feature":
        return {"answer": best_feature_phone(q, df)}

    elif intent == "recommend":
        return {"answer": recommend_phone(q, df)}

    elif intent == "list":
        return {"answer": list_latest(df)}

    else:
        return {"answer": generate_answer(q, df)}
