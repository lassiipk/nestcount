# nestcount
 
Recursively count every file in a folder — and log every detail.
 
![Python](https://img.shields.io/badge/Python-3.6%2B-blue?style=flat-square)
![Zero Dependencies](https://img.shields.io/badge/dependencies-none-brightgreen?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-gray?style=flat-square)
 
---
 
## What it does
 
Drop a folder path in, get back a full count of every file — across every subfolder, no matter how deep — plus a timestamped `.txt` log with sizes, types, modified dates, and a per-directory breakdown.
 
---
 
## Features
 
- **Deep recursion** — walks every nested subfolder automatically
- **Extension breakdown** — groups files by type with combined sizes
- **Detailed log** — timestamped `.txt` report saved per run, never overwritten
- **Graceful errors** — permission-denied directories get logged, not crashes
 
---
 
## Usage
 
```bash
# Pass the folder path directly
python file_counter.py "C:\Users\You\Documents"
 
# Or let it prompt you
python file_counter.py
```
 
---
 
## Log output includes
 
```
Scan target, start time, duration
Total files, total size, directory count
Files per directory (recursive breakdown)
Extension breakdown — count and size per type
Full file list — name, size, modified date, relative path
Skipped directories — permission denied, flagged cleanly
```
 
---
 
## Requirements
 
Python 3.6 or higher. No external packages. No `pip install`. Just run it.
 
---
 
## License
 
MIT — use it, fork it, ship it.