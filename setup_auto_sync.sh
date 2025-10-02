#!/bin/bash
"""
Setup script for automated Cursor dataset syncing
Creates systemd service and cron jobs for continuous syncing
"""

set -e

# Configuration
SCRIPT_DIR="/Users/hamidaho/Desktop/cursor-datasets"
SERVICE_NAME="cursor-dataset-sync"
USER="hamidaho"
PYTHON_PATH="/usr/bin/python3"

echo "🚀 Setting up automated Cursor dataset syncing..."

# Create systemd service file
sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null <<EOF
[Unit]
Description=Cursor Dataset Auto Sync
After=network.target

[Service]
Type=simple
User=${USER}
WorkingDirectory=${SCRIPT_DIR}
ExecStart=${PYTHON_PATH} ${SCRIPT_DIR}/auto_sync_datasets.py --daemon
Restart=always
RestartSec=60
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Create cron job for incremental sync
(crontab -l 2>/dev/null; echo "# Cursor dataset incremental sync - every 5 minutes") | crontab -
(crontab -l 2>/dev/null; echo "*/5 * * * * cd ${SCRIPT_DIR} && ${PYTHON_PATH} incremental_sync.py >> incremental_sync.log 2>&1") | crontab -

# Create cron job for full sync - every hour
(crontab -l 2>/dev/null; echo "# Cursor dataset full sync - every hour") | crontab -
(crontab -l 2>/dev/null; echo "0 * * * * cd ${SCRIPT_DIR} && ${PYTHON_PATH} auto_sync_datasets.py --once >> auto_sync.log 2>&1") | crontab -

# Make scripts executable
chmod +x ${SCRIPT_DIR}/auto_sync_datasets.py
chmod +x ${SCRIPT_DIR}/incremental_sync.py

# Reload systemd and enable service
sudo systemctl daemon-reload
sudo systemctl enable ${SERVICE_NAME}

echo "✅ Setup complete!"
echo ""
echo "📋 Services created:"
echo "  - Systemd service: ${SERVICE_NAME}"
echo "  - Cron job: Incremental sync every 5 minutes"
echo "  - Cron job: Full sync every hour"
echo ""
echo "🔧 Management commands:"
echo "  Start service: sudo systemctl start ${SERVICE_NAME}"
echo "  Stop service:  sudo systemctl stop ${SERVICE_NAME}"
echo "  Status:        sudo systemctl status ${SERVICE_NAME}"
echo "  Logs:          journalctl -u ${SERVICE_NAME} -f"
echo ""
echo "📊 Cron jobs:"
echo "  View:          crontab -l"
echo "  Edit:          crontab -e"
echo ""
echo "📁 Log files:"
echo "  Auto sync:     ${SCRIPT_DIR}/auto_sync.log"
echo "  Incremental:   ${SCRIPT_DIR}/incremental_sync.log"
echo "  Systemd:       journalctl -u ${SERVICE_NAME}"
