#!/bin/bash
# Re-run the unresolved lemmas with per-lemma budgets.
# Epoch / successor variants get 7200 s; the two lifecycle unreachability
# candidates get 10800 s; the empty-file race casualty needs only a few minutes.
set -u
W1=/home/lab701/qzy/CDDS补充实验/code/v1_auxiliary/W1_reveal_matrix
RUN=$(ls -d "$W1"/runs/w1_* | tail -1)
LOG=/tmp/w1_retry.log
: > "$LOG"

run_one() {  # lemma timeout
  local lemma=$1 timeout=$2
  echo "=== $lemma (budget ${timeout}s) ===" >> "$LOG"
  python3 "$W1/w1_driver.py" --lemma "$lemma" --jobs 1 --timeout "$timeout" \
      --derivcheck 300 --run-dir "$RUN" --resume >> "$LOG" 2>&1
  echo "--- exit $? for $lemma ---" >> "$LOG"
}

# Group A: three lemmas that previously exhausted 1800 s, run concurrently.
for lemma in w1_r_historical_pce_after_epoch_reachable \
             w1_r_historical_pce_after_epoch_plaintext_secrecy \
             w1_r_historical_pce_after_epoch_key_secrecy \
             w1_r_successor_only_reachable \
             w1_r_successor_only_plaintext_secrecy \
             w1_r_successor_only_key_secrecy; do
  run_one "$lemma" 7200 &
done
wait
echo "=== group A finished ===" >> "$LOG"

# Group B: the two all-traces lifecycle obligations plus the race casualty.
for lemma in w1_r_key_disclosure_after_erasure_unreachable \
             w1_r_ephemeral_disclosure_after_erasure_unreachable; do
  run_one "$lemma" 10800 &
done
run_one w1_r_pce_only_reachable 900 &
wait
echo "=== group B finished ===" >> "$LOG"
echo "RETRY_DONE" >> "$LOG"
