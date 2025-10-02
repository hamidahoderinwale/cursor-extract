# Cursor Data Extraction & Analysis System

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()
[![Data](https://img.shields.io/badge/Data-1.17M+%20Records-orange.svg)]()
[![Size](https://img.shields.io/badge/Size-8.4GB+%20Exports-red.svg)]()

> **Comprehensive system for extracting, analyzing, and visualizing Cursor IDE data**

This repository contains a complete toolkit for extracting and analyzing data from Cursor IDE, including API activity logs, workspace configurations, chat histories, and real-time development patterns. Perfect for developers, researchers, and data analysts who want to understand their coding patterns and AI interactions.

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/cursor-data-extraction.git
cd cursor-data-extraction

# Install dependencies
pip install -r requirements.txt

# Export all databases to JSON (saves to Desktop)
python export_all_databases_to_json.py

# Or export individual databases
python export_api_activity_to_json.py    # 1.17M+ API records
python export_vscdb_to_json.py          # Chat histories & workspace data
python export_prompt_versions_to_json.py # AI prompt versioning
```

## ✨ Features

- 🔍 **Complete Data Extraction** - Extract all Cursor IDE data including API logs, chat histories, and workspace configurations
- 📊 **Real-time Monitoring** - Monitor development patterns and AI interactions in real-time
- 🗄️ **Multiple Database Support** - Export SQLite databases (API activity, prompt versions) to JSON format
- 📈 **Data Visualization** - Interactive dashboards and analytics for understanding coding patterns
- 🔒 **Privacy-Focused** - All data processing happens locally, no external transmission
- 🚀 **Easy to Use** - Simple one-command exports with comprehensive documentation
- 📱 **Cross-Platform** - Works on macOS, Linux, and Windows
- 🔧 **Extensible** - Modular architecture for easy customization and extension

## 📊 Key Data Sources

| Data Source | Size | Records | Content | Importance |
|-------------|------|---------|---------|------------|
| **VSCDB Extraction** | 6.75 MB | Multiple workspaces | Chat histories, file tracking, workspace state | ⭐⭐⭐⭐⭐ |
| **API Activity DB** | ~500MB | 1,174,858 records | API calls, responses, errors | ⭐⭐⭐⭐⭐ |
| **Prompt Versions** | 4.4 MB | Variable | AI prompt history, versioning | ⭐⭐⭐⭐ |
| **Real-time Export** | ~7.9GB | 7,800+ files | Complete Cursor data | ⭐⭐⭐ |
| **Configuration** | <1MB | 8 files | Settings, IDE state | ⭐⭐ |

## 📋 Table of Contents

- [🚀 Quick Start](#-quick-start)
- [📊 Key Data Sources](#-key-data-sources)
- [🏗️ Architecture](#️-architecture)
- [📊 Data Sources & Retrieval Methods](#-data-sources--retrieval-methods)
- [🔧 Core Scripts & Their Functions](#-core-scripts--their-functions)
- [📁 Export Structure & Output Files](#-export-structure--output-files)
- [🚀 Usage Instructions](#-usage-instructions)
- [📊 Data Insights & Capabilities](#-data-insights--capabilities)
- [🔧 Technical Requirements](#-technical-requirements)
- [🎯 Use Cases](#-use-cases)
- [📝 File Commit Strategy](#-file-commit-strategy)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

## 🏗️ Architecture

### Core Components

```
cursor_data_extraction/
├── 📊 Data Sources
│   ├── SQLite Databases (cursor_api_activity.db, prompt_versions.db)
│   ├── Cursor Workspace Storage (state.vscdb files)
│   ├── Configuration Files (argv.json, ide_state.json, mcp.json)
│   └── Real-time Activity Logs
├── 🔧 Extraction Scripts
│   ├── Database Exporters
│   ├── Workspace Scanners
│   ├── Real-time Monitors
│   └── Configuration Extractors
├── 📈 Analysis Tools
│   ├── Data Dashboards
│   ├── API Servers
│   └── Visualization Components
└── 📁 Export Outputs
    ├── JSON Exports
    ├── Database Dumps
    └── Comprehensive Reports
```

## 📊 Data Sources & Retrieval Methods

### 1. **Cursor API Activity Database** (Most Comprehensive)
- **Location**: `cursor_api_analysis/cursor_api_activity.db`
- **Size**: ~500MB+ (estimated database size)
- **Records**: 1,174,858 total records
- **Tables**: 
  - `api2_cursor_activities`: 256,036 records
  - `other_cursor_activities`: 918,822 records
  - `api3_cursor_activities`: 0 records
  - `api_sessions`: 0 records
- **JSON Export**: `cursor_activity_export.json` (~2MB sample), `cursor_activity_FULL_export.json` (~500MB+ full)
- **Retrieval Method**: Direct SQLite database access via `export_cursor_activity_json.py`

### 2. **Cursor Workspace Storage (VSCDB)** (Most Meaningful)
- **Location**: `~/.cursor/User/workspaceStorage/` (macOS)
- **JSON Export**: `cursor_vscdb_extraction.json`
- **Size**: 6.75 MB
- **Content**: Project-specific state, chat histories, file tracking, workspace configurations
- **Files**: `state.vscdb`, `state.vscdb.backup`, workspace configurations
- **Retrieval Method**: Workspace scanning via `extract_cursor_data.py`

### 3. **Prompt Versioning Databases**
- **Locations**: 
  - `enhanced_cursor_export/prompt_versions.db`
  - `prompt_versions/prompt_versions.db`
- **JSON Export**: `prompt_versions.json`
- **Size**: 4.4 MB
- **Content**: AI prompt history, versioning, and evolution tracking
- **Retrieval Method**: SQLite extraction with JSON conversion

### 4. **Configuration Files**
- **Global**: `~/.cursor/argv.json`, `~/.cursor/ide_state.json`
- **Project-specific**: `mcp.json`, workspace settings
- **Content**: Cursor settings, recently viewed files, MCP server configs
- **Retrieval Method**: File system scanning and JSON parsing

### 5. **Comprehensive Real-Time Export**
- **Location**: `comprehensive_real_time_export/`
- **Size**: ~7.9GB (from cursor_dashboard exports)
- **Files**: 7,800+ files including logs, user data, workspace storage
- **Content**: Complete Cursor user data, settings, workspace configurations
- **Retrieval Method**: Complete system backup and extraction

### 6. **Real-time Activity Logs**
- **Source**: Cursor's internal logging system
- **Content**: Live API calls, user interactions, development patterns
- **Retrieval Method**: Real-time monitoring via `enhanced_cursor_integration.py`

## 📊 Key Data Metrics

### **Most Meaningful Data Sources**

| Data Source | Size | Records/Entries | Content Type | Importance |
|-------------|------|-----------------|--------------|------------|
| **VSCDB Extraction** | 6.75 MB | Multiple workspaces | Chat histories, file tracking, workspace state | ⭐⭐⭐⭐⭐ |
| **API Activity DB** | ~500MB | 1,174,858 records | API calls, responses, errors | ⭐⭐⭐⭐⭐ |
| **Prompt Versions** | 4.4 MB | Variable | AI prompt history, versioning | ⭐⭐⭐⭐ |
| **Real-time Export** | ~7.9GB | 7,800+ files | Complete Cursor data | ⭐⭐⭐ |
| **Configuration** | <1MB | 8 files | Settings, IDE state | ⭐⭐ |

### **Data Volume Summary**
- **Total Database Records**: 1,174,858+ (API activity)
- **Total File Size**: ~8.4GB+ (all exports combined)
- **Workspace Count**: 20+ unique workspaces
- **Time Range**: September 2025 (recent data)
- **Data Types**: 6 major categories

## 🔧 Core Scripts & Their Functions

### **Database Exporters**

#### `export_cursor_activity_json.py`
- **Purpose**: Export cursor API activity database to JSON
- **Input**: `cursor_api_activity.db`
- **Output**: `cursor_activity_export.json` (sample), `cursor_activity_FULL_export.json`
- **Features**: 
  - Sample export (1,000 records per table)
  - Full export (all 1.17M+ records)
  - Metadata and statistics

#### `export_db_to_jsonl.py`
- **Purpose**: Convert SQLite databases to JSONL format
- **Input**: Any SQLite database
- **Output**: JSONL files for streaming processing
- **Features**: Table-by-table export with metadata

#### `export_detailed_cursor_data.py`
- **Purpose**: Extract detailed interaction data from state databases
- **Input**: `state.vscdb` files from workspace storage
- **Output**: `detailed_cursor_interactions.json`
- **Features**: AI prompts, file searches, chat interactions, code context

### **Workspace Scanners**

#### `extract_cursor_data.py` (in cursor_dashboard)
- **Purpose**: Main workspace data extraction
- **Input**: Cursor workspace storage directories
- **Output**: `cursor_vscdb_extraction.json`, workspace-specific exports
- **Features**:
  - MD5 workspace folder detection
  - JSON/DB/SQLite file processing
  - Chat/prompt/code snippet categorization
  - Workspace metadata extraction

#### `comprehensive_cursor_extractor.py`
- **Purpose**: System-wide Cursor data extraction
- **Input**: Global Cursor directories
- **Output**: `cursor_comprehensive_export.json`
- **Features**:
  - Global configuration extraction
  - Project-specific data collection
  - IDE state tracking
  - MCP server configuration discovery

#### `comprehensive_data_extractor.py`
- **Purpose**: Find and extract all Cursor data
- **Input**: System-wide file scanning
- **Output**: Multiple export directories
- **Features**:
  - Recursive directory scanning
  - File type detection
  - Metadata extraction
  - Categorization by data type

### **Real-time Monitors**

#### `enhanced_cursor_integration.py`
- **Purpose**: Real-time Cursor data monitoring
- **Input**: Live Cursor activity
- **Output**: Live data exports, comprehensive reports
- **Features**:
  - Real-time file monitoring
  - Prompt versioning
  - Session tracking
  - Analytics generation

#### `realtime_prompt_monitor.py`
- **Purpose**: Monitor prompt changes in real-time
- **Input**: Live prompt modifications
- **Output**: Prompt versioning database
- **Features**:
  - Change detection
  - Version tracking
  - Diff analysis
  - Historical preservation

#### `cursor_activity_monitor.py`
- **Purpose**: Monitor Cursor API activity
- **Input**: Live API calls and responses
- **Output**: Activity database, real-time logs
- **Features**:
  - API call interception
  - Response time tracking
  - Error monitoring
  - Session management

### **Analysis & Visualization**

#### `cursor_api_server.py`
- **Purpose**: API server for data access
- **Features**: RESTful endpoints, data querying, real-time updates

#### `cursor_activity_dashboard.html`
- **Purpose**: Web-based data visualization
- **Features**: Interactive charts, data filtering, export capabilities

#### `properties_dashboard.py`
- **Purpose**: Properties and metadata analysis
- **Features**: Data categorization, statistics, trend analysis

## 📁 Export Structure & Output Files

### **Main Export Directories**

```
/Users/hamidaho/Desktop/new_experiments/
├── cursor_api_analysis/           # API activity database
│   └── cursor_api_activity.db     # Main SQLite database (1.17M+ records)
├── enhanced_cursor_export/        # Enhanced extraction results
│   ├── prompt_versions.db         # Prompt versioning database
│   └── cursor_comprehensive_export.json
├── prompt_versions/               # Additional prompt data
│   ├── prompt_versions.db
│   └── realtime_prompt_monitor_codeobj.marshalled
├── comprehensive_real_time_export/ # Real-time monitoring results
│   └── [7,800+ files]            # Complete Cursor user data
└── [various]_export/              # Specialized extractions
    ├── cursor_comprehensive_export.json
    ├── cursor_files/
    ├── rules/
    └── memories/
```

### **Key Output Files**

#### **JSON Exports**
- `cursor_activity_export.json` - Sample API activity (1,000 records per table, ~2MB)
- `cursor_activity_FULL_export.json` - Complete API activity (1.17M+ records, ~500MB+)
- `cursor_vscdb_extraction.json` - Workspace storage data (6.75 MB)
- `prompt_versions.json` - Prompt versioning data (4.4 MB)
- `cursor_comprehensive_export.json` - Configuration and settings data
- `detailed_cursor_interactions.json` - Detailed interaction data
- `workspace_data_comprehensive.json` - Complete workspace analysis

#### **Database Files**
- `cursor_api_activity.db` - Main activity database
- `prompt_versions.db` - Prompt versioning data
- `enhanced_cursor_telemetry.db` - Enhanced telemetry data

#### **Configuration Files**
- `argv.json` - Cursor startup arguments
- `ide_state.json` - Recently viewed files and IDE state
- `mcp.json` - Model Context Protocol server configurations

## 🚀 Usage Instructions

### **1. Basic Data Extraction**

```bash
# Export API activity database
python export_cursor_activity_json.py

# Extract workspace data
python extract_cursor_data.py

# Comprehensive system extraction
python comprehensive_cursor_extractor.py
```

### **2. Real-time Monitoring**

```bash
# Start real-time monitoring
python enhanced_cursor_integration.py

# Monitor prompt changes
python realtime_prompt_monitor.py

# Monitor API activity
python cursor_activity_monitor.py
```

### **3. Data Analysis**

```bash
# Start API server
python cursor_api_server.py

# Launch dashboard
python properties_dashboard.py

# Open web dashboard
open cursor_activity_dashboard.html
```

### **4. Export All Data to Desktop**

```bash
# Export everything to Desktop
python export_all_cursor_data_to_desktop.py
```

## 📊 Data Insights & Capabilities

### **What We Can Extract**

1. **Development Patterns**
   - File editing history
   - Code change patterns
   - Project switching behavior
   - Development session duration

2. **AI Interaction Data**
   - Prompt history and evolution
   - Response patterns
   - Code generation tracking
   - Chat conversation analysis

3. **Workspace Analysis**
   - Project configurations
   - File relationships
   - Extension usage
   - Settings preferences

4. **API Activity**
   - Request/response patterns
   - Performance metrics
   - Error tracking
   - Session management

5. **Real-time Monitoring**
   - Live development activity
   - Instant change detection
   - Performance tracking
   - Usage analytics

### **Privacy & Security Considerations**

- **Data Location**: All data is stored locally
- **No External Transmission**: No data is sent to external servers
- **User Control**: Full control over what data is extracted
- **Anonymization**: Optional data anonymization features
- **Retention**: Configurable data retention policies

## 🔧 Technical Requirements

### **Dependencies**
- Python 3.8+
- SQLite3
- Flask (for API server)
- Required packages in `requirements.txt`

### **System Requirements**
- macOS/Linux/Windows
- Cursor IDE installed
- Sufficient disk space for data exports
- Read access to Cursor data directories

## 📈 Performance Characteristics

### **Database Sizes**
- `cursor_api_activity.db`: ~1.17M records, ~500MB
- `prompt_versions.db`: Variable size based on usage
- Export files: 2MB-500MB+ depending on scope

### **Processing Times**
- Sample export: ~30 seconds
- Full export: ~5-10 minutes
- Real-time monitoring: Minimal overhead
- Dashboard loading: ~2-3 seconds

## 🎯 Use Cases

1. **Development Analytics**: Understand coding patterns and productivity
2. **AI Interaction Analysis**: Track prompt effectiveness and evolution
3. **Workspace Management**: Analyze project configurations and usage
4. **Performance Monitoring**: Track API performance and errors
5. **Data Backup**: Comprehensive backup of Cursor data
6. **Research**: Academic research on development patterns
7. **Debugging**: Troubleshoot Cursor issues and performance

## 🔄 Maintenance & Updates

### **Regular Tasks**
- Update extraction scripts for new Cursor versions
- Monitor database growth and performance
- Clean up old export files
- Update documentation for new features

### **Troubleshooting**
- Check file permissions for data directories
- Verify SQLite database integrity
- Monitor disk space for large exports
- Review error logs for extraction issues

## 📝 File Commit Strategy

### **Files to Commit to Repository**

#### **Core Scripts**
- `export_cursor_activity_json.py`
- `export_db_to_jsonl.py`
- `export_detailed_cursor_data.py`
- `comprehensive_cursor_extractor.py`
- `comprehensive_data_extractor.py`
- `enhanced_cursor_integration.py`
- `realtime_prompt_monitor.py`
- `cursor_activity_monitor.py`
- `extract_cursor_rules.py`
- `cursor_chat_history_extractor.py`

#### **Analysis & Visualization**
- `cursor_api_server.py`
- `properties_dashboard.py`
- `cursor_activity_dashboard.html`
- `cursor_activity_dashboard_enhanced.html`
- `integrated_cursor_dashboard.py`
- `real_time_cursor_dashboard.py`

#### **Utility Scripts**
- `export_all_cursor_data_to_desktop.py`
- `launch_cursor_dashboard.py`
- `launch_enhanced_dashboard.py`
- `serve_cursor_data.py`
- `serve_dashboard.py`

#### **Documentation**
- `README_CURSOR_DATA_EXTRACTION.md` (this file)
- `DATA_LOCATIONS.md`
- `EXTRACTION_SUMMARY.md`
- `REAL_TIME_EXTRACTION_SUMMARY.md`
- `ENHANCED_CURSOR_INTEGRATION_SUMMARY.md`

#### **Configuration**
- `requirements.txt`
- `cursor_properties_extractor.py`
- `prompt_version_control.py`

### **Files to Exclude from Repository**

#### **Generated Data Files**
- `*.db` files (databases)
- `*_export.json` files (generated exports)
- `cursor_activity.jsonl` (log files)
- `__pycache__/` directories
- `*.pyc` files

#### **Large Export Directories**
- `comprehensive_real_time_export/`
- `*_export/` directories
- `cursor_tracker_data/`
- `cursor_api_analysis/` (except scripts)

#### **Temporary Files**
- `*.log` files
- `*.tmp` files
- `*.backup` files
- `cursor_export_*/` directories

## 🎉 Conclusion

This system provides comprehensive access to Cursor IDE data through multiple extraction methods, real-time monitoring, and powerful analysis tools. It enables deep insights into development patterns, AI interactions, and workspace management while maintaining user privacy and data control.

The modular architecture allows for easy extension and customization, making it suitable for both individual developers and research teams studying software development patterns and AI-assisted coding.

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### 🐛 Bug Reports
- Use the [Issues](https://github.com/yourusername/cursor-data-extraction/issues) tab
- Include system information and error logs
- Provide steps to reproduce the issue

### 💡 Feature Requests
- Open an issue with the "enhancement" label
- Describe the use case and expected behavior
- Consider contributing the implementation

### 🔧 Code Contributions
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### 📚 Documentation
- Improve README sections
- Add code comments
- Create usage examples
- Write tutorials

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for the Cursor IDE community
- Inspired by the need for better development analytics
- Thanks to all contributors and users

---

**⭐ If you find this project useful, please give it a star!**
