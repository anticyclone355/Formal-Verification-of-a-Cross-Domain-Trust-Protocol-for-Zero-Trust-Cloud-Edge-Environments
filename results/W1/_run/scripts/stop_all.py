#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Stop everything belonging to the W1 campaign: harness, drivers, Tamarin children.

Deliberately does NOT touch the author's own W2/W3 models or processes.
"""
import os
import re
import signal
import subprocess
import time

PATTERNS = ["run_heavy.sh", "w1_driver.py", "w1_campaign", "retry_all.sh"]

print("--- before ---")
print(subprocess.run(["bash", "-c",
                      "ps -eo pid,etimes,args | grep -E 'tamarin-prover|w1_driver|run_heavy' | grep -v grep"],
                     capture_output=True, text=True).stdout or "(none)")

out = subprocess.run(["bash", "-c", "ps -eo pid,args"], capture_output=True, text=True).stdout
stopped = {"harness": 0, "driver": 0, "tamarin": 0}
for line in out.splitlines():
    if "grep" in line or "ps -eo" in line:
        continue
    pid_text = line.split(None, 1)
    if len(pid_text) != 2:
        continue
    pid_str, args = pid_text
    if not pid_str.isdigit():
        continue
    pid = int(pid_str)
    if any(pattern in args for pattern in PATTERNS):
        try:
            os.kill(pid, signal.SIGKILL)
            stopped["harness" if "run_heavy" in args or "retry_all" in args else "driver"] += 1
        except OSError:
            pass
    elif "tamarin-prover" in args and "repaired_reveal_matrix" in args:
        try:
            os.kill(pid, signal.SIGKILL)
            stopped["tamarin"] += 1
        except OSError:
            pass

time.sleep(5)
print("stopped:", stopped)
print("--- after ---")
print(subprocess.run(["bash", "-c",
                      "ps -eo pid,etimes,args | grep -E 'tamarin-prover|w1_driver|run_heavy' | grep -v grep"],
                     capture_output=True, text=True).stdout or "(none)")
print("--- author jobs left alone ---")
print(subprocess.run(["bash", "-c",
                      "ps -eo pid,etimes,args | grep -E 'w2_|w3_|state_lifecycle|concurrent_agreement' | grep -v grep"],
                     capture_output=True, text=True).stdout or "(none)")
print("--- memory ---")
print(subprocess.run(["free", "-g"], capture_output=True, text=True).stdout)
print("=== end ===")
