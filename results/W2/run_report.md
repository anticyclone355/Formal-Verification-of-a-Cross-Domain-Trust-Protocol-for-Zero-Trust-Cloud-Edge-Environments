# W2 确认与状态生命周期 运行结果

- 运行目录：`/home/lab701/qzy/CDDS补充实验/code/v1_auxiliary/W2_confirmation_lifecycle/runs/w2_20260928T084144Z`
- 完成时间（UTC）：2026-09-28T21:49:18.785407+00:00
- 模型：`repaired_state_lifecycle.spthy` SHA-256 `14E941343C02EB549AC53CB568E14742E6B3F525A3873170A1160887BDEE19F9`
- Tamarin：tamarin-prover 1.10.0, (C) David Basin, Cas Cremers, Jannik Dreier, Simon Meier, Ralf Sasse, Benedikt Schmidt, 2010-2023
- 每条性质预算：3600s，派生检查预算：300s，并行度：4
- 总墙钟时间：16366.64s
- 状态统计：`{"driver_error": 4, "timeout": 14, "verified": 10}`

| 场景 | 性质 | 期望轨迹 | 结果 | 耗时(s) | Tamarin 计时(s) | 步骤 | trace 图（pdf/png） |
|---|---|---|---|---|---|---|---|
| confirmation | `key_confirmation_agreement` |  | driver_error | None |  |  |  |
| confirmation | `key_confirmation_origin` | all-traces | timeout | 3601.915 |  |  |  |
| disclosure_controls | `w2_initiator_confirmation_disclosure_reachable` | exists-trace | timeout | 3600.638 |  |  |  |
| disclosure_controls | `w2_initiator_data_disclosure_reachable` | exists-trace | verified | 1460.55 | 1459.6 | 31 | [pdf](disclosure_controls/w2_initiator_data_disclosure_reachable.trace.pdf) / [png](disclosure_controls/w2_initiator_data_disclosure_reachable.trace.png) |
| disclosure_controls | `w2_initiator_ephemeral_disclosure_reachable` | exists-trace | verified | 1230.938 | 1229.76 | 32 | [pdf](disclosure_controls/w2_initiator_ephemeral_disclosure_reachable.trace.pdf) / [png](disclosure_controls/w2_initiator_ephemeral_disclosure_reachable.trace.png) |
| disclosure_controls | `w2_pending_ephemeral_disclosure_reachable` | exists-trace | timeout | 3602.086 |  |  |  |
| disclosure_controls | `w2_responder_confirmation_disclosure_reachable` | exists-trace | verified | 1445.662 | 1444.51 | 30 | [pdf](disclosure_controls/w2_responder_confirmation_disclosure_reachable.trace.pdf) / [png](disclosure_controls/w2_responder_confirmation_disclosure_reachable.trace.png) |
| disclosure_controls | `w2_responder_data_disclosure_reachable` | exists-trace | verified | 1389.103 | 1388.04 | 31 | [pdf](disclosure_controls/w2_responder_data_disclosure_reachable.trace.pdf) / [png](disclosure_controls/w2_responder_data_disclosure_reachable.trace.png) |
| disclosure_controls | `w2_responder_ephemeral_disclosure_reachable` | exists-trace | verified | 1094.609 | 1093.67 | 32 | [pdf](disclosure_controls/w2_responder_ephemeral_disclosure_reachable.trace.pdf) / [png](disclosure_controls/w2_responder_ephemeral_disclosure_reachable.trace.png) |
| independent_oracles | `w2_initiator_independent_oracles_forward` | exists-trace | timeout | 3602.396 |  |  |  |
| independent_oracles | `w2_initiator_independent_oracles_reverse` | exists-trace | timeout | 3602.88 |  |  |  |
| independent_oracles | `w2_responder_independent_oracles_forward` | exists-trace | timeout | 3602.062 |  |  |  |
| independent_oracles | `w2_responder_independent_oracles_reverse` | exists-trace | timeout | 3602.154 |  |  |  |
| key_separation | `w2_confirmation_key_exposure_data_key_secrecy` | all-traces | timeout | 3601.432 |  |  |  |
| key_separation | `w2_confirmation_key_exposure_plaintext_secrecy` | all-traces | timeout | 3601.05 |  |  |  |
| key_separation | `w2_confirmation_key_exposure_reachable` | exists-trace | verified | 1184.158 | 1182.89 | 27 | [pdf](key_separation/w2_confirmation_key_exposure_reachable.trace.pdf) / [png](key_separation/w2_confirmation_key_exposure_reachable.trace.png) |
| lifecycle | `confirmation_key_unreadable_after_local_erasure` | all-traces | timeout | 3603.245 |  |  |  |
| lifecycle | `data_key_unreadable_after_local_erasure` | all-traces | timeout | 3602.511 |  |  |  |
| lifecycle | `derived_key_lifetime` |  | driver_error | None |  |  |  |
| lifecycle | `ephemeral_state_lifetime` | all-traces | timeout | 3602.241 |  |  |  |
| lifecycle | `ephemeral_unreadable_after_local_erasure` | all-traces | timeout | 3602.963 |  |  |  |
| lifecycle | `erased_secrets_have_prior_creation` | all-traces | timeout | 3602.393 |  |  |  |
| lifecycle | `pending_state_non_reuse_after_erasure` |  | driver_error | None |  |  |  |
| lifecycle | `pre_erasure_state_non_reuse` |  | driver_error | None |  |  |  |
| lifecycle | `session_erasure_requires_both_local_erasures` | all-traces | verified | 308.749 | 307.86 | 79 |  |
| post_erasure | `w2_post_erasure_all_longterm_disclosures_reachable` | exists-trace | verified | 1169.771 | 1168.53 | 36 | [pdf](post_erasure/w2_post_erasure_all_longterm_disclosures_reachable.trace.pdf) / [png](post_erasure/w2_post_erasure_all_longterm_disclosures_reachable.trace.png) |
| post_erasure | `w2_post_erasure_data_key_secrecy` | all-traces | verified | 510.987 | 509.89 | 194 |  |
| post_erasure | `w2_post_erasure_plaintext_secrecy` | all-traces | verified | 533.358 | 532.2 | 207 |  |
