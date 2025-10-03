# Cursor Data Extraction Tools

Automated extraction and synchronization tools for Cursor IDE usage data.

## Project Aim

Extract, monitor, and automatically sync Cursor IDE data (API activity, prompts, workspace interactions) to keep datasets up-to-date in real-time.

## Core Tools

### **Database Export Scripts**
- **`export_vscdb_to_json.py`** - Export VSCDB workspace data to JSON
- **`export_detailed_cursor_data.py`** - Export detailed interaction data
- **`export_db_to_jsonl.py`** - Convert SQLite databases to JSONL format

### **Automated Sync System**
- **`auto_sync_datasets.py`** - Main sync script with file monitoring and Git LFS
- **`incremental_sync.py`** - Efficient incremental updates for large datasets
- **`webhook_sync.py`** - Real-time webhook-based syncing with file system monitoring
- **`sync_dashboard.py`** - Web dashboard for monitoring and control

### **Setup & Configuration**
- **`setup_auto_sync.sh`** - Automated setup for systemd service and cron jobs
- **`requirements.txt`** - Python dependencies for basic tools
- **`requirements_sync.txt`** - Python dependencies for sync tools

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements_sync.txt

# Export VSCDB data
python export_vscdb_to_json.py

# Export detailed data
python export_detailed_cursor_data.py

# Run one-time sync
python auto_sync_datasets.py --once

# Start continuous monitoring
python auto_sync_datasets.py

# Launch dashboard
python sync_dashboard.py
```

## Automated Setup

```bash
# Setup systemd service and cron jobs
chmod +x setup_auto_sync.sh
./setup_auto_sync.sh
```

## Monitoring

- **Dashboard**: `http://localhost:8080` - Web interface for sync status
- **Webhook API**: `http://localhost:5000/webhook/sync` - External triggers
- **Logs**: `auto_sync.log`, `incremental_sync.log`, `webhook_sync.log`

## Sync Methods

1. **File Monitoring** - Watches for database changes
2. **Incremental Updates** - Batched updates for large datasets  
3. **Webhook Triggers** - External API for manual syncs
4. **Scheduled Jobs** - Cron-based periodic syncing
5. **Systemd Service** - Background daemon process

## Datasets

The extracted data is available at:
- [Hugging Face Datasets](https://huggingface.co/datasets/midah/cursor-extract) [Private]

## License

This project is licensed under the MIT License - see the LICENSE file for details.
