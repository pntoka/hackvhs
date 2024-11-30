import os
from dotenv import load_dotenv
from fastapi import FastAPI
from playwright.sync_api import sync_playwright
import pandas as pd
from tavily import TavilyClient
import asyncio

load_dotenv()

app = FastAPI()
tavily_client = TavilyClient(api_key=os.getenv('TAVILY_API_KEY'))

@app.post("/scrape")
async def start_scraping():
    data = []
    search_results = tavily_client.search(
        query="vaccines",
        search_depth="advanced",
        include_answer=True,
        max_results=20
    )
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        for result in search_results:
            try:
                page.goto(result['url'])
                content = page.content()
                data.append({
                    'url': result['url'],
                    'content': content,
                    'title': result['title']
                })
            except Exception as e:
                print(f"Error processing {result['url']}: {e}")
                
    df = pd.DataFrame(data)
    df.to_csv('vaccine_data.csv', index=False)
    return {"status": "success", "records": len(data)}