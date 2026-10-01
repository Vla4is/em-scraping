"""Task 2 pipeline: fetch every page of the category, then parse them into one CSV.

    python task2/task2.py

Stops if the fetch fails (blocked, no VPN), so an older page is never parsed by mistake.
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent

for step in ("fetch_page.py", "parse_page.py"):
    print(f"--- {step}")
    result = subprocess.run([sys.executable, str(HERE / step)])
    if result.returncode != 0:
        sys.exit(f"{step} failed (exit {result.returncode}); stopping.")
print("--- done")
