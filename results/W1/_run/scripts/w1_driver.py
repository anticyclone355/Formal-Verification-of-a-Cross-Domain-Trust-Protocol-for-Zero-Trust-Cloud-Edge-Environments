#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""W1 driver: run every lemma listed in experiments.json, one Tamarin invocation
per lemma, and archive raw output, timing, proof state, trace JSON and trace graph.

Layout produced under <W1>/runs/w1_<timestamp>/ :
    commands.json                  plan actually executed
    summary.csv / summary.json     per-lemma result + timing
    <protocol>/<case>/<lemma>.stdout.log
    <protocol>/<case>/<lemma>.stderr.log
    <protocol>/<case>/<lemma>.time.txt
    <protocol>/<case>/<lemma>.status.json
    <protocol>/<case>/<lemma>.proof.spthy     (replayable proof state)
    <protocol>/<case>/<lemma>.trace.json      (found trace, when falsified)
    <protocol>/<case>/<lemma>.trace.dot       (graphviz source)
    <protocol>/<case>/<lemma>.trace.png       (rendered trace graph)
    <protocol>/<case>/<lemma>.trace.svg
"""
from __future__ import annotations

import argparse
import concurrent.futures as futures
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REMOTE_HINT = "/home/lab701/qzy/CDDS补充实验"

# Lemmas whose proof search needs more than the default per-lemma budget.
# The cross-epoch and successor-key variants carry two credential generations
# plus modular arithmetic; the two lifecycle obligations are all-traces
# unreachability claims over the erased state.
TIMEOUT_OVERRIDES = {
    "historical_pce_after_epoch": 7200,
    "successor_only": 7200,
    "key_lifecycle": 10800,
}

RESULT_RE = re.compile(
    r"^\s*(?P<lemma>\S+)\s+\((?P<trace>all-traces|exists-trace)\):\s*(?P<summary>.+?)\s*$",
    re.M,
)


def run_one(entry, tag, tamarin, first_flags, timeout, derivcheck, out_dir):
    """Run one lemma in a private working directory."""
    protocol = entry["protocol"]
    case = entry["case"]
    lemma = entry["lemma"]
    work = out_dir / protocol / case
    work.mkdir(parents=True, exist_ok=True)
    model_src = ROOT / protocol / f"{protocol}_reveal_matrix.spthy"
    model = work / f"{protocol}_reveal_matrix.spthy"
    # Refresh only when the content differs, and publish through a
    # process-unique temporary file: parallel workers share this path, so an
    # unconditional truncating copy could expose a half-written model.
    source_bytes = model_src.read_bytes()
    source_sha256 = hashlib.sha256(source_bytes).hexdigest().upper()
    if not model.exists() or hashlib.sha256(model.read_bytes()).hexdigest().upper() != source_sha256:
        # The temporary name must be unique per invocation: several lemmas of the
        # same (protocol, case) run in parallel and share this directory, and a
        # shared temp path made one thread's os.replace consume another's file.
        temporary = work / (
            f".{protocol}.{os.getpid()}.{threading.get_ident()}."
            f"{hashlib.sha256(lemma.encode('utf-8')).hexdigest()[:8]}.tmp"
        )
        temporary.write_bytes(source_bytes)
        for attempt in range(20):
            try:
                os.replace(temporary, model)
                break
            except FileNotFoundError:
                # Another worker published first; verify and fall through.
                if model.exists() and hashlib.sha256(model.read_bytes()).hexdigest().upper() == source_sha256:
                    break
                temporary.write_bytes(source_bytes)
                time.sleep(0.05 * (attempt + 1))
        else:
            raise RuntimeError(f"could not publish model for {protocol}/{case}")
    model_sha256 = hashlib.sha256(model.read_bytes()).hexdigest().upper()

    stem = lemma
    paths = {
        "stdout": work / f"{stem}.stdout.log",
        "stderr": work / f"{stem}.stderr.log",
        "time": work / f"{stem}.time.txt",
        "status": work / f"{stem}.status.json",
        "proof": work / f"{stem}.proof.spthy",
        "trace_json": work / f"{stem}.trace.json",
        "trace_dot": work / f"{stem}.trace.dot",
        "trace_png": work / f"{stem}.trace.png",
        "trace_svg": work / f"{stem}.trace.svg",
    }

    command = [tamarin, model.name, "--quit-on-warning",
               f"--derivcheck-timeout={derivcheck}", f"--prove={lemma}"]
    for flag in first_flags:
        command.append(f"-D{flag}")
    command += [
        f"--output={paths['proof'].name}",
        f"--output-json={paths['trace_json'].name}",
        f"--output-dot={paths['trace_dot'].name}",
    ]

    started_utc = datetime.now(timezone.utc).isoformat()
    started = time.monotonic()
    timed_out = False
    stopped_with_child = False
    with paths["stdout"].open("w", encoding="utf-8") as out, \
         paths["stderr"].open("w", encoding="utf-8") as err:
        proc = subprocess.Popen(command, cwd=str(work), stdout=out, stderr=err)
        try:
            proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            proc.kill()
            proc.wait()
        except BaseException:
            # The driver itself is being stopped (SIGTERM/SIGKILL escalation or
            # KeyboardInterrupt). Kill the child and record nothing: a status
            # record written here would claim a terminal failure for a lemma
            # that was never actually given a chance to finish.
            stopped_with_child = True
            proc.kill()
            proc.wait()
    if stopped_with_child:
        raise KeyboardInterrupt("driver stopped; no status record written")
    elapsed = time.monotonic() - started
    returncode = proc.returncode
    finished_utc = datetime.now(timezone.utc).isoformat()

    paths["time"].write_text(
        f"started_utc={started_utc}\nfinished_utc={finished_utc}\n"
        f"wall_seconds={elapsed:.3f}\ntimeout={timed_out}\nexit_code={returncode}\n"
        f"command={' '.join(command)}\ncwd={work}\n",
        encoding="utf-8",
    )

    raw = paths["stdout"].read_text(encoding="utf-8", errors="replace")
    err = paths["stderr"].read_text(encoding="utf-8", errors="replace")
    summary = None
    status = "inconclusive"
    if timed_out:
        status = "timeout"
    elif returncode != 0:
        status = "tool_error"
    else:
        match = None
        for candidate in RESULT_RE.finditer(raw):
            if candidate.group("lemma") == lemma:
                match = candidate
        if match:
            summary = match.group("summary").strip()
            if summary.startswith("verified"):
                status = "verified"
            elif summary.startswith("falsified"):
                status = "falsified"
            elif "analysis incomplete" in summary:
                status = "incomplete"
            else:
                status = "unknown_summary"

    # Tamarin's own accounted processing time, for cross-checking wall clock.
    tool_seconds = None
    tool_match = re.search(r"processing time:\s*([0-9.]+)s", raw)
    if tool_match:
        tool_seconds = float(tool_match.group(1))
    steps = None
    if summary:
        step_match = re.search(r"\((\d+) steps\)", summary)
        if step_match:
            steps = int(step_match.group(1))

    # Render the trace graph when Tamarin emitted one.
    rendered = {}
    if paths["trace_dot"].exists() and paths["trace_dot"].stat().st_size > 0:
        for fmt, target in (("png", paths["trace_png"]), ("svg", paths["trace_svg"])):
            try:
                subprocess.run(
                    ["dot", f"-T{fmt}", paths["trace_dot"].name, "-o", target.name],
                    cwd=str(work), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                    timeout=600, check=False,
                )
            except subprocess.TimeoutExpired:
                pass
            if target.exists() and target.stat().st_size > 0:
                rendered[fmt] = target.name

    artifacts = {k: v.name for k, v in paths.items()
                 if k not in {"status"} and v.exists() and v.stat().st_size > 0}
    status_record = {
        "protocol": protocol,
        "case": case,
        "lemma": lemma,
        "trace": entry["trace"],
        "defines": entry["defines"],
        "model_sha256": model_sha256,
        "status": status,
        "raw_summary": summary,
        "steps": steps,
        "wall_seconds": round(elapsed, 3),
        "tamarin_processing_seconds": tool_seconds,
        "started_utc": started_utc,
        "finished_utc": finished_utc,
        "timed_out": timed_out,
        "exit_code": returncode,
        "command": command,
        "workdir": str(work),
        "artifacts": artifacts,
        "rendered_graphs": rendered,
        "stderr_tail": err.strip().splitlines()[-5:],
    }
    paths["status"].write_text(
        json.dumps(status_record, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"[{status:>12}] {elapsed:8.2f}s  {protocol}/{case}/{lemma}", flush=True)
    return status_record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tamarin", default="tamarin-prover")
    parser.add_argument("--timeout", type=int, default=1800, help="seconds per lemma")
    parser.add_argument("--derivcheck", type=int, default=300,
                        help="Tamarin --derivcheck-timeout in seconds (default 5s is too "
                             "small for these models: they need ~40s)")
    parser.add_argument("--jobs", type=int, default=8, help="parallel Tamarin processes")
    parser.add_argument("--runs-root",
                        help="directory that holds run subdirectories; defaults to "
                             "<model dir>/runs. Point this outside the synced source tree "
                             "so a workspace sync cannot delete the evidence.")
    parser.add_argument("--no-overrides", action="store_true",
                        help="ignore the per-case budget overrides")
    parser.add_argument("--scale-overrides", type=int, default=1,
                        help="multiply the per-case budget overrides, e.g. 3 to give the "
                             "cross-epoch lemmas 21600s instead of 7200s")
    parser.add_argument("--protocol", choices=["original", "repaired"])
    parser.add_argument("--case")
    parser.add_argument("--lemma")
    parser.add_argument("--run-dir", help="explicit run directory (for --resume)")
    parser.add_argument("--resume", action="store_true",
                        help="skip lemmas whose status.json is already terminal")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    entries = json.loads((ROOT / "experiments.json").read_text(encoding="utf-8"))["experiments"]
    if args.protocol:
        entries = [e for e in entries if e["protocol"] == args.protocol]
    if args.case:
        entries = [e for e in entries if e["case"] == args.case]
    if args.lemma:
        entries = [e for e in entries if e["lemma"] == args.lemma]
    if not entries:
        parser.error("no matching experiment")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    runs_root = Path(args.runs_root) if args.runs_root else ROOT / "runs"
    runs_root.mkdir(parents=True, exist_ok=True)
    out_dir = Path(args.run_dir) if args.run_dir else runs_root / f"w1_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    def budget(entry):
        if args.no_overrides:
            return args.timeout
        base = TIMEOUT_OVERRIDES.get(entry["case"], 0)
        if base and args.scale_overrides > 1:
            base *= args.scale_overrides
        return max(args.timeout, base)

    version = subprocess.run([args.tamarin, "--version"], capture_output=True,
                             text=True, encoding="utf-8", errors="replace", check=False)
    plan = {
        "started_utc": stamp,
        "tamarin": args.tamarin,
        "tamarin_version": (version.stdout or "") + (version.stderr or ""),
        "timeout_seconds_per_lemma": args.timeout,
        "timeout_overrides": {} if args.no_overrides else TIMEOUT_OVERRIDES,
        "derivcheck_timeout_seconds": args.derivcheck,
        "parallel_jobs": args.jobs,
        "lemma_count": len(entries),
        "run_dir": str(out_dir),
        "entries": entries,
    }
    (out_dir / "commands.json").write_text(
        json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.dry_run:
        print(json.dumps(plan, ensure_ascii=False, indent=2)[:4000])
        return 0

    pending = []
    for entry in entries:
        status_path = out_dir / entry["protocol"] / entry["case"] / f"{entry['lemma']}.status.json"
        if args.resume and status_path.exists():
            try:
                previous = json.loads(status_path.read_text(encoding="utf-8"))
                if previous.get("status") in {"verified", "falsified", "incomplete", "timeout",
                                              "tool_error"}:
                    print(f"[skip] {entry['lemma']} ({previous['status']})", flush=True)
                    continue
            except json.JSONDecodeError:
                pass
        pending.append((entry, entry["lemma"]))

    t0 = time.monotonic()
    effective_overrides = {} if args.no_overrides else TIMEOUT_OVERRIDES
    print(f"running {len(pending)} lemmas, {args.jobs} in parallel, "
          f"default {args.timeout}s per lemma, derivcheck-timeout={args.derivcheck}s, "
          f"overrides={effective_overrides}", flush=True)
    results = []
    with futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        jobs = {pool.submit(run_one, e, t, args.tamarin, e["defines"],
                            budget(e), args.derivcheck, out_dir): e for e, t in pending}
        for job in futures.as_completed(jobs):
            try:
                results.append(job.result())
            except Exception as exc:  # noqa: BLE001
                entry = jobs[job]
                results.append({"protocol": entry["protocol"], "case": entry["case"],
                                "lemma": entry["lemma"], "status": "driver_error",
                                "error": repr(exc), "wall_seconds": None})
                print(f"[driver_error] {entry['lemma']}: {exc!r}", flush=True)

    results.sort(key=lambda r: (r["protocol"], r["case"], r["lemma"]))
    total = time.monotonic() - t0
    tally = {}
    for record in results:
        tally[record["status"]] = tally.get(record["status"], 0) + 1
    summary = {
        "run_dir": str(out_dir),
        "total_wall_seconds": round(total, 2),
        "lemma_count": len(results),
        "status_tally": tally,
        "tamarin_version": plan["tamarin_version"],
        "finished_utc": datetime.now(timezone.utc).isoformat(),
        "results": results,
    }
    (out_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    header = "protocol,case,lemma,expected_trace,status,wall_seconds,raw_summary\n"
    rows = "".join(
        "{},{},{},{},{},{},{}\n".format(
            r["protocol"], r["case"], r["lemma"], r.get("trace", ""), r["status"],
            r.get("wall_seconds", ""),
            str(r.get("raw_summary", "")).replace(",", ";"),
        ) for r in results)
    (out_dir / "summary.csv").write_text(header + rows, encoding="utf-8")

    # Human-readable per-case report with the trace graphs embedded.
    lines = [
        "# W1 运行结果",
        "",
        f"- 运行目录：`{out_dir}`",
        f"- 完成时间（UTC）：{summary['finished_utc']}",
        f"- Tamarin：{plan['tamarin_version'].strip().splitlines()[0] if plan['tamarin_version'] else 'n/a'}",
        f"- 每条性质预算：{args.timeout}s，派生检查预算：{args.derivcheck}s，并行度：{args.jobs}",
        f"- 总墙钟时间：{summary['total_wall_seconds']}s",
        f"- 状态统计：`{json.dumps(tally, ensure_ascii=False)}`",
        "",
        "| 协议 | 场景 | 性质 | 期望轨迹 | 结果 | 耗时(s) | Tamarin 计时(s) | 步骤 | 反例图 |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for record in results:
        graph = record.get("rendered_graphs", {}).get("png", "")
        graph_cell = f"[png]({record['protocol']}/{record['case']}/{graph})" if graph else ""
        lines.append(
            "| {p} | {c} | `{l}` | {t} | {s} | {w} | {ts} | {st} | {g} |".format(
                p=record["protocol"], c=record["case"], l=record["lemma"],
                t=record.get("trace", ""), s=record["status"],
                w=record.get("wall_seconds", ""),
                ts=record.get("tamarin_processing_seconds") or "",
                st=record.get("steps") or "", g=graph_cell,
            ))
    (out_dir / "run_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps({"status_tally": tally, "total_wall_seconds": round(total, 2),
                      "run_dir": str(out_dir)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
