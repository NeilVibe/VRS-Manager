# VRS Manager - Quick Start Guide

## Installation

```bash
cd /home/neil1988/vrsmanager
pip install -r requirements.txt
```

## Running the Application

```bash
python main.py
```

## Project Structure

```
vrsmanager/
├── main.py                    # START HERE - Main entry point
├── requirements.txt           # Dependencies
├── src/
│   ├── processors/           # Process orchestrators
│   │   ├── raw_processor.py
│   │   ├── working_processor.py
│   │   ├── alllang_processor.py
│   │   └── master_processor.py
│   ├── ui/                   # GUI components
│   │   ├── main_window.py
│   │   └── history_viewer.py
│   ├── core/                 # Business logic
│   ├── io/                   # Excel I/O
│   ├── history/              # Update tracking
│   └── utils/                # Utilities
└── vrsmanager1114v3.py       # Original monolith (archived)
```

## Available Processes

1. **Raw Process** - Compare previous and current raw VRS files
2. **Working Process** - Import with intelligent logic
3. **All Language Process** - Tri-lingual import (KR/EN/CN)
4. **Master File Update** - Update master with working output
5. **View Update History** - See all process history

## Key Features

- 4-Tier Key System for accurate matching
- Background threading (UI stays responsive)
- Complete update history tracking
- Intelligent import logic based on recording status
- High/Low importance handling (Master process)
- Flexible language updates (All Language process)

## File Locations

- **Output files**: Generated in script directory
- **History files**: JSON files in script directory
  - `working_update_history.json`
  - `alllang_update_history.json`
  - `master_update_history.json`

## For All Language Process

Create these folders in the script directory:
- `Previous/` - Optional previous files (_KR, _EN, _CN)
- `Current/` - Required current files (_KR, _EN, _CN)

## Documentation

- `PHASE2_EXTRACTION_COMPLETE.md` - Complete extraction summary
- `DEVELOPER_GUIDE.md` - Development guidelines
- `roadmap.md` - Project roadmap

## Support

For issues or questions, refer to the developer documentation.

---
VRS Manager v1114v3 - By Neil Schmitt
