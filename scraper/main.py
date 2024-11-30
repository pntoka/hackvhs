# main.py
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status
from playwright.sync_api import sync_playwright
import pandas as pd
from tavily import TavilyClient
import asyncio
from typing import Dict, List
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import json

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = FastAPI(title="Vaccine Sentiment Scraper", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Tavily client
tavily_client = TavilyClient(api_key=os.getenv('TAVILY_API_KEY'))

# Status tracking
scraping_status = {
    "last_run": None,
    "total_records": 0,
    "errors": [],
    "is_running": False
}

class ScrapingStats(BaseModel):
    last_run: str = None
    total_records: int = 0
    errors: List[str] = []
    is_running: bool = False

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/stats")
async def get_stats() -> ScrapingStats:
    """Get current scraping statistics"""
    return scraping_status

@app.post("/scrape")
async def start_scraping():
    """Start the scraping process"""
    global scraping_status
    
    if scraping_status["is_running"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Scraping process already running"
        )
    
    try:
        scraping_status["is_running"] = True
        scraping_status["errors"] = []
        data = []
        
        logger.info("Starting scraping process")
        
        # Tavily search
        try:
            search_results = tavily_client.search(
                query="vaccination",
                search_depth="advanced",
                include_answer=True,
                max_results=20
            )
            logger.info(f"Retrieved {len(search_results)} results from Tavily")
        except Exception as e:
            error_msg = f"Tavily API error: {str(e)}"
            logger.error(error_msg)
            scraping_status["errors"].append(error_msg)
            raise HTTPException(status_code=500, detail=error_msg)

        # Playwright scraping
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            
            for result in search_results:
                try:
                    page.goto(result['url'], timeout=30000)
                    content = page.content()
                    data.append({
                        'url': result['url'],
                        'content': content,
                        'title': result['title'],
                        'timestamp': datetime.now().isoformat()
                    })
                    logger.info(f"Successfully scraped: {result['url']}")
                except Exception as e:
                    error_msg = f"Error processing {result['url']}: {str(e)}"
                    logger.error(error_msg)
                    scraping_status["errors"].append(error_msg)

        # Save results
        df = pd.DataFrame(data)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'vaccine_data_{timestamp}.csv'
        df.to_csv(filename, index=False)
        
        # Update status
        scraping_status.update({
            "last_run": datetime.now().isoformat(),
            "total_records": len(data),
            "is_running": False
        })
        
        logger.info(f"Scraping completed. Saved {len(data)} records to {filename}")
        
        return {
            "status": "success",
            "records": len(data),
            "filename": filename,
            "errors": scraping_status["errors"]
        }

    except Exception as e:
        error_msg = f"Scraping process failed: {str(e)}"
        logger.error(error_msg)
        scraping_status["is_running"] = False
        scraping_status["errors"].append(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/results/{filename}")
async def get_results(filename: str):
    """Retrieve results from a specific scraping run"""
    try:
        df = pd.read_csv(filename)
        return json.loads(df.to_json(orient='records'))
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"File not found or error reading file: {str(e)}"
        )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Global error: {str(exc)}")
    return {
        "error": str(exc),
        "status": "failed",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)