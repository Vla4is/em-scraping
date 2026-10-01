"""Task 1 pipeline: fetch page 1, then parse it into a CSV.

    python task1/task1.py

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
