import os
import nest_asyncio
import pandas as pd
from pathlib import Path
from datetime import datetime
import json
from dotenv import load_dotenv
from llama_parse import LlamaParse
from llama_index.readers.web import SimpleWebPageReader

load_dotenv()

def scrape_url(url):
    try:
        # Initialize LlamaParse
        parser = LlamaParse(
            api_key=os.getenv('LLAMACLOUD_API_KEY'),
            result_type="text",
            fast_mode=True,
            verbose=True,
            language="en"
        )
        # Use LlamaIndex web reader to get clean text
        documents = SimpleWebPageReader(html_to_text=True).load_data([url])
        if documents:
            return documents[0].text
        return ""
    except Exception as e:
        # logger.error(f"Error cleaning content from {url}: {str(e)}")
        return ""

if __name__ == '__main__':
    results_dir = Path('results')
    csv_files = list(results_dir.glob('*.csv'))

    master_data = dict()

    # Process each CSV file
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file)
            # Iterate through each row in the DataFrame
            for index, row in df.iterrows():
                entry = {
                    'topic': row['topic'],
                    'query': row['query'],
                    'title': row['title'],
                    'url': row['url'],
                    'content': scrape_url(row['url']) if "facebook" in row['url'] else "",
                    'scrape_date': row['timestamp'],
                    'search_depth': row['search_depth'],
                    'timestamp': datetime.now().isoformat()  # Convert datetime to string
                }
                # Use URL as key to avoid overwriting
                master_data[row['url']] = entry
                    
                # Save after each new entry
                with open('sentiment_data.json', 'w', encoding='utf-8') as f:
                    json.dump(master_data, f, indent=4, ensure_ascii=False)
                
        except Exception as e:
            print(f'Error processing {csv_file}: {e}')