#!/usr/bin/env python3
"""
File Counter with Recursive Subdirectory Support
Counts all files inside a folder and its subfolders,
and generates a detailed log file.
"""

import os
import sys
import datetime
from collections import defaultdict


# ─────────────────────────────────────────────
#  CONFIGURATION
# ─────────────────────────────────────────────
LOG_DIR = os.path.dirname(os.path.abspath(__file__))  # Log saved next to script


# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def format_size(bytes_val):
    """Convert raw bytes to human-readable string."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_val < 1024:
            return f"{bytes_val:.2f} {unit}"
        bytes_val /= 1024
    return f"{bytes_val:.2f} PB"


def get_file_info(filepath):
    """Return a dict with metadata about a single file."""
    try:
        stat = os.stat(filepath)
        return {
            "path":      filepath,
            "name":      os.path.basename(filepath),
            "extension": os.path.splitext(filepath)[1].lower() or "(no ext)",
            "size":      stat.st_size,
            "modified":  datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
        }
    except PermissionError:
        return None
    except Exception as e:
        return {"path": filepath, "name": os.path.basename(filepath),
                "extension": "?", "size": 0, "modified": "?", "error": str(e)}


# ─────────────────────────────────────────────
#  CORE SCAN
# ─────────────────────────────────────────────
def scan_folder(root_path):
    """
    Walk the folder tree and collect:
      - all file metadata
      - per-directory file counts
      - skipped (permission-denied) directories
    """
    all_files      = []
    dir_counts     = {}       # {dir_path: file_count}
    skipped_dirs   = []

    for dirpath, dirnames, filenames in os.walk(root_path):
        # Handle permission errors on subdirectories
        accessible = []
        for d in dirnames:
            full = os.path.join(dirpath, d)
            if os.access(full, os.R_OK):
                accessible.append(d)
            else:
                skipped_dirs.append(full)
        dirnames[:] = accessible   # prune inaccessible dirs from walk

        count = 0
        for fname in filenames:
            fpath = os.path.join(dirpath, fname)
            info  = get_file_info(fpath)
            if info:
                all_files.append(info)
                count += 1

        dir_counts[dirpath] = count

    return all_files, dir_counts, skipped_dirs


# ─────────────────────────────────────────────
#  LOG GENERATION
# ─────────────────────────────────────────────
def write_log(root_path, all_files, dir_counts, skipped_dirs, scan_start, scan_end):
    """Write a structured, detailed log file and return its path."""
    timestamp  = scan_start.strftime("%Y%m%d_%H%M%S")
    log_name   = f"file_count_log_{timestamp}.txt"
    log_path   = os.path.join(LOG_DIR, log_name)

    total_files = len(all_files)
    total_size  = sum(f["size"] for f in all_files)
    duration    = (scan_end - scan_start).total_seconds()

    # Extension breakdown
    ext_counts = defaultdict(lambda: {"count": 0, "size": 0})
    for f in all_files:
        ext_counts[f["extension"]]["count"] += 1
        ext_counts[f["extension"]]["size"]  += f["size"]

    with open(log_path, "w", encoding="utf-8") as log:

        # ── HEADER ──────────────────────────────────────────────────────
        log.write("=" * 70 + "\n")
        log.write("              FILE COUNTER — SCAN REPORT\n")
        log.write("=" * 70 + "\n\n")

        log.write(f"  Scan Target   : {root_path}\n")
        log.write(f"  Scan Started  : {scan_start.strftime('%Y-%m-%d %H:%M:%S')}\n")
        log.write(f"  Scan Finished : {scan_end.strftime('%Y-%m-%d %H:%M:%S')}\n")
        log.write(f"  Duration      : {duration:.3f} seconds\n\n")

        # ── SUMMARY ─────────────────────────────────────────────────────
        log.write("─" * 70 + "\n")
        log.write("  SUMMARY\n")
        log.write("─" * 70 + "\n")
        log.write(f"  Total Files       : {total_files:,}\n")
        log.write(f"  Total Size        : {format_size(total_size)}\n")
        log.write(f"  Total Directories : {len(dir_counts):,}\n")
        log.write(f"  Skipped (No Perm) : {len(skipped_dirs):,}\n\n")

        # ── EXTENSION BREAKDOWN ──────────────────────────────────────────
        log.write("─" * 70 + "\n")
        log.write("  FILE TYPES (by extension)\n")
        log.write("─" * 70 + "\n")
        sorted_exts = sorted(ext_counts.items(), key=lambda x: x[1]["count"], reverse=True)
        for ext, data in sorted_exts:
            log.write(f"  {ext:<20} {data['count']:>6,} files    {format_size(data['size']):>12}\n")
        log.write("\n")

        # ── PER-DIRECTORY BREAKDOWN ──────────────────────────────────────
        log.write("─" * 70 + "\n")
        log.write("  FILES PER DIRECTORY\n")
        log.write("─" * 70 + "\n")
        for dirpath, count in sorted(dir_counts.items()):
            rel = os.path.relpath(dirpath, root_path) or "."
            log.write(f"  [{count:>5,} files]  {rel}\n")
        log.write("\n")

        # ── SKIPPED DIRECTORIES ──────────────────────────────────────────
        if skipped_dirs:
            log.write("─" * 70 + "\n")
            log.write("  SKIPPED DIRECTORIES (permission denied)\n")
            log.write("─" * 70 + "\n")
            for d in skipped_dirs:
                log.write(f"  !! {d}\n")
            log.write("\n")

        # ── FULL FILE LIST ───────────────────────────────────────────────
        log.write("─" * 70 + "\n")
        log.write("  FULL FILE LIST\n")
        log.write("─" * 70 + "\n")
        log.write(f"  {'#':<7} {'Size':>10}  {'Modified':<20}  {'Ext':<12}  Name\n")
        log.write(f"  {'-'*6}  {'-'*10}  {'-'*19}  {'-'*11}  {'-'*30}\n")
        for i, f in enumerate(all_files, 1):
            rel_name = os.path.relpath(f["path"], root_path)
            log.write(
                f"  {i:<7,} {format_size(f['size']):>10}  {f['modified']:<20}  "
                f"{f['extension']:<12}  {rel_name}\n"
            )

        # ── FOOTER ──────────────────────────────────────────────────────
        log.write("\n" + "=" * 70 + "\n")
        log.write(f"  End of Report — {total_files:,} files found\n")
        log.write("=" * 70 + "\n")

    return log_path


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────
def main():
    # ── Get target folder ──
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        target = input("Enter folder path to scan: ").strip().strip('"')

    # ── Validate ──
    if not os.path.exists(target):
        print(f"[ERROR] Path does not exist: {target}")
        sys.exit(1)
    if not os.path.isdir(target):
        print(f"[ERROR] Path is not a directory: {target}")
        sys.exit(1)

    print(f"\n  Scanning: {target}")
    print("  Please wait...\n")

    # ── Scan ──
    scan_start = datetime.datetime.now()
    all_files, dir_counts, skipped_dirs = scan_folder(target)
    scan_end   = datetime.datetime.now()

    # ── Console Summary ──
    total_size = sum(f["size"] for f in all_files)
    print("=" * 50)
    print("  SCAN COMPLETE")
    print("=" * 50)
    print(f"  Total Files       : {len(all_files):,}")
    print(f"  Total Size        : {format_size(total_size)}")
    print(f"  Total Directories : {len(dir_counts):,}")
    print(f"  Skipped Dirs      : {len(skipped_dirs):,}")
    print(f"  Duration          : {(scan_end - scan_start).total_seconds():.3f}s")

    # ── Write Log ──
    log_path = write_log(target, all_files, dir_counts, skipped_dirs, scan_start, scan_end)
    print(f"\n  Log saved to: {log_path}\n")


if __name__ == "__main__":
    main()
