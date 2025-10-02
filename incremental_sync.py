#!/usr/bin/env python3
"""
Incremental Cursor Dataset Sync
Handles large datasets with incremental updates and efficient syncing
"""

import os
import sys
import json
import sqlite3
import hashlib
import subprocess
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
import argparse
import tempfile
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('incremental_sync.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class IncrementalSync:
    def __init__(self, 
                 source_dir: str = "/Users/hamidaho/Desktop/new_experiments",
                 hf_repo: str = "midah/cursor-extract",
                 batch_size: int = 10000):
        self.source_dir = Path(source_dir)
        self.hf_repo = hf_repo
        self.batch_size = batch_size
        self.state_file = Path("incremental_sync_state.json")
        self.last_sync_state = self.load_sync_state()
        
        # Database configurations
        self.databases = {
            "cursor_api_activity.db": {
                "path": self.source_dir / "cursor_api_analysis" / "cursor_api_activity.db",
                "primary_key": "id",
                "timestamp_column": "timestamp",
                "json_export": "cursor_activity_incremental.json",
                "max_records": 1000000  # Limit for incremental updates
            },
            "prompt_versions.db": {
                "path": self.source_dir / "prompt_versions" / "prompt_versions.db",
                "primary_key": "prompt_id",
                "timestamp_column": "timestamp",
                "json_export": "prompt_versions_incremental.json",
                "max_records": 50000
            }
        }

    def load_sync_state(self) -> Dict:
        """Load incremental sync state"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load sync state: {e}")
        return {}

    def save_sync_state(self, state: Dict):
        """Save incremental sync state"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save sync state: {e}")

    def get_database_max_id(self, db_path: Path, primary_key: str) -> int:
        """Get maximum ID from database"""
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute(f"SELECT MAX({primary_key}) FROM api_activity")
            result = cursor.fetchone()
            conn.close()
            return result[0] if result[0] is not None else 0
        except Exception as e:
            logger.error(f"Failed to get max ID from {db_path}: {e}")
            return 0

    def get_incremental_data(self, db_name: str, db_info: Dict) -> Dict:
        """Get incremental data from database"""
        try:
            db_path = db_info["path"]
            if not db_path.exists():
                logger.warning(f"Database not found: {db_path}")
                return {}
            
            primary_key = db_info["primary_key"]
            timestamp_column = db_info["timestamp_column"]
            
            # Get last synced ID
            last_id = self.last_sync_state.get(f"{db_name}_last_id", 0)
            
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Get new records since last sync
            query = f"""
            SELECT * FROM api_activity 
            WHERE {primary_key} > ? 
            ORDER BY {primary_key} 
            LIMIT ?
            """
            
            cursor.execute(query, (last_id, self.batch_size))
            rows = cursor.fetchall()
            
            # Get column names
            cursor.execute("PRAGMA table_info(api_activity)")
            columns = [column[1] for column in cursor.fetchall()]
            
            # Convert to dictionaries
            new_data = []
            max_id = last_id
            for row in rows:
                new_data.append(dict(zip(columns, row)))
                max_id = max(max_id, row[0])  # Assuming first column is ID
            
            conn.close()
            
            # Update sync state
            self.last_sync_state[f"{db_name}_last_id"] = max_id
            self.save_sync_state(self.last_sync_state)
            
            return {
                "database": db_name,
                "incremental": True,
                "last_synced_id": last_id,
                "new_max_id": max_id,
                "new_records": len(new_data),
                "export_timestamp": datetime.now().isoformat(),
                "data": new_data
            }
            
        except Exception as e:
            logger.error(f"Failed to get incremental data from {db_name}: {e}")
            return {}

    def create_incremental_export(self, db_name: str, db_info: Dict) -> bool:
        """Create incremental export file"""
        try:
            incremental_data = self.get_incremental_data(db_name, db_info)
            if not incremental_data:
                logger.info(f"No new data for {db_name}")
                return True
            
            # Save incremental export
            json_path = Path(db_info["json_export"])
            with open(json_path, 'w') as f:
                json.dump(incremental_data, f, indent=2, default=str)
            
            logger.info(f"Created incremental export: {json_path} ({incremental_data['new_records']} records)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create incremental export for {db_name}: {e}")
            return False

    def merge_incremental_data(self, db_name: str, db_info: Dict) -> bool:
        """Merge incremental data with existing full export"""
        try:
            incremental_file = Path(db_info["json_export"])
            full_export_file = Path(f"cursor_activity_FULL_export.json")
            
            if not incremental_file.exists():
                logger.warning(f"Incremental file not found: {incremental_file}")
                return False
            
            # Load incremental data
            with open(incremental_file, 'r') as f:
                incremental_data = json.load(f)
            
            if not incremental_data.get("data"):
                logger.info(f"No new data to merge for {db_name}")
                return True
            
            # Load or create full export
            if full_export_file.exists():
                with open(full_export_file, 'r') as f:
                    full_data = json.load(f)
            else:
                full_data = {
                    "database": db_name,
                    "export_timestamp": datetime.now().isoformat(),
                    "total_records": 0,
                    "incremental_updates": [],
                    "data": []
                }
            
            # Add incremental data
            full_data["data"].extend(incremental_data["data"])
            full_data["total_records"] = len(full_data["data"])
            full_data["incremental_updates"].append({
                "timestamp": incremental_data["export_timestamp"],
                "new_records": incremental_data["new_records"],
                "last_id": incremental_data["last_synced_id"],
                "max_id": incremental_data["new_max_id"]
            })
            full_data["export_timestamp"] = datetime.now().isoformat()
            
            # Save merged data
            with open(full_export_file, 'w') as f:
                json.dump(full_data, f, indent=2, default=str)
            
            logger.info(f"Merged {incremental_data['new_records']} new records into full export")
            return True
            
        except Exception as e:
            logger.error(f"Failed to merge incremental data for {db_name}: {e}")
            return False

    def sync_to_huggingface(self, changed_files: List[str]) -> bool:
        """Sync changed files to Hugging Face"""
        try:
            # Add files to git
            for file in changed_files:
                subprocess.run(["git", "add", file], check=True)
            
            # Check if there are changes
            result = subprocess.run(["git", "diff", "--cached", "--quiet"], 
                                  capture_output=True)
            if result.returncode == 0:
                logger.info("No changes to commit")
                return True
            
            # Commit changes
            commit_message = f"Incremental sync: {', '.join(changed_files)} - {datetime.now().isoformat()}"
            subprocess.run(["git", "commit", "-m", commit_message], check=True)
            
            # Push to Hugging Face
            subprocess.run(["git", "push", "origin", "master"], check=True)
            
            logger.info(f"Successfully synced incremental updates")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Git operation failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to sync to Hugging Face: {e}")
            return False

    def run_incremental_sync(self) -> bool:
        """Run incremental sync cycle"""
        logger.info("Starting incremental sync...")
        
        changed_files = []
        
        # Process each database
        for db_name, db_info in self.databases.items():
            if not db_info["path"].exists():
                continue
            
            # Create incremental export
            if self.create_incremental_export(db_name, db_info):
                changed_files.append(db_info["json_export"])
                
                # Merge with full export
                if self.merge_incremental_data(db_name, db_info):
                    changed_files.append("cursor_activity_FULL_export.json")
        
        if not changed_files:
            logger.info("No incremental changes detected")
            return True
        
        # Sync to Hugging Face
        success = self.sync_to_huggingface(changed_files)
        
        if success:
            logger.info("Incremental sync completed successfully")
        else:
            logger.error("Incremental sync failed")
        
        return success

def main():
    parser = argparse.ArgumentParser(description="Incremental Cursor dataset sync")
    parser.add_argument("--source-dir", default="/Users/hamidaho/Desktop/new_experiments",
                       help="Source directory containing Cursor data")
    parser.add_argument("--hf-repo", default="midah/cursor-extract",
                       help="Hugging Face repository name")
    parser.add_argument("--batch-size", type=int, default=10000,
                       help="Batch size for incremental updates")
    
    args = parser.parse_args()
    
    # Initialize incremental sync
    sync = IncrementalSync(
        source_dir=args.source_dir,
        hf_repo=args.hf_repo,
        batch_size=args.batch_size
    )
    
    # Run incremental sync
    success = sync.run_incremental_sync()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
