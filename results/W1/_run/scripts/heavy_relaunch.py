#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Give the six cross-epoch / successor-key lemmas a 6-hour budget.

They exhausted 1800 s and 7200 s without settling, so they are relaunched on
their own with `--scale-overrides 3` while everything else is already delivered.
"""
from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
from pathlib import Path

BASE = Path("/home/lab701/qzy/CDDS补充实验")
W1 = BASE / "code/v1_auxiliary/W1_reveal_matrix"
RUNS_ROOT = Path("/home/lab701/qzy/CDDS补充实验_results/W1_reveal_matrix")
run = sorted(RUNS_ROOT.glob("w1_*"))[-1]

HEAVY = {
    "w1_r_historical_pce_after_epoch_reachable",
    "w1_r_historical_pce_after_epoch_plaintext_secrecy",
    "w1_r_historical_pce_after_epoch_key_secrecy",
    "w1_r_successor_only_reachable",
    "w1_r_successor_only_plaintext_secrecy",
    "w1_r_successor_only_key_secrecy",
}

# Stop any in-flight instance of these lemmas so the relaunch is clean.
killed = []
out = subprocess.run(["bash", "-c", "ps -eo pid,args"], capture_output=True, text=True).stdout
for line in out.splitlines():
    if "tamarin-prover" not in line or "repaired_reveal_matrix" not in line:
        continue
    for lemma in HEAVY:
        if f"--prove={lemma}" in line:
            pid = int(line.split()[0])
            try:
                os.kill(pid, signal.SIGKILL)
                killed.append((pid, lemma))
            except OSError:
                pass
print("stopped in-flight heavy lemmas:", killed or "none")

removed = 0
for status in run.glob("repaired/*/*.status.json"):
    record = json.loads(status.read_text(encoding="utf-8"))
    if record["lemma"] in HEAVY:
        status.unlink()
        removed += 1
print("cleared stale heavy status records:", removed)

log = Path("/tmp/w1_heavy.log")
command = ["nohup", sys.executable, str(W1 / "w1_driver.py"),
           "--lemma", "w1_r_historical_pce_after_epoch_reachable",
           "--jobs", "1", "--timeout", "21600", "--derivcheck", "300",
           "--scale-overrides", "3",
           "--runs-root", str(RUNS_ROOT), "--run-dir", str(run), "--resume"]
print("note: launching per-lemma invocations")
print("run dir:", run)
print("log:", log)
