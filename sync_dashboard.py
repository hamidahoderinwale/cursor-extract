#!/usr/bin/env python3
"""
Cursor Dataset Sync Dashboard
Web-based monitoring and control interface for automated syncing
"""

import os
import sys
import json
import time
import sqlite3
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
import argparse
from flask import Flask, render_template_string, jsonify, request

# Dashboard HTML template
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Cursor Dataset Sync Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .card { background: white; padding: 20px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .status { padding: 10px; border-radius: 4px; margin: 10px 0; }
        .status.success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .status.error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .status.warning { background: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }
        .metric { display: inline-block; margin: 10px 20px 10px 0; }
        .metric-value { font-size: 24px; font-weight: bold; color: #2c3e50; }
        .metric-label { font-size: 14px; color: #7f8c8d; }
        .button { background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; margin: 5px; }
        .button:hover { background: #2980b9; }
        .button.danger { background: #e74c3c; }
        .button.danger:hover { background: #c0392b; }
        .log { background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 4px; font-family: monospace; font-size: 12px; max-height: 300px; overflow-y: auto; }
        table { width: 100%; border-collapse: collapse; margin: 10px 0; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f8f9fa; font-weight: bold; }
        .progress-bar { width: 100%; background: #ecf0f1; border-radius: 4px; overflow: hidden; }
        .progress-fill { height: 20px; background: #3498db; transition: width 0.3s ease; }
    </style>
    <script>
        function refreshData() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    updateDashboard(data);
                });
        }
        
        function updateDashboard(data) {
            // Update sync status
            const syncStatus = document.getElementById('sync-status');
            syncStatus.className = 'status ' + (data.sync_running ? 'success' : 'error');
            syncStatus.textContent = data.sync_running ? 'Sync Running' : 'Sync Stopped';
            
            // Update metrics
            document.getElementById('total-records').textContent = data.total_records.toLocaleString();
            document.getElementById('last-sync').textContent = data.last_sync || 'Never';
            document.getElementById('queue-size').textContent = data.queue_size || 0;
            
            // Update database status
            const dbStatus = document.getElementById('db-status');
            dbStatus.innerHTML = data.databases.map(db => 
                `<div class="status ${db.status}">${db.name}: ${db.records.toLocaleString()} records (${db.size})</div>`
            ).join('');
            
            // Update recent activity
            const activity = document.getElementById('recent-activity');
            activity.innerHTML = data.recent_activity.map(activity => 
                `<div>${activity.timestamp}: ${activity.message}</div>`
            ).join('');
        }
        
        function triggerSync() {
            fetch('/api/trigger-sync', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    alert('Sync triggered: ' + data.message);
                    refreshData();
                });
        }
        
        function stopSync() {
            fetch('/api/stop-sync', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    alert('Sync stopped: ' + data.message);
                    refreshData();
                });
        }
        
        // Auto-refresh every 30 seconds
        setInterval(refreshData, 30000);
        
        // Initial load
        refreshData();
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Cursor Dataset Sync Dashboard</h1>
            <p>Automated monitoring and control for Cursor data synchronization</p>
        </div>
        
        <div class="card">
            <h2>📊 Sync Status</h2>
            <div id="sync-status" class="status">Loading...</div>
            <div class="metric">
                <div class="metric-value" id="total-records">0</div>
                <div class="metric-label">Total Records</div>
            </div>
            <div class="metric">
                <div class="metric-value" id="last-sync">Never</div>
                <div class="metric-label">Last Sync</div>
            </div>
            <div class="metric">
                <div class="metric-value" id="queue-size">0</div>
                <div class="metric-label">Queue Size</div>
            </div>
            <button class="button" onclick="triggerSync()">🔄 Trigger Sync</button>
            <button class="button danger" onclick="stopSync()">⏹️ Stop Sync</button>
        </div>
        
        <div class="card">
            <h2>🗄️ Database Status</h2>
            <div id="db-status">Loading...</div>
        </div>
        
        <div class="card">
            <h2>📈 Recent Activity</h2>
            <div id="recent-activity" class="log">Loading...</div>
        </div>
        
        <div class="card">
            <h2>⚙️ Configuration</h2>
            <table>
                <tr><th>Setting</th><th>Value</th></tr>
                <tr><td>Source Directory</td><td>/Users/hamidaho/Desktop/new_experiments</td></tr>
                <tr><td>HF Repository</td><td>midah/cursor-extract</td></tr>
                <tr><td>Sync Interval</td><td>5 minutes</td></tr>
                <tr><td>Webhook Port</td><td>5000</td></tr>
            </table>
        </div>
    </div>
</body>
</html>
"""

class SyncDashboard:
    def __init__(self, 
                 source_dir: str = "/Users/hamidaho/Desktop/new_experiments",
                 hf_repo: str = "midah/cursor-extract",
                 port: int = 8080):
        self.source_dir = Path(source_dir)
        self.hf_repo = hf_repo
        self.port = port
        self.app = Flask(__name__)
        self.setup_routes()
    
    def get_database_info(self) -> List[Dict]:
        """Get database information"""
        databases = []
        
        db_configs = [
            ("cursor_api_activity.db", self.source_dir / "cursor_api_analysis" / "cursor_api_activity.db"),
            ("prompt_versions.db", self.source_dir / "prompt_versions" / "prompt_versions.db"),
            ("enhanced_prompt_versions.db", self.source_dir / "enhanced_cursor_export" / "prompt_versions.db")
        ]
        
        for name, path in db_configs:
            if path.exists():
                try:
                    # Get file size
                    size = path.stat().st_size
                    size_str = self.format_size(size)
                    
                    # Get record count
                    conn = sqlite3.connect(str(path))
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM api_activity")
                    records = cursor.fetchone()[0]
                    conn.close()
                    
                    databases.append({
                        "name": name,
                        "path": str(path),
                        "size": size_str,
                        "records": records,
                        "status": "success"
                    })
                except Exception as e:
                    databases.append({
                        "name": name,
                        "path": str(path),
                        "size": "Unknown",
                        "records": 0,
                        "status": "error"
                    })
            else:
                databases.append({
                    "name": name,
                    "path": str(path),
                    "size": "Not Found",
                    "records": 0,
                    "status": "warning"
                })
        
        return databases
    
    def format_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def get_sync_status(self) -> Dict:
        """Get current sync status"""
        try:
            # Check if sync processes are running
            result = subprocess.run(["pgrep", "-f", "auto_sync_datasets.py"], 
                                  capture_output=True, text=True)
            sync_running = result.returncode == 0
            
            # Get total records
            total_records = 0
            for db_info in self.get_database_info():
                total_records += db_info["records"]
            
            # Get last sync time (from git log)
            try:
                result = subprocess.run(["git", "log", "-1", "--format=%cd", "--date=iso"], 
                                      capture_output=True, text=True, cwd=".")
                last_sync = result.stdout.strip() if result.returncode == 0 else "Unknown"
            except:
                last_sync = "Unknown"
            
            return {
                "sync_running": sync_running,
                "total_records": total_records,
                "last_sync": last_sync,
                "queue_size": 0  # Would need to implement queue monitoring
            }
        except Exception as e:
            return {
                "sync_running": False,
                "total_records": 0,
                "last_sync": "Error",
                "queue_size": 0
            }
    
    def get_recent_activity(self) -> List[Dict]:
        """Get recent sync activity"""
        activities = []
        
        try:
            # Get recent git commits
            result = subprocess.run(["git", "log", "--oneline", "-10"], 
                                  capture_output=True, text=True, cwd=".")
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        activities.append({
                            "timestamp": datetime.now().strftime("%H:%M:%S"),
                            "message": line
                        })
        except:
            pass
        
        return activities
    
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def dashboard():
            return render_template_string(DASHBOARD_TEMPLATE)
        
        @self.app.route('/api/status')
        def api_status():
            return jsonify({
                **self.get_sync_status(),
                "databases": self.get_database_info(),
                "recent_activity": self.get_recent_activity()
            })
        
        @self.app.route('/api/trigger-sync', methods=['POST'])
        def api_trigger_sync():
            try:
                # Trigger sync by running the sync script
                result = subprocess.run(["python3", "auto_sync_datasets.py", "--once"], 
                                      capture_output=True, text=True, cwd=".")
                return jsonify({
                    "status": "success",
                    "message": "Sync triggered successfully"
                })
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "message": str(e)
                }), 500
        
        @self.app.route('/api/stop-sync', methods=['POST'])
        def api_stop_sync():
            try:
                # Stop sync processes
                subprocess.run(["pkill", "-f", "auto_sync_datasets.py"])
                return jsonify({
                    "status": "success",
                    "message": "Sync stopped successfully"
                })
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "message": str(e)
                }), 500
    
    def run(self):
        """Run the dashboard"""
        print(f"🚀 Starting Cursor Dataset Sync Dashboard on port {self.port}")
        print(f"📊 Dashboard URL: http://localhost:{self.port}")
        self.app.run(host='0.0.0.0', port=self.port, debug=False)

def main():
    parser = argparse.ArgumentParser(description="Cursor Dataset Sync Dashboard")
    parser.add_argument("--source-dir", default="/Users/hamidaho/Desktop/new_experiments",
                       help="Source directory containing Cursor data")
    parser.add_argument("--hf-repo", default="midah/cursor-extract",
                       help="Hugging Face repository name")
    parser.add_argument("--port", type=int, default=8080,
                       help="Dashboard port")
    
    args = parser.parse_args()
    
    # Initialize dashboard
    dashboard = SyncDashboard(
        source_dir=args.source_dir,
        hf_repo=args.hf_repo,
        port=args.port
    )
    
    # Run dashboard
    dashboard.run()

if __name__ == "__main__":
    main()
