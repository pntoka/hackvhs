# database.py
import pandas as pd
import logging
import os
from typing import List

logger = logging.getLogger(__name__)

class ScrapedDataDatabase:
    def __init__(self):
        self.data = pd.DataFrame(columns=[
            'url',
            'title',
            'content',
            'query',
            'timestamp',
            'search_depth',
            'perspective',
            'demographic'
        ])
        self.db_file = 'results/master_database.csv'
        self._load_or_create_db()

    def _load_or_create_db(self):
        try:
            if os.path.exists(self.db_file):
                self.data = pd.read_csv(self.db_file)
        except Exception as e:
            logger.error(f"Error loading database: {e}")

    def add_entries(self, entries: List[dict]):
        new_data = pd.DataFrame(entries)
        self.data = pd.concat([self.data, new_data], ignore_index=True)
        self._save_db()

    def _save_db(self):
        try:
            self.data.to_csv(self.db_file, index=False)
        except Exception as e:
            logger.error(f"Error saving database: {e}")