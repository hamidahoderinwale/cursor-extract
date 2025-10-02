#!/usr/bin/env python3
"""
Export Detailed Cursor Data - File Searches, AI Prompts, Code Context
Extracts comprehensive cursor interaction data from state databases
"""

import sqlite3
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

def export_detailed_cursor_data():
    """Export detailed cursor interaction data including file searches, AI prompts, and code context"""
    
    # Find all state databases
    state_dbs = list(Path("/Users/hamidaho/Desktop/new_experiments/comprehensive_real_time_export/User/workspaceStorage").glob("*/state.vscdb"))
    
    print(f"📊 Found {len(state_dbs)} workspace state databases")
    
    export_data = {
        "metadata": {
            "export_time": datetime.now().isoformat(),
            "total_workspaces": len(state_dbs),
            "export_type": "DETAILED_CURSOR_INTERACTIONS"
        },
        "ai_prompts": [],
        "file_searches": [],
        "chat_interactions": [],
        "code_context": [],
        "workspace_data": []
    }
    
    for db_path in state_dbs:
        workspace_id = db_path.parent.name
        print(f"🔍 Processing workspace: {workspace_id}")
        
        try:
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get workspace info
            workspace_info = {
                "workspace_id": workspace_id,
                "database_path": str(db_path),
                "tables": []
            }
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            workspace_info["tables"] = tables
            
            # Extract AI prompts
            if 'ItemTable' in tables:
                cursor.execute("SELECT key, value FROM ItemTable WHERE key LIKE '%prompt%' OR key LIKE '%ai%' OR key LIKE '%chat%'")
                for row in cursor.fetchall():
                    try:
                        value_data = json.loads(row['value']) if row['value'] else None
                        export_data["ai_prompts"].append({
                            "workspace_id": workspace_id,
                            "key": row['key'],
                            "value": value_data,
                            "raw_value": row['value']
                        })
                    except:
                        export_data["ai_prompts"].append({
                            "workspace_id": workspace_id,
                            "key": row['key'],
                            "value": row['value'],
                            "raw_value": row['value']
                        })
            
            # Extract file search data
            if 'ItemTable' in tables:
                cursor.execute("SELECT key, value FROM ItemTable WHERE key LIKE '%search%' OR key LIKE '%file%'")
                for row in cursor.fetchall():
                    try:
                        value_data = json.loads(row['value']) if row['value'] else None
                        export_data["file_searches"].append({
                            "workspace_id": workspace_id,
                            "key": row['key'],
                            "value": value_data,
                            "raw_value": row['value']
                        })
                    except:
                        export_data["file_searches"].append({
                            "workspace_id": workspace_id,
                            "key": row['key'],
                            "value": row['value'],
                            "raw_value": row['value']
                        })
            
            # Extract code context data
            if 'ItemTable' in tables:
                cursor.execute("SELECT key, value FROM ItemTable WHERE key LIKE '%code%' OR key LIKE '%editor%' OR key LIKE '%context%'")
                for row in cursor.fetchall():
                    try:
                        value_data = json.loads(row['value']) if row['value'] else None
                        export_data["code_context"].append({
                            "workspace_id": workspace_id,
                            "key": row['key'],
                            "value": value_data,
                            "raw_value": row['value']
                        })
                    except:
                        export_data["code_context"].append({
                            "workspace_id": workspace_id,
                            "key": row['key'],
                            "value": row['value'],
                            "raw_value": row['value']
                        })
            
            # Extract all other data
            if 'ItemTable' in tables:
                cursor.execute("SELECT key, value FROM ItemTable")
                for row in cursor.fetchall():
                    try:
                        value_data = json.loads(row['value']) if row['value'] else None
                        export_data["chat_interactions"].append({
                            "workspace_id": workspace_id,
                            "key": row['key'],
                            "value": value_data,
                            "raw_value": row['value']
                        })
                    except:
                        export_data["chat_interactions"].append({
                            "workspace_id": workspace_id,
                            "key": row['key'],
                            "value": row['value'],
                            "raw_value": row['value']
                        })
            
            workspace_info["total_items"] = len(export_data["chat_interactions"])
            export_data["workspace_data"].append(workspace_info)
            
            conn.close()
            
        except Exception as e:
            print(f"⚠️  Error processing {workspace_id}: {e}")
    
    # Save to JSON file
    output_file = Path("/Users/hamidaho/Desktop/new_experiments/detailed_cursor_interactions.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Detailed export completed: {output_file}")
    print(f"📊 Export statistics:")
    print(f"  AI Prompts: {len(export_data['ai_prompts'])}")
    print(f"  File Searches: {len(export_data['file_searches'])}")
    print(f"  Code Context: {len(export_data['code_context'])}")
    print(f"  Total Interactions: {len(export_data['chat_interactions'])}")
    print(f"  Workspaces: {len(export_data['workspace_data'])}")
    
    return output_file

if __name__ == "__main__":
    export_detailed_cursor_data()
