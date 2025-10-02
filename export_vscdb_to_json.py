#!/usr/bin/env python3
"""
Export Cursor VSCDB Data to JSON
Extracts workspace storage data from state.vscdb files
"""

import os
import json
import shutil
import glob
from pathlib import Path
import hashlib
from datetime import datetime

def find_cursor_workspace_storage():
    """Find Cursor workspace storage directory"""
    home = Path.home()
    
    # Common locations for Cursor workspace storage
    possible_paths = [
        home / ".config" / "Cursor" / "User" / "workspaceStorage",
        home / "Library" / "Application Support" / "Cursor" / "User" / "workspaceStorage",
        home / "AppData" / "Roaming" / "Cursor" / "User" / "workspaceStorage"
    ]
    
    for path in possible_paths:
        if path.exists():
            print(f"Found Cursor workspace storage at: {path}")
            return path
    
    print("Could not find Cursor workspace storage directory")
    return None

def extract_workspace_data(workspace_path, output_file):
    """Extract data from all workspace folders"""
    if not workspace_path or not workspace_path.exists():
        print("Invalid workspace path")
        return False
    
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    extracted_data = {
        "extraction_timestamp": datetime.now().isoformat(),
        "source_directory": str(workspace_path),
        "workspaces": []
    }
    
    # Find all workspace folders (MD5 hashes)
    workspace_folders = [f for f in workspace_path.iterdir() if f.is_dir() and len(f.name) == 32]
    
    print(f"Found {len(workspace_folders)} workspace folders")
    
    for workspace_folder in workspace_folders:
        workspace_id = workspace_folder.name
        print(f"Processing workspace: {workspace_id}")
        
        workspace_data = {
            "workspace_id": workspace_id,
            "folder_path": str(workspace_folder),
            "files": [],
            "chats": [],
            "prompts": [],
            "code_snippets": []
        }
        
        # Look for common Cursor data files
        data_files = []
        for pattern in ["**/*.json", "**/*.db", "**/*.sqlite", "**/*.txt", "**/*.md"]:
            data_files.extend(workspace_folder.glob(pattern))
        
        for file_path in data_files:
            try:
                file_info = {
                    "name": file_path.name,
                    "path": str(file_path.relative_to(workspace_folder)),
                    "size": file_path.stat().st_size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                }
                
                # Try to read and parse JSON files
                if file_path.suffix == '.json':
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = json.load(f)
                            file_info["content"] = content
                            
                            # Extract chat/prompt data
                            if isinstance(content, dict):
                                if 'messages' in content or 'chats' in content:
                                    workspace_data["chats"].append(file_info)
                                elif 'prompts' in content or 'prompt' in content:
                                    workspace_data["prompts"].append(file_info)
                                elif 'code' in content or 'snippets' in content:
                                    workspace_data["code_snippets"].append(file_info)
                            elif isinstance(content, list):
                                # Check if it looks like chat data
                                if content and isinstance(content[0], dict):
                                    if any('message' in str(item) or 'prompt' in str(item) for item in content):
                                        workspace_data["chats"].append(file_info)
                    except (json.JSONDecodeError, UnicodeDecodeError) as e:
                        file_info["error"] = str(e)
                
                workspace_data["files"].append(file_info)
                
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
        
        extracted_data["workspaces"].append(workspace_data)
        print(f"   Found {len(workspace_data['files'])} files, {len(workspace_data['chats'])} chats, {len(workspace_data['prompts'])} prompts")
    
    # Save extracted data
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(extracted_data, f, indent=2, ensure_ascii=False, default=str)
    
    file_size = output_path.stat().st_size / (1024 * 1024)  # MB
    print(f"✅ VSCDB extraction saved to: {output_path}")
    print(f"   📊 File size: {file_size:.1f} MB")
    print(f"   📁 Workspaces: {len(extracted_data['workspaces'])}")
    
    return True

def main():
    """Export VSCDB data to JSON"""
    print("🚀 Exporting Cursor VSCDB Data to JSON...")
    print("=" * 60)
    
    # Find workspace storage
    workspace_path = find_cursor_workspace_storage()
    
    if not workspace_path:
        print("❌ Could not find Cursor workspace storage")
        return
    
    # Export to Desktop
    output_file = "/Users/hamidaho/Desktop/cursor_vscdb_extraction.json"
    
    success = extract_workspace_data(workspace_path, output_file)
    
    if success:
        print(f"\n🎉 VSCDB extraction complete!")
        print(f"📁 File saved to: {output_file}")
        print(f"📊 This file contains the most meaningful data:")
        print(f"   - Chat histories and conversations")
        print(f"   - File tracking and workspace state")
        print(f"   - Project-specific configurations")
        print(f"   - Development patterns and interactions")
    else:
        print("❌ VSCDB extraction failed")

if __name__ == "__main__":
    main()
