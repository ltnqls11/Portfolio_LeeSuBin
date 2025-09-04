# 이전 버전들은 주석으로 보관 (API Key 제거됨)

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import pandas as pd
from openai import OpenAI
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.post("/query")
async def query(request: Request):
    data = await request.json()
    question = data["question"]
    print("👉 사용자 질문:", question)
    
    prompt = f"""
    You are a helpful assistant that converts natural language to SQL.
    Table: sales(product TEXT, quantity INTEGER, date TEXT)
    Question: {question}
    Only return the SQL query without explanation.
    """
    
    sql = None
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        sql = response.choices[0].message.content.strip()
        print("💡 GPT가 생성한 SQL:", sql)
        
        conn = sqlite3.connect("sales.db")
        try:
            df = pd.read_sql_query(sql, conn)
            return {"result": df.to_dict(orient="records"), "sql": sql}
        finally:
            conn.close()
            
    except Exception as e:
        print("❌ 에러 발생:", e)
        return {"error": str(e), "sql": sql}