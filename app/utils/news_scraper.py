import os
import requests
import sqlite3
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "news_database.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            url TEXT UNIQUE,
            content TEXT,
            fake_score REAL,
            bias_label TEXT,
            summary TEXT,
            created_at DATETIME
        )
    ''')
    conn.commit()
    conn.close()

def fetch_trending_news():
    api_key = os.getenv("NEWSAPI_KEY")
    if not api_key or api_key == "your_newsapi_key_here":
        print("NewsAPI key not configured. Skipping live scrape.")
        return
        
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            articles = response.json().get("articles", [])
            for art in articles[:10]:
                save_to_db(art)
    except Exception as e:
        print(f"NewsAPI Exception: {e}")

def save_to_db(article_data):
    init_db()
    title = article_data.get('title', '')
    url = article_data.get('url', '')
    content = article_data.get('content') or article_data.get('description', '')
    
    if not url or not title:
        return
        
    fake_score = 0.5
    bias_label = "CENTER"
    summary = content[:200] + "..." if content else ""
    
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            INSERT OR IGNORE INTO articles 
            (title, url, content, fake_score, bias_label, summary, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (title, url, content, fake_score, bias_label, summary, datetime.now()))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"DB Insert Error: {e}")

if __name__ == "__main__":
    fetch_trending_news()
