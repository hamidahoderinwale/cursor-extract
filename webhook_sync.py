#!/usr/bin/env python3
"""
Webhook-based Cursor Dataset Sync
Real-time syncing using file system monitoring and webhooks
"""

import os
import sys
import json
import time
import logging
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Callable
import argparse
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import requests
from flask import Flask, request, jsonify

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('webhook_sync.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CursorFileHandler(FileSystemEventHandler):
    """File system event handler for Cursor data changes"""
    
    def __init__(self, sync_callback: Callable):
        self.sync_callback = sync_callback
        self.last_modified = {}
        self.debounce_time = 5  # seconds
        
    def on_modified(self, event):
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        current_time = time.time()
        
        # Debounce rapid file changes
        if file_path in self.last_modified:
            if current_time - self.last_modified[file_path] < self.debounce_time:
                return
        
        self.last_modified[file_path] = current_time
        
        # Check if it's a monitored file
        if self.is_monitored_file(file_path):
            logger.info(f"File changed: {file_path}")
            self.sync_callback(str(file_path))
    
    def is_monitored_file(self, file_path: Path) -> bool:
        """Check if file should be monitored"""
        monitored_patterns = [
            "cursor_api_activity.db",
            "prompt_versions.db",
            "cursor_activity_export.json",
            "development_timeline.json"
        ]
        
        return any(pattern in str(file_path) for pattern in monitored_patterns)

class WebhookSync:
    def __init__(self, 
                 source_dir: str = "/Users/hamidaho/Desktop/new_experiments",
                 hf_repo: str = "midah/cursor-extract",
                 webhook_port: int = 5000):
        self.source_dir = Path(source_dir)
        self.hf_repo = hf_repo
        self.webhook_port = webhook_port
        self.observer = None
        self.sync_queue = []
        self.sync_lock = threading.Lock()
        
        # Start background sync thread
        self.sync_thread = threading.Thread(target=self._sync_worker, daemon=True)
        self.sync_thread.start()
    
    def _sync_worker(self):
        """Background worker for processing sync queue"""
        while True:
            try:
                if self.sync_queue:
                    with self.sync_lock:
                        file_path = self.sync_queue.pop(0)
                    
                    self.sync_file(file_path)
                else:
                    time.sleep(1)
            except Exception as e:
                logger.error(f"Sync worker error: {e}")
                time.sleep(5)
    
    def queue_sync(self, file_path: str):
        """Queue file for syncing"""
        with self.sync_lock:
            if file_path not in self.sync_queue:
                self.sync_queue.append(file_path)
                logger.info(f"Queued for sync: {file_path}")
    
    def sync_file(self, file_path: str):
        """Sync individual file to Hugging Face"""
        try:
            file_path = Path(file_path)
            
            # Copy file to current directory
            dest_name = file_path.name
            if file_path.exists():
                import shutil
                shutil.copy2(file_path, dest_name)
                
                # Add to git
                import subprocess
                subprocess.run(["git", "add", dest_name], check=True)
                
                # Commit and push
                commit_message = f"Auto-sync: {dest_name} - {datetime.now().isoformat()}"
                subprocess.run(["git", "commit", "-m", commit_message], check=True)
                subprocess.run(["git", "push", "origin", "master"], check=True)
                
                logger.info(f"Successfully synced: {dest_name}")
            else:
                logger.warning(f"File not found: {file_path}")
                
        except Exception as e:
            logger.error(f"Failed to sync {file_path}: {e}")
    
    def start_file_monitoring(self):
        """Start file system monitoring"""
        event_handler = CursorFileHandler(self.queue_sync)
        self.observer = Observer()
        
        # Monitor source directory
        self.observer.schedule(event_handler, str(self.source_dir), recursive=True)
        
        # Monitor specific subdirectories
        subdirs = [
            "cursor_api_analysis",
            "prompt_versions", 
            "enhanced_cursor_export"
        ]
        
        for subdir in subdirs:
            subdir_path = self.source_dir / subdir
            if subdir_path.exists():
                self.observer.schedule(event_handler, str(subdir_path), recursive=True)
        
        self.observer.start()
        logger.info(f"Started file monitoring on {self.source_dir}")
    
    def stop_file_monitoring(self):
        """Stop file system monitoring"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            logger.info("Stopped file monitoring")
    
    def create_webhook_app(self):
        """Create Flask webhook app for external triggers"""
        app = Flask(__name__)
        
        @app.route('/webhook/sync', methods=['POST'])
        def webhook_sync():
            try:
                data = request.get_json()
                file_path = data.get('file_path')
                
                if file_path:
                    self.queue_sync(file_path)
                    return jsonify({"status": "queued", "file": file_path})
                else:
                    return jsonify({"error": "file_path required"}), 400
                    
            except Exception as e:
                logger.error(f"Webhook error: {e}")
                return jsonify({"error": str(e)}), 500
        
        @app.route('/webhook/status', methods=['GET'])
        def webhook_status():
            return jsonify({
                "status": "running",
                "queue_size": len(self.sync_queue),
                "monitoring": self.observer.is_alive() if self.observer else False
            })
        
        @app.route('/webhook/trigger-sync', methods=['POST'])
        def trigger_full_sync():
            try:
                # Trigger sync of all monitored files
                monitored_files = [
                    self.source_dir / "cursor_api_analysis" / "cursor_api_activity.db",
                    self.source_dir / "prompt_versions" / "prompt_versions.db",
                    self.source_dir / "enhanced_cursor_export" / "prompt_versions.db",
                    self.source_dir / "cursor_activity_export.json",
                    self.source_dir / "development_timeline.json"
                ]
                
                for file_path in monitored_files:
                    if file_path.exists():
                        self.queue_sync(str(file_path))
                
                return jsonify({"status": "triggered", "files": len(monitored_files)})
                
            except Exception as e:
                logger.error(f"Trigger sync error: {e}")
                return jsonify({"error": str(e)}), 500
        
        return app
    
    def run_webhook_server(self):
        """Run webhook server"""
        app = self.create_webhook_app()
        logger.info(f"Starting webhook server on port {self.webhook_port}")
        app.run(host='0.0.0.0', port=self.webhook_port, debug=False)

def main():
    parser = argparse.ArgumentParser(description="Webhook-based Cursor dataset sync")
    parser.add_argument("--source-dir", default="/Users/hamidaho/Desktop/new_experiments",
                       help="Source directory containing Cursor data")
    parser.add_argument("--hf-repo", default="midah/cursor-extract",
                       help="Hugging Face repository name")
    parser.add_argument("--webhook-port", type=int, default=5000,
                       help="Webhook server port")
    parser.add_argument("--monitor-only", action="store_true",
                       help="Only run file monitoring, no webhook server")
    parser.add_argument("--webhook-only", action="store_true",
                       help="Only run webhook server, no file monitoring")
    
    args = parser.parse_args()
    
    # Initialize webhook sync
    sync = WebhookSync(
        source_dir=args.source_dir,
        hf_repo=args.hf_repo,
        webhook_port=args.webhook_port
    )
    
    try:
        if not args.webhook_only:
            # Start file monitoring
            sync.start_file_monitoring()
        
        if not args.monitor_only:
            # Start webhook server
            sync.run_webhook_server()
        else:
            # Keep monitoring running
            while True:
                time.sleep(1)
                
    except KeyboardInterrupt:
        logger.info("Stopping webhook sync...")
    finally:
        sync.stop_file_monitoring()

if __name__ == "__main__":
    main()
