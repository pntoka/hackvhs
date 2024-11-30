import os
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import PlainTextResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from playwright.async_api import async_playwright  # Changed to async
import pandas as pd
from tavily import TavilyClient
import asyncio
from typing import Dict, List
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from scraper.query import VaccineQueryGenerator
from scraper.database import ScrapedDataDatabase
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

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize clients
tavily_client = TavilyClient(api_key=os.getenv('TAVILY_API_KEY'))
db = ScrapedDataDatabase()

# Status tracking
scraping_status = {
    "last_run": None,
    "total_records": 0,
    "errors": [],
    "is_running": False,
    "current_query": None
}

class ScrapingStats(BaseModel):
    last_run: str = None
    total_records: int = 0
    errors: List[str] = []
    is_running: bool = False
    current_query: str = None

@app.get("/")
async def root():
    return {"message": "Welcome to the Vaccine Sentiment Scraper API"}

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
async def start_scraping(num_queries: int = 1, search_depth: str = "advanced"):
    """Start the scraping process with multiple queries"""
    global scraping_status
    
    if scraping_status["is_running"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Scraping process already running"
        )
    
    try:
        scraping_status["is_running"] = True
        scraping_status["errors"] = []
        all_data = []
        query_generator = VaccineQueryGenerator()
        queries = query_generator.generate_query()
        # Create directory for results if it doesn't exist
        Path("results").mkdir(exist_ok=True)
        
        # Generate and process multiple queries
        for i in range(num_queries):
            query = queries[i]
            scraping_status["current_query"] = query
            logger.info(f"Processing query {i+1}/{num_queries}: {query}")
            
            try:
                search_results = tavily_client.search(
                    query=query,
                    search_depth=search_depth,
                    include_answer=True,
                    max_results=5
                )
                logger.info(f"Retrieved {len(search_results['results'])} results for query: {query}")  # Access 'results' key
                
                async with async_playwright() as p:
                    browser = await p.chromium.launch()
                    page = await browser.new_page()
                    
                    query_data = []
                    for result in search_results['results']:
                        try:
                            await page.goto(result['url'], timeout=30000)
                            content = await page.content()
                            entry_data = {
                                'url': result['url'],
                                'content': content,
                                'title': result['title'],
                                'query': query,
                                'timestamp': datetime.now().isoformat(),
                                'search_depth': search_depth,
                            }
                            query_data.append(entry_data)
                            logger.info(f"Successfully scraped: {result['url']}")
                        except Exception as e:
                            error_msg = f"Error processing {result['url']}: {str(e)}"
                            logger.error(error_msg)
                            scraping_status["errors"].append(error_msg)
                    
                    await browser.close()
                    
                    if query_data:
                        # Save to individual file
                        df = pd.DataFrame(query_data)
                        query_filename = "_".join(query.lower().split()[:3])
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        filename = f'results/vaccine_data_{query_filename}_{timestamp}.csv'
                        df.to_csv(filename, index=False)
                        logger.info(f"Saved results for query '{query}' to {filename}")
                        
                        # Add to master database
                        db.add_entries(query_data)
                        all_data.extend(query_data)
            
            except Exception as e:
                error_msg = f"Error with query '{query}': {str(e)}"
                logger.error(error_msg)
                scraping_status["errors"].append(error_msg)
                continue
        
        # Update status
        scraping_status.update({
            "last_run": datetime.now().isoformat(),
            "total_records": len(all_data),
            "is_running": False,
            "current_query": None
        })
        
        return {
            "status": "success",
            "total_records": len(all_data),
            "queries_processed": num_queries,
            "errors": scraping_status["errors"]
        }

    except Exception as e:
        error_msg = f"Scraping process failed: {str(e)}"
        logger.error(error_msg)
        scraping_status["is_running"] = False
        scraping_status["current_query"] = None
        scraping_status["errors"].append(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/results/{filename}")
async def get_results(filename: str):
    """Retrieve results from a specific scraping run"""
    try:
        df = pd.read_csv(f"results/{filename}")
        return json.loads(df.to_json(orient='records'))
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"File not found or error reading file: {str(e)}"
        )

@app.get("/database")
async def get_database():
    """Retrieve the entire database"""
    try:
        return json.loads(db.data.to_json(orient='records'))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error accessing database: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)