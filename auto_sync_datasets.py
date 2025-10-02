#!/usr/bin/env python3
"""
Automated Cursor Dataset Sync to Hugging Face
Monitors database changes and automatically syncs to HF dataset
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
from typing import Dict, List, Optional, Tuple
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_sync.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CursorDatasetSync:
    def __init__(self, 
                 source_dir: str = "/Users/hamidaho/Desktop/new_experiments",
                 hf_repo: str = "midah/cursor-extract",
                 sync_interval: int = 300):  # 5 minutes
        self.source_dir = Path(source_dir)
        self.hf_repo = hf_repo
        self.sync_interval = sync_interval
        self.state_file = Path("sync_state.json")
        self.last_sync_state = self.load_sync_state()
        
        # Database files to monitor
        self.databases = {
            "cursor_api_activity.db": {
                "path": self.source_dir / "cursor_api_analysis" / "cursor_api_activity.db",
                "json_export": "cursor_activity_FULL_export.json",
                "sample_export": "cursor_activity_export.json"
            },
            "prompt_versions.db": {
                "path": self.source_dir / "prompt_versions" / "prompt_versions.db",
                "json_export": "prompt_versions_export.json"
            },
            "enhanced_prompt_versions.db": {
                "path": self.source_dir / "enhanced_cursor_export" / "prompt_versions.db",
                "json_export": "enhanced_prompt_versions_export.json"
            }
        }
        
        # JSON exports to monitor
        self.json_exports = [
            "cursor_activity_FULL_export.json",
            "cursor_activity_export.json",
            "development_timeline.json"
        ]

    def load_sync_state(self) -> Dict:
        """Load last sync state from file"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load sync state: {e}")
        return {}

    def save_sync_state(self, state: Dict):
        """Save current sync state to file"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save sync state: {e}")

    def get_file_hash(self, file_path: Path) -> Optional[str]:
        """Get MD5 hash of file for change detection"""
        if not file_path.exists():
            return None
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.error(f"Failed to hash {file_path}: {e}")
            return None

    def get_database_stats(self, db_path: Path) -> Dict:
        """Get database statistics for change detection"""
        if not db_path.exists():
            return {}
        
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Get table names and row counts
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            stats = {}
            for (table_name,) in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                stats[table_name] = count
            
            conn.close()
            return stats
        except Exception as e:
            logger.error(f"Failed to get database stats for {db_path}: {e}")
            return {}

    def check_for_changes(self) -> List[str]:
        """Check for changes in monitored files"""
        changed_files = []
        current_state = {}
        
        # Check database files
        for db_name, db_info in self.databases.items():
            db_path = db_info["path"]
            if db_path.exists():
                # Check file modification time and size
                stat = db_path.stat()
                current_state[db_name] = {
                    "mtime": stat.st_mtime,
                    "size": stat.size,
                    "hash": self.get_file_hash(db_path),
                    "db_stats": self.get_database_stats(db_path)
                }
                
                # Compare with last known state
                if db_name in self.last_sync_state:
                    last_state = self.last_sync_state[db_name]
                    if (current_state[db_name]["mtime"] > last_state.get("mtime", 0) or
                        current_state[db_name]["size"] != last_state.get("size", 0) or
                        current_state[db_name]["hash"] != last_state.get("hash", "")):
                        changed_files.append(db_name)
                        logger.info(f"Database changed: {db_name}")
                else:
                    changed_files.append(db_name)
                    logger.info(f"New database detected: {db_name}")
        
        # Check JSON export files
        for json_file in self.json_exports:
            json_path = self.source_dir / json_file
            if json_path.exists():
                stat = json_path.stat()
                current_state[json_file] = {
                    "mtime": stat.st_mtime,
                    "size": stat.size,
                    "hash": self.get_file_hash(json_path)
                }
                
                if json_file in self.last_sync_state:
                    last_state = self.last_sync_state[json_file]
                    if (current_state[json_file]["mtime"] > last_state.get("mtime", 0) or
                        current_state[json_file]["size"] != last_state.get("size", 0) or
                        current_state[json_file]["hash"] != last_state.get("hash", "")):
                        changed_files.append(json_file)
                        logger.info(f"JSON export changed: {json_file}")
                else:
                    changed_files.append(json_file)
                    logger.info(f"New JSON export detected: {json_file}")
        
        # Update sync state
        self.last_sync_state.update(current_state)
        self.save_sync_state(self.last_sync_state)
        
        return changed_files

    def export_database_to_json(self, db_name: str, db_info: Dict) -> bool:
        """Export database to JSON format"""
        try:
            db_path = db_info["path"]
            if not db_path.exists():
                logger.warning(f"Database not found: {db_path}")
                return False
            
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            export_data = {
                "database": db_name,
                "export_timestamp": datetime.now().isoformat(),
                "tables": {}
            }
            
            for (table_name,) in tables:
                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()
                
                # Get column names
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = [column[1] for column in cursor.fetchall()]
                
                # Convert rows to dictionaries
                table_data = []
                for row in rows:
                    table_data.append(dict(zip(columns, row)))
                
                export_data["tables"][table_name] = {
                    "columns": columns,
                    "row_count": len(table_data),
                    "data": table_data
                }
            
            conn.close()
            
            # Save JSON export
            json_path = Path(db_info.get("json_export", f"{db_name}_export.json"))
            with open(json_path, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            logger.info(f"Exported {db_name} to {json_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export {db_name}: {e}")
            return False

    def copy_file_to_repo(self, source_path: Path, dest_name: str) -> bool:
        """Copy file to local repo directory"""
        try:
            if not source_path.exists():
                logger.warning(f"Source file not found: {source_path}")
                return False
            
            # Copy file to current directory
            dest_path = Path(dest_name)
            subprocess.run(["cp", str(source_path), str(dest_path)], check=True)
            logger.info(f"Copied {source_path} to {dest_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to copy {source_path}: {e}")
            return False

    def sync_to_huggingface(self, changed_files: List[str]) -> bool:
        """Sync changed files to Hugging Face"""
        try:
            # Add changed files to git
            for file in changed_files:
                if file in self.databases:
                    # Copy database file
                    db_info = self.databases[file]
                    if not self.copy_file_to_repo(db_info["path"], file):
                        continue
                    
                    # Export to JSON if needed
                    if "json_export" in db_info:
                        self.export_database_to_json(file, db_info)
                        subprocess.run(["git", "add", db_info["json_export"]], check=True)
                    
                    subprocess.run(["git", "add", file], check=True)
                
                elif file in self.json_exports:
                    # Copy JSON export
                    source_path = self.source_dir / file
                    if self.copy_file_to_repo(source_path, file):
                        subprocess.run(["git", "add", file], check=True)
            
            # Check if there are changes to commit
            result = subprocess.run(["git", "diff", "--cached", "--quiet"], 
                                  capture_output=True)
            if result.returncode == 0:
                logger.info("No changes to commit")
                return True
            
            # Commit changes
            commit_message = f"Auto-sync: Update {', '.join(changed_files)} - {datetime.now().isoformat()}"
            subprocess.run(["git", "commit", "-m", commit_message], check=True)
            
            # Push to Hugging Face
            subprocess.run(["git", "push", "origin", "master"], check=True)
            
            logger.info(f"Successfully synced {len(changed_files)} files to Hugging Face")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Git operation failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to sync to Hugging Face: {e}")
            return False

    def run_sync_cycle(self) -> bool:
        """Run one sync cycle"""
        logger.info("Starting sync cycle...")
        
        # Check for changes
        changed_files = self.check_for_changes()
        
        if not changed_files:
            logger.info("No changes detected")
            return True
        
        logger.info(f"Changes detected in: {changed_files}")
        
        # Sync to Hugging Face
        success = self.sync_to_huggingface(changed_files)
        
        if success:
            logger.info("Sync cycle completed successfully")
        else:
            logger.error("Sync cycle failed")
        
        return success

    def run_continuous(self):
        """Run continuous monitoring and syncing"""
        logger.info(f"Starting continuous sync (interval: {self.sync_interval}s)")
        
        try:
            while True:
                self.run_sync_cycle()
                time.sleep(self.sync_interval)
        except KeyboardInterrupt:
            logger.info("Stopping continuous sync...")
        except Exception as e:
            logger.error(f"Continuous sync failed: {e}")

    def run_once(self):
        """Run sync once and exit"""
        return self.run_sync_cycle()

def main():
    parser = argparse.ArgumentParser(description="Auto-sync Cursor datasets to Hugging Face")
    parser.add_argument("--source-dir", default="/Users/hamidaho/Desktop/new_experiments",
                       help="Source directory containing Cursor data")
    parser.add_argument("--hf-repo", default="midah/cursor-extract",
                       help="Hugging Face repository name")
    parser.add_argument("--interval", type=int, default=300,
                       help="Sync interval in seconds (default: 300)")
    parser.add_argument("--once", action="store_true",
                       help="Run sync once and exit")
    parser.add_argument("--daemon", action="store_true",
                       help="Run as daemon process")
    
    args = parser.parse_args()
    
    # Initialize sync
    sync = CursorDatasetSync(
        source_dir=args.source_dir,
        hf_repo=args.hf_repo,
        sync_interval=args.interval
    )
    
    if args.daemon:
        # Run as daemon
        import daemon
        with daemon.DaemonContext():
            sync.run_continuous()
    elif args.once:
        # Run once
        success = sync.run_once()
        sys.exit(0 if success else 1)
    else:
        # Run continuous
        sync.run_continuous()

if __name__ == "__main__":
    main()
