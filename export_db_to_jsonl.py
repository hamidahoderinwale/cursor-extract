#!/usr/bin/env python3
"""
Export Database to JSONL Format
Converts SQLite databases to JSONL (one JSON object per line) for efficient processing
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

def export_db_to_jsonl():
    """Export all cursor databases to JSONL format"""
    
    # Database paths
    db_paths = [
        "/Users/hamidaho/Desktop/new_experiments/cursor_api_analysis/cursor_api_activity.db",
        "/Users/hamidaho/Desktop/new_experiments/comprehensive_real_time_export/User/workspaceStorage/2de0e42c99d0e36f9f36ed120b2c242f/state.vscdb",
        "/Users/hamidaho/Desktop/new_experiments/comprehensive_real_time_export/User/workspaceStorage/8d9a76d52bdf58837313ae164c0115e0/state.vscdb",
        "/Users/hamidaho/Desktop/new_experiments/comprehensive_real_time_export/User/workspaceStorage/baf9dc865f7bf822abee54fdcdf2b5a6/state.vscdb"
    ]
    
    # Find all state databases
    state_dbs = list(Path("/Users/hamidaho/Desktop/new_experiments/comprehensive_real_time_export/User/workspaceStorage").glob("*/state.vscdb"))
    db_paths.extend([str(db) for db in state_dbs])
    
    print(f"📊 Found {len(db_paths)} databases to export")
    
    for db_path in db_paths:
        if not Path(db_path).exists():
            print(f"⚠️  Database not found: {db_path}")
            continue
            
        print(f"🔍 Processing: {Path(db_path).name}")
        
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            # Create output file
            output_file = Path(db_path).stem + ".jsonl"
            output_path = Path("/Users/hamidaho/Desktop/new_experiments") / output_file
            
            with open(output_path, 'w', encoding='utf-8') as f:
                for table in tables:
                    print(f"  📤 Exporting table: {table}")
                    
                    # Get table schema
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = [row[1] for row in cursor.fetchall()]
                    
                    # Export all rows
                    cursor.execute(f"SELECT * FROM {table}")
                    row_count = 0
                    
                    for row in cursor.fetchall():
                        # Convert row to dictionary
                        row_dict = dict(zip(columns, row))
                        
                        # Add metadata
                        record = {
                            "database": str(db_path),
                            "table": table,
                            "timestamp": datetime.now().isoformat(),
                            "data": row_dict
                        }
                        
                        # Write as JSONL
                        f.write(json.dumps(record, ensure_ascii=False) + '\n')
                        row_count += 1
                        
                        # Progress indicator for large tables
                        if row_count % 10000 == 0:
                            print(f"    Exported {row_count:,} records from {table}")
                    
                    print(f"  ✅ Exported {row_count:,} records from {table}")
            
            conn.close()
            print(f"✅ Completed: {output_path}")
            
        except Exception as e:
            print(f"❌ Error processing {db_path}: {e}")
    
    print(f"\n🎉 JSONL export completed!")
    print(f"📁 Output files:")
    for db_path in db_paths:
        if Path(db_path).exists():
            output_file = Path(db_path).stem + ".jsonl"
            output_path = Path("/Users/hamidaho/Desktop/new_experiments") / output_file
            if output_path.exists():
                size_mb = output_path.stat().st_size / (1024 * 1024)
                print(f"  - {output_file} ({size_mb:.1f} MB)")

def export_main_activity_db():
    """Export the main activity database to JSONL with better structure"""
    
    db_path = "/Users/hamidaho/Desktop/new_experiments/cursor_api_analysis/cursor_api_activity.db"
    
    if not Path(db_path).exists():
        print(f"❌ Database not found: {db_path}")
        return
    
    print(f"🔍 Exporting main activity database to JSONL...")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get table counts
    tables = ['api2_cursor_activities', 'other_cursor_activities', 'api3_cursor_activities', 'api_sessions']
    
    output_path = Path("/Users/hamidaho/Desktop/new_experiments/cursor_activity.jsonl")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for table in tables:
            print(f"📤 Exporting {table}...")
            
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            total_rows = cursor.fetchone()[0]
            print(f"  Total rows: {total_rows:,}")
            
            cursor.execute(f"SELECT * FROM {table}")
            row_count = 0
            
            for row in cursor.fetchall():
                record = {
                    "table": table,
                    "id": row['id'],
                    "timestamp": row['timestamp'],
                    "session_id": row['session_id'],
                    "endpoint": row['endpoint'],
                    "method": row['method'],
                    "status_code": row['status_code'],
                    "response_time": row['response_time'],
                    "error_message": row['error_message'],
                    "raw_log": row['raw_log']
                }
                
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
                row_count += 1
                
                if row_count % 50000 == 0:
                    print(f"    Exported {row_count:,}/{total_rows:,} records")
            
            print(f"  ✅ Exported {row_count:,} records from {table}")
    
    conn.close()
    
    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"✅ Main activity database exported: {output_path} ({size_mb:.1f} MB)")

if __name__ == "__main__":
    print("🚀 Starting database to JSONL export...")
    
    # Export main activity database
    export_main_activity_db()
    
    print("\n" + "="*50)
    print("📊 JSONL Export Summary:")
    print("="*50)
    
    # List all JSONL files created
    jsonl_files = list(Path("/Users/hamidaho/Desktop/new_experiments").glob("*.jsonl"))
    for file in jsonl_files:
        size_mb = file.stat().st_size / (1024 * 1024)
        print(f"📁 {file.name} ({size_mb:.1f} MB)")
    
    print(f"\n✅ Export completed! {len(jsonl_files)} JSONL files created.")
    print("💡 JSONL format allows for efficient streaming and processing of large datasets.")
