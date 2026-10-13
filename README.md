# CDDS 协议形式化分析

## 1 本仓库的内容与用途

本仓库是论文《面向零信任云—边—端环境的跨域数据共享（CDDS）协议形式化分析》
 **Tamarin 可复现实验包**。它围绕三条问题线组织证据：
原协议漏洞的**因果归因**、AECDHE 修复所依赖的**认证与信任层条件**、
以及建模限制究竟是**建模假设**还是**协议真实条件**。

**仓库内容**：

| 目录 | 内容 | 文件数 |
|---|---|---:|
| `models/original/` | 原协议完整模型（PCE 数据路径）——论文漏洞结论所依据的对照模型 | 1 |
| `models/repaired/` | AECDHE 修复模型当前最新版，供复现与二次分析 | 1 |
| `models/supplementary/` | 六组补充实验模型（W1–W5、S1）＋ 5 份优化重跑模型 | 24 |
| `results/` | 六组补充实验的逐条运行结果：结论、证明、原始日志与计时；另含 W3/W1 timeout 条目的优化重跑批次 `opt_20260928T175925Z`（原字节归档） | 2030 |

三份模型都以完整源码给出。`results/` 对 W1–W5 与 S1 的每一条性质给出结论、
证明步数、可重放证明文件、原始 stdout／stderr 与完整墙钟时间；
修复模型的 lemma 清单与运行方式见 §3.4。

### 1.1 模型与实验对照

| 组 | 回答的问题 | 模型目录 | 声明性质 | 归档记录 | 归档结果 |
|---|---|---|---:|---:|---|
| **W1** | 历史明文恢复究竟由哪把密钥造成 | `models/supplementary/W1_reveal_matrix` | 66 | 58 | falsified 6，verified 52 |
| **W2** | 擦除后密钥是否确实不可读、确认绑定是否成立 | `models/supplementary/W2_confirmation_lifecycle` | 30 | 27 | timeout 15，verified 12 |
| **W3** | 唯一性限制是建模假设还是协议真实条件 | `models/supplementary/W3_concurrent_agreement` | 144 | 144 | falsified 12，timeout 12，verified 120 |
| **W3 重跑** | 原批次 timeout 条目的优化重试（改写事实名消除状态回环） | `models/supplementary/timeout_optimization` | 24 | 24 | falsified 2，timeout 20，verified 2 |
| **W4** | 复合一致性能否分解为可验证义务 | `models/supplementary/W4_policy_decomposition` | 58 | 58 | verified 58 |
| **W5** | 后继密钥来源与重配置一致性 | `models/supplementary/W5_epoch_successor` | 54 | 54 | falsified 16，verified 38 |
| **S1** | 删除注册—策略顺序限制后目标条件是否仍可导出 | `models/supplementary/S1_restriction_sensitivity` | 28 | 28 | timeout 2，verified 26 |
| **修复模型** | AECDHE 修复后的完整协议，当前最新版 | `models/repaired` | 34 | 源码提供 | 见 §3.4 |

> 「归档记录」列给出本仓库逐条收录的条数，「归档结果」列给出该批次逐条记录的结论分布。
> 预算内未判定的条目计入 `timeout`，与 `verified`／`falsified` 分列统计，口径见 §6。

### 1.2 目录结构

```text
.
├── README.md
├── models/
│   ├── original/CDDS_PCE_original_full.spthy      原协议完整模型
│   ├── repaired/CDDS_AECDHE_repaired.spthy        AECDHE 修复模型（当前最新版）
│   └── supplementary/
│       ├── W1_reveal_matrix/          original_reveal_matrix.spthy
│       │                              repaired_reveal_matrix.spthy
│       ├── W2_confirmation_lifecycle/ repaired_state_lifecycle.spthy
│       ├── W3_concurrent_agreement/   13 份按配置展开的模型
│       ├── W4_policy_decomposition/   policy_decomposition.spthy
│       ├── W5_epoch_successor/        epoch_successor.spthy
│       ├── S1_restriction_sensitivity/registration_policy_order.spthy
│       └── timeout_optimization/      5 份优化重跑模型（4 份 W3 配置 ＋ W1 修复矩阵）
└── results/
    ├── W1/w1_20260928T105641Z/{original,repaired}/<场景>/<性质>.{status.json,proof.spthy,...}
    ├── W2/w2_20260928T084144Z/<场景>/…
    ├── W3/w3_20260928T143228Z/{original,repaired}/<配置>/…
    ├── W4/w4_20260928T141100Z/<profile>/<case>/…
    ├── W5/w5_20260928T151942Z/<profile>/<case>/…
    ├── S1/_run/<profile>/<case>/…
    └── timeout_optimization/opt_20260928T175925Z/{W1,W2,W3}/<配置>/<性质>/<启发式>/…
```

每组 `results/<组>/` 根下另有若干组级运行记录（`commands.json`、`summary.json`、
`run_manifest.json`、`结果汇总.md` 等），记录该批次的工具版本、预算与汇总结论。

---

## 2 环境安装

### 2.1 官方安装方式

Tamarin 需要 **Maude** 与 **Graphviz** 才能运行。官方推荐（参考
[Tamarin 安装页](https://tamarin-prover.com/install.html)）：

```bash
# macOS / Linux（Homebrew，同时装好 Maude 与 Graphviz）
brew install tamarin-prover/tap/tamarin-prover

# Arch Linux
pacman -S tamarin-prover

# 也可直接从 GitHub Releases 下载预编译二进制
# https://github.com/tamarin-prover/tamarin-prover/releases
```

Windows 用户按官方建议使用 **WSL2 + Ubuntu**，在 WSL 内按上面的 Linux 方式安装。

### 2.2 复现本仓库所需的精确版本

本仓库的结果是在下列版本上产生的；**其他版本会产生不同的步数与耗时**，
安全结论（`verified`／`falsified`）通常一致，但引用数字前应固定版本。

| 组件 | 本仓库使用的版本 |
|---|---|
| Tamarin Prover | **1.10.0**（Git revision `cb62c305f8c8b8c1e664152aa33c95b7b8d5ef32`） |
| Maude | **3.1**（Tamarin 要求 ≥ 2.7.1） |
| Graphviz | **2.43.0**（仅用于把反例迹渲染成 PDF/SVG） |

### 2.3 构建指定版本的 Tamarin（推荐用于复现）

要从源码钉住 1.10.0：

```bash
# 1) 先装依赖：Haskell Stack + Maude(>=2.7.1) + Graphviz
#    Debian/Ubuntu 示例（Maude 需从官网获取 3.1 源码编译或使用发行版包）
sudo apt-get install -y graphviz build-essential curl
#    Maude: http://maude.cs.illinois.edu/w/index.php/Maude_download_and_installation
#    Stack: https://docs.haskellstack.org/en/stable/install_and_upgrade/
stack upgrade   # 发行版自带的 stack 往往过旧，必须升级

# 2) 取源码并切到 1.10.0
git clone https://github.com/tamarin-prover/tamarin-prover.git
cd tamarin-prover
git checkout 1.10.0

# 3) 编译（首次约 30–60 分钟，需编译约 120 个依赖）
make default
# 产物：~/.local/bin/tamarin-prover
```

> 本仓库的运行时参数使用了 GHC 的 `+RTS -N<k> -M<size> -RTS`。
> 这些选项要求二进制带 `-rtsopts` 编译；`make default` 与官方预编译包均满足。
> 如果 `+RTS` 被拒绝，说明所用二进制不支持 RTS 选项，需改用源码构建。

### 2.4 验证安装

```bash
tamarin-prover --version
# 期望输出首行为： tamarin-prover 1.10.0, (C) David Basin, ...
# 并应包含：      checking version: 3.1. OK.        (Maude 版本自检)

dot -V            # 期望 graphviz 版本信息
```

### 2.5 本仓库实验所用的实际平台

这些参数记录在各组 `results/<组>/commands.json` 与 `run_manifest.json` 中。

| 项 | 值 |
|---|---|
| 服务器 | `192.168.120.71`（主机名 `lab701-2288H-V5`） |
| 操作系统 | Ubuntu，Linux 内核 6.8.0，x86_64 |
| CPU / 内存 | 80 核 / 503 GB，**无 swap** |
| 并发环境 | 机上有其他租户；快照时 load average 曾达 207/129/82（80 核），**计时受整机负载影响** |
| 工具链 | Tamarin 1.10.0、Maude 3.1、Graphviz 2.43.0、Python 3.10 |

---

## 3 如何运行

以下命令都可直接在任何装好上述工具链的环境里执行；路径均相对于本仓库根目录，
不依赖任何特定机器。

### 3.1 通用调用模板

```bash
tamarin-prover <模型>.spthy \
  --quit-on-warning --derivcheck-timeout=300 \
  --prove=<lemma> \
  [<配置开关>...] [+RTS -N<线程数> -RTS] \
  --output=<lemma>.proof.spthy \
  --output-json=<lemma>.trace.json \
  --output-dot=<lemma>.trace.dot
```

| 参数 | 说明 |
|---|---|
| `--prove=<lemma>` | 只证明指定的那一条性质。**每条性质一次独立进程**，不做同进程复用 |
| `--quit-on-warning` | 遇良构警告立即退出，避免在可疑模型上白跑预算 |
| `--derivcheck-timeout=300` | **必须显式设置**。默认 5 s 对本仓库的模型不足（派生检查约需 40 s），与 `--quit-on-warning` 并用会中止全部性质 |
| `-D<FLAG>` | 预处理开关，选择配置（见各组小节） |
| `+RTS -N<k> -RTS` | GHC 运行时线程数。注意：`-M<size>` 限制的是 GHC 堆，**不是常驻内存上限** |
| `--output-*` | 分别导出可重放证明、迹的 JSON 与 `.dot` 图 |
| `bound=<n>` | 可选，限制搜索深度（原协议早期结果使用过 `bound=50`） |

### 3.2 先过解析门

长跑之前先确认模型良构。此处**故意不带** `--quit-on-warning`，让警告全部打印出来：

```bash
timeout 1800 tamarin-prover models/original/CDDS_PCE_original_full.spthy \
  +RTS -N1 -M16G -RTS --derivcheck-timeout=300 --precompute-only
```

干净输出应依次出现：

```text
[Theory ...] Theory loaded
[Theory ...] Theory translated
[Theory ...] Derivation checks started
[Theory ...] Derivation checks ended
[Theory ...] Theory closed
```

若出现任何 `WARNING` 行，先修模型，不要投入证明预算。

### 3.3 逐组运行参数

| 组 | 模型目录 | 归档批次 | 单条预算 | 并行进程 | 每进程线程 |
|---|---|---|---:|---:|---|
| W1 | `models/supplementary/W1_reveal_matrix` | `w1_20260928T105641Z` | 1800 s（另有覆盖，见表下说明） | 16 | — |
| W2 | `models/supplementary/W2_confirmation_lifecycle` | `w2_20260928T084144Z` | 3600 s | 4 | `+RTS -N4` |
| W3 | `models/supplementary/W3_concurrent_agreement` | `w3_20260928T143228Z` | 3600 s | 8 | — |
| W3 重跑 | `models/supplementary/timeout_optimization` | `opt_20260928T175925Z` | 1800 s／启发式（i/s/S 串行重试） | — | — |
| W4 | `models/supplementary/W4_policy_decomposition` | `w4_20260928T141100Z` | 1800 s | 1 | `+RTS -N2` |
| W5 | `models/supplementary/W5_epoch_successor` | `w5_20260928T151942Z` | 1800 s | 1 | `+RTS -N2` |
| S1 | `models/supplementary/S1_restriction_sensitivity` | `s1_20260929T080037Z` | 600 s | — | — |

**W1 的预算覆盖**（`historical_pce_after_epoch`／`successor_only` → 7200 s，
`key_lifecycle` → 10800 s）在当时**并未实际生效**：补跑脚本调用了错误的驱动路径，
这批条目实际是在 1800 s 下跑的。见 §6 第 4 项。

修复模型的运行方式与 lemma 清单见 §3.4；按 §3.1 模板设定预算与并发数即可。

### 3.4 逐组目标

每组给出一张「模型 × 配置开关 → 性质」对照表。逐条运行就是把表中的
模型文件、开关、lemma 名代入 §3.1 模板。

#### W1 独立密钥泄露矩阵（泄露因果归因）

模型目录：`models/supplementary/W1_reveal_matrix`

下表由归档的 58 条 `status.json` 逐条还原，即**实际跑过的目标**。

| 模型文件 | 配置开关 | RTS | 性质数 | lemma |
|---|---|---|---:|---|
| `original_reveal_matrix.spthy` | — | — | 15 | `w1_o_baseline_key_secrecy`, `w1_o_baseline_plaintext_secrecy`, `w1_o_baseline_reachable`, `w1_o_combined_key_secrecy`, `w1_o_combined_plaintext_secrecy`, `w1_o_combined_reachable`, `w1_o_combined_record_decrypt`, `w1_o_identity_only_key_secrecy`, `w1_o_identity_only_plaintext_secrecy`, `w1_o_identity_only_reachable`, `w1_o_pce_only_key_secrecy`, `w1_o_pce_only_plaintext_secrecy`, `w1_o_pce_only_reachable`, `w1_o_pce_only_record_decrypt`, `w1_o_session_key_disclosure_reachable` |
| `original_reveal_matrix.spthy` | `-DAFTER_EPOCH` | — | 7 | `w1_o_historical_pce_after_epoch_key_secrecy`, `w1_o_historical_pce_after_epoch_plaintext_secrecy`, `w1_o_historical_pce_after_epoch_reachable`, `w1_o_historical_pce_after_epoch_record_decrypt`, `w1_o_successor_only_key_secrecy`, `w1_o_successor_only_plaintext_secrecy`, `w1_o_successor_only_reachable` |
| `repaired_reveal_matrix.spthy` | — | — | 36 | `w1_r_all_identity_domain_key_secrecy`, `w1_r_all_identity_domain_plaintext_secrecy`, `w1_r_all_identity_domain_reachable`, `w1_r_baseline_key_secrecy`, `w1_r_baseline_plaintext_secrecy`, `w1_r_baseline_reachable`, `w1_r_both_domain_key_secrecy`, `w1_r_both_domain_plaintext_secrecy`, `w1_r_both_domain_reachable`, `w1_r_both_identity_key_secrecy`, `w1_r_both_identity_plaintext_secrecy`, `w1_r_both_identity_reachable`, `w1_r_combined_key_secrecy`, `w1_r_combined_plaintext_secrecy`, `w1_r_combined_reachable`, `w1_r_identity_only_key_secrecy`, `w1_r_identity_only_plaintext_secrecy`, `w1_r_identity_only_reachable`, `w1_r_initiator_ephemeral_control_reachable`, `w1_r_initiator_session_key_control_reachable`, `w1_r_kci_reachable`, `w1_r_kci_responder_origin`, `w1_r_pce_only_key_secrecy`, `w1_r_pce_only_plaintext_secrecy`, `w1_r_pce_only_reachable`, `w1_r_requester_domain_key_secrecy`, `w1_r_requester_domain_plaintext_secrecy`, `w1_r_requester_domain_reachable`, `w1_r_responder_domain_key_secrecy`, `w1_r_responder_domain_plaintext_secrecy`, `w1_r_responder_domain_reachable`, `w1_r_responder_ephemeral_control_reachable`, `w1_r_responder_identity_key_secrecy`, `w1_r_responder_identity_plaintext_secrecy`, `w1_r_responder_identity_reachable`, `w1_r_responder_session_key_control_reachable` |

> W1 声明 66 条性质，下表列出归档中已结算的 58 条，即本仓库逐条收录的证明目标；
> 声明总数与已收录条数的对应关系见 §6 第 2 项。

#### W2 确认与状态生命周期

模型目录：`models/supplementary/W2_confirmation_lifecycle`

下表由归档的 27 条 `status.json` 逐条还原，即**实际跑过的目标**。

| 模型文件 | 配置开关 | RTS | 性质数 | lemma |
|---|---|---|---:|---|
| `repaired_state_lifecycle.spthy` | — | — | 3 | `key_confirmation_agreement`, `w2_normal_confirmation_and_erasure`, `w2_responder_erases_before_acceptance` |
| `repaired_state_lifecycle.spthy` | — | `+RTS -N4 -RTS` | 24 | `confirmation_key_unreadable_after_local_erasure`, `data_key_unreadable_after_local_erasure`, `ephemeral_state_lifetime`, `ephemeral_unreadable_after_local_erasure`, `erased_secrets_have_prior_creation`, `key_confirmation_origin`, `session_erasure_requires_both_local_erasures`, `w2_confirmation_key_exposure_data_key_secrecy`, `w2_confirmation_key_exposure_plaintext_secrecy`, `w2_confirmation_key_exposure_reachable`, `w2_initiator_confirmation_disclosure_reachable`, `w2_initiator_data_disclosure_reachable`, `w2_initiator_ephemeral_disclosure_reachable`, `w2_initiator_independent_oracles_forward`, `w2_initiator_independent_oracles_reverse`, `w2_pending_ephemeral_disclosure_reachable`, `w2_post_erasure_all_longterm_disclosures_reachable`, `w2_post_erasure_data_key_secrecy`, `w2_post_erasure_plaintext_secrecy`, `w2_responder_confirmation_disclosure_reachable`, `w2_responder_data_disclosure_reachable`, `w2_responder_ephemeral_disclosure_reachable`, `w2_responder_independent_oracles_forward`, `w2_responder_independent_oracles_reverse` |

#### W3 并发认证与限制消融

模型目录：`models/supplementary/W3_concurrent_agreement`

下表由归档的 144 条 `status.json` 逐条还原，即**实际跑过的目标**。

| 模型文件 | 配置开关 | RTS | 性质数 | lemma |
|---|---|---|---:|---|
| `original_ablated_two.spthy` | — | — | 8 | `data_origin_authentication`, `initiator_aliveness`, `initiator_injective_agreement`, `initiator_noninjective_agreement`, `initiator_weak_agreement`, `reachable_session`, `reachable_two_concurrent_sessions`, `replay_acceptance_exclusion` |
| `original_ablated_unbounded.spthy` | — | — | 8 | `data_origin_authentication`, `initiator_aliveness`, `initiator_injective_agreement`, `initiator_noninjective_agreement`, `initiator_weak_agreement`, `reachable_session`, `reachable_two_concurrent_sessions`, `replay_acceptance_exclusion` |
| `original_local_receiver_two.spthy` | — | — | 8 | `data_origin_authentication`, `initiator_aliveness`, `initiator_injective_agreement`, `initiator_noninjective_agreement`, `initiator_weak_agreement`, `reachable_session`, `reachable_two_concurrent_sessions`, `replay_acceptance_exclusion` |
| `original_local_receiver_unbounded.spthy` | — | — | 8 | `data_origin_authentication`, `initiator_aliveness`, `initiator_injective_agreement`, `initiator_noninjective_agreement`, `initiator_weak_agreement`, `reachable_session`, `reachable_two_concurrent_sessions`, `replay_acceptance_exclusion` |
| `original_multi_ablated_two.spthy` | — | — | 10 | `data_origin_authentication`, `initiator_aliveness`, `initiator_injective_agreement`, `initiator_noninjective_agreement`, `initiator_weak_agreement`, `reachable_session`, `reachable_two_concurrent_sessions`, `reachable_two_distinct_contexts`, `replay_acceptance_exclusion`, `unknown_key_share_exclusion` |
| `original_multi_local_receiver_two.spthy` | — | — | 10 | `data_origin_authentication`, `initiator_aliveness`, `initiator_injective_agreement`, `initiator_noninjective_agreement`, `initiator_weak_agreement`, `reachable_session`, `reachable_two_concurrent_sessions`, `reachable_two_distinct_contexts`, `replay_acceptance_exclusion`, `unknown_key_share_exclusion` |
| `original_multi_restricted_two.spthy` | — | — | 10 | `data_origin_authentication`, `initiator_aliveness`, `initiator_injective_agreement`, `initiator_noninjective_agreement`, `initiator_weak_agreement`, `reachable_session`, `reachable_two_concurrent_sessions`, `reachable_two_distinct_contexts`, `replay_acceptance_exclusion`, `unknown_key_share_exclusion` |
| `original_restricted_two.spthy` | — | — | 8 | `data_origin_authentication`, `initiator_aliveness`, `initiator_injective_agreement`, `initiator_noninjective_agreement`, `initiator_weak_agreement`, `reachable_session`, `reachable_two_concurrent_sessions`, `replay_acceptance_exclusion` |
| `repaired_ablated_two.spthy` | — | — | 14 | `authorization_before_send`, `initiator_aliveness`, `initiator_injective_agreement`, `initiator_noninjective_agreement`, `initiator_weak_agreement`, `reachable_session`, `reachable_two_concurrent_sessions`, `repaired_data_origin_authentication`, `replay_acceptance_exclusion`, `responder_aliveness`, `responder_injective_request_agreement`, `responder_noninjective_request_agreement`, `responder_request_replay_exclusion`, `responder_weak_agreement` |
| `repaired_ablated_unbounded.spthy` | — | — | 14 | `authorization_before_send`, `initiator_aliveness`, `initiator_injective_agreement`, `initiator_noninjective_agreement`, `initiator_weak_agreement`, `reachable_session`, `reachable_two_concurrent_sessions`, `repaired_data_origin_authentication`, `replay_acceptance_exclusion`, `responder_aliveness`, `responder_injective_request_agreement`, `responder_noninjective_request_agreement`, `responder_request_replay_exclusion`, `responder_weak_agreement` |
| `repaired_multi_ablated_two.spthy` | — | — | 16 | `authorization_before_send`, `initiator_aliveness`, `initiator_injective_agreement`, `initiator_noninjective_agreement`, `initiator_weak_agreement`, `reachable_session`, `reachable_two_concurrent_sessions`, `reachable_two_distinct_contexts`, `repaired_data_origin_authentication`, `replay_acceptance_exclusion`, `responder_aliveness`, `responder_injective_request_agreement`, `responder_noninjective_request_agreement`, `responder_request_replay_exclusion`, `responder_weak_agreement`, `unknown_key_share_exclusion` |
| `repaired_multi_restricted_two.spthy` | — | — | 16 | `authorization_before_send`, `initiator_aliveness`, `initiator_injective_agreement`, `initiator_noninjective_agreement`, `initiator_weak_agreement`, `reachable_session`, `reachable_two_concurrent_sessions`, `reachable_two_distinct_contexts`, `repaired_data_origin_authentication`, `replay_acceptance_exclusion`, `responder_aliveness`, `responder_injective_request_agreement`, `responder_noninjective_request_agreement`, `responder_request_replay_exclusion`, `responder_weak_agreement`, `unknown_key_share_exclusion` |
| `repaired_restricted_two.spthy` | — | — | 14 | `authorization_before_send`, `initiator_aliveness`, `initiator_injective_agreement`, `initiator_noninjective_agreement`, `initiator_weak_agreement`, `reachable_session`, `reachable_two_concurrent_sessions`, `repaired_data_origin_authentication`, `replay_acceptance_exclusion`, `responder_aliveness`, `responder_injective_request_agreement`, `responder_noninjective_request_agreement`, `responder_request_replay_exclusion`, `responder_weak_agreement` |

> W3 的模型用 `#ifdef` 表达配置，但 `LOCAL_RECEIVER × UNBOUNDED` 的组合
> `LOCAL_RECEIVER × UNBOUNDED` 的组合需要 `#ifndef`／`#elif`，或让 `#ifdef` 落在
> `#else` 分支内，而 Tamarin 预处理器支持的是更简单的条件展开。因此这里给出
> **按配置展开后的具体模型**：它们就是当时的运行输入，归档 `model_sha256` 与这 13 份一一对应。

#### W3 重跑批次（timeout 条目的优化重试）

模型目录：`models/supplementary/timeout_optimization`；归档批次：`results/timeout_optimization/opt_20260928T175925Z`。

原批次中 12 条 W3 条目在 3600 s 预算内未判定。重跑批次对其中 10 条 W3 目标
（外加 8 条 W1 跨 epoch／后继凭据目标）改用**优化模型**重试：优化模型与上表同名配置模型
仅差事实命名（在事实名内编码一次性泄露权限，消除同名状态回环），逐一对应关系见 §5 哈希表。
每条按 `i`／`s`／`S` 启发式串行重试，单启发式预算 1800 s。

下表由归档的 24 份 `status.json` 逐条还原：

| 目标（配置／lemma） | trace 类型 | 结论 | 步数 |
|---|---|---|---:|
| `ablated_two`／`reachable_two_concurrent_sessions` | exists-trace | verified | 31 |
| `multi_local_receiver_two`／`reachable_two_distinct_contexts` | exists-trace | verified | 26 |
| `multi_ablated_two`／`responder_injective_request_agreement` | all-traces | falsified | 23 |
| `multi_ablated_two`／`responder_request_replay_exclusion` | all-traces | falsified | 23 |
| 其余 20 份重试记录（含 8 条 W1 目标） | — | timeout | — |

**合并口径（与回复信一致）**：原批次 144 条＝120 verified ＋ 12 falsified ＋ 12 timeout，
重跑结算 4 条（2 verified 见证 ＋ 2 falsified responder 候选），合并后并发研究共
**136 条有结论（122 verified ＋ 14 falsified），8 条仍未判定**。

> 注：`multi_ablated_two` 与 `multi_restricted_two` 的 `reachable_two_distinct_contexts`
> 两条，`stdout.log` 已打印 `verified (39 steps)` 且 trace 产物完整，但进程在渲染阶段
> 撞上 1800 s 预算被终止，`status.json` 按保守口径记 `timeout`（`summary.json` 记 verified）。
> 按 `status.json` 口径**不计入**上述合并数；原始证据（`stdout.log`、`result.trace.json`、
> `summary.json`）均在归档中，未做任何改写。

#### W4 跨域策略一致性分解

模型目录：`models/supplementary/W4_policy_decomposition`

下表由归档的 58 条 `status.json` 逐条还原，即**实际跑过的目标**。

| 模型文件 | 配置开关 | RTS | 性质数 | lemma |
|---|---|---|---:|---|
| `policy_decomposition.spthy` | — | `+RTS -N2 -RTS` | 14 | `reachable_b_domain_compromise`, `reachable_b_processing`, `reachable_owner_identity_compromise`, `reachable_policy_installation`, `reachable_proposal`, `reachable_roots`, `w4_a_acceptance_source`, `w4_a_to_b_root_derivation`, `w4_b_processing_source`, `w4_b_to_a_root_derivation`, `w4_matching_context_root_agreement`, `w4_private_a_continuation_source`, `w4_private_b_continuation_source`, `w4_proposal_source` |
| `policy_decomposition.spthy` | `-DKEEP_POLICY_RESTRICTIONS` | `+RTS -N2 -RTS` | 14 | `reachable_b_domain_compromise`, `reachable_b_processing`, `reachable_owner_identity_compromise`, `reachable_policy_installation`, `reachable_proposal`, `reachable_roots`, `w4_a_acceptance_source`, `w4_a_to_b_root_derivation`, `w4_b_processing_source`, `w4_b_to_a_root_derivation`, `w4_matching_context_root_agreement`, `w4_private_a_continuation_source`, `w4_private_b_continuation_source`, `w4_proposal_source` |
| `policy_decomposition.spthy` | `-DMULTI_CONTEXT` | `+RTS -N2 -RTS` | 15 | `reachable_alternative_context`, `reachable_b_domain_compromise`, `reachable_b_processing`, `reachable_owner_identity_compromise`, `reachable_policy_installation`, `reachable_proposal`, `reachable_roots`, `w4_a_acceptance_source`, `w4_a_to_b_root_derivation`, `w4_b_processing_source`, `w4_b_to_a_root_derivation`, `w4_matching_context_root_agreement`, `w4_private_a_continuation_source`, `w4_private_b_continuation_source`, `w4_proposal_source` |
| `policy_decomposition.spthy` | `-DMULTI_CONTEXT -DKEEP_POLICY_RESTRICTIONS` | `+RTS -N2 -RTS` | 15 | `reachable_alternative_context`, `reachable_b_domain_compromise`, `reachable_b_processing`, `reachable_owner_identity_compromise`, `reachable_policy_installation`, `reachable_proposal`, `reachable_roots`, `w4_a_acceptance_source`, `w4_a_to_b_root_derivation`, `w4_b_processing_source`, `w4_b_to_a_root_derivation`, `w4_matching_context_root_agreement`, `w4_private_a_continuation_source`, `w4_private_b_continuation_source`, `w4_proposal_source` |

#### W5 epoch 与后继密钥

模型目录：`models/supplementary/W5_epoch_successor`

下表由归档的 54 条 `status.json` 逐条还原，即**实际跑过的目标**。

| 模型文件 | 配置开关 | RTS | 性质数 | lemma |
|---|---|---|---:|---|
| `epoch_successor.spthy` | — | `+RTS -N2 -RTS` | 11 | `accepted_epoch_has_started_candidate`, `classified_successor_origin`, `domain_reconfiguration_agreement`, `domain_successor_key_authentication`, `epoch_successor_origin`, `reachable_disclosure_before_acceptance`, `reachable_honest_update`, `reachable_old_key_disclosure`, `reachable_repeated_acceptance`, `successor_acceptance_injective_candidate`, `unconditional_successor_authentication_candidate` |
| `epoch_successor.spthy` | `-DSECOND_UPDATE` | `+RTS -N2 -RTS` | 14 | `accepted_epoch_has_started_candidate`, `classified_successor_origin`, `domain_reconfiguration_agreement`, `domain_successor_key_authentication`, `epoch_successor_origin`, `historical_update_freshness_candidate`, `reachable_disclosure_before_acceptance`, `reachable_historical_reacceptance`, `reachable_honest_update`, `reachable_old_key_disclosure`, `reachable_repeated_acceptance`, `reachable_two_honest_updates`, `successor_acceptance_injective_candidate`, `unconditional_successor_authentication_candidate` |
| `epoch_successor.spthy` | `-DSPECIAL_ATTACK` | `+RTS -N2 -RTS` | 13 | `accepted_epoch_has_started_candidate`, `classified_successor_origin`, `domain_reconfiguration_agreement`, `domain_successor_key_authentication`, `epoch_successor_origin`, `reachable_disclosure_before_acceptance`, `reachable_honest_update`, `reachable_old_key_disclosure`, `reachable_repeated_acceptance`, `reachable_special_update`, `special_without_disclosure_authentication_candidate`, `successor_acceptance_injective_candidate`, `unconditional_successor_authentication_candidate` |
| `epoch_successor.spthy` | `-DSPECIAL_ATTACK -DSECOND_UPDATE` | `+RTS -N2 -RTS` | 16 | `accepted_epoch_has_started_candidate`, `classified_successor_origin`, `domain_reconfiguration_agreement`, `domain_successor_key_authentication`, `epoch_successor_origin`, `historical_update_freshness_candidate`, `reachable_disclosure_before_acceptance`, `reachable_historical_reacceptance`, `reachable_honest_update`, `reachable_old_key_disclosure`, `reachable_repeated_acceptance`, `reachable_special_update`, `reachable_two_honest_updates`, `special_without_disclosure_authentication_candidate`, `successor_acceptance_injective_candidate`, `unconditional_successor_authentication_candidate` |

#### S1 注册—策略顺序限制消融

模型目录：`models/supplementary/S1_restriction_sensitivity`

下表由归档的 28 条 `status.json` 逐条还原，即**实际跑过的目标**。

| 模型文件 | 配置开关 | RTS | 性质数 | lemma |
|---|---|---|---:|---|
| `registration_policy_order.spthy` | — | — | 14 | `access_grant_correspondence`, `access_request_registration_source`, `policy_acceptance_source`, `policy_context_root_agreement`, `policy_domains_distinct`, `policy_processing_source`, `reachable_access_grant`, `reachable_policy_installation`, `reachable_registration`, `reachable_request_before_policy`, `reachable_same_domain_registration`, `registration_issuance_correspondence`, `registration_precedes_policy`, `subject_before_policy_full_candidate` |
| `registration_policy_order.spthy` | `-DKEEP_ORDER` | — | 14 | `access_grant_correspondence`, `access_request_registration_source`, `policy_acceptance_source`, `policy_context_root_agreement`, `policy_domains_distinct`, `policy_processing_source`, `reachable_access_grant`, `reachable_policy_installation`, `reachable_registration`, `reachable_request_before_policy`, `reachable_same_domain_registration`, `registration_issuance_correspondence`, `registration_precedes_policy`, `subject_before_policy_full_candidate` |

> S1 的两组只用 `-DKEEP_ORDER` 一条开关区分：带该开关＝保留
> `Subject_before_PolicyRegister` 限制（`restricted`），不带＝删除该限制（`ablated`）。
> 归档命令以默认线程数执行。

#### 修复模型 CDDS_AECDHE_repaired.spthy

模型目录：`models/repaired`

| 项 | 值 |
|---|---|
| 内部 theory 名 | `CDDS_matched_v8` |
| 规模 | 28 rule／21 restriction／34 lemma |
| 覆盖内容 | 域初始化与重配置、主体注册、策略同步、Merkle 状态、访问授权、AECDHE 数据路径与擦除规则 |

运行方式与 §3.1 模板相同，`--prove` 取下面清单中的 lemma 之一，例如：

```bash
tamarin-prover models/repaired/CDDS_AECDHE_repaired.spthy \
  --quit-on-warning --derivcheck-timeout=300 \
  --prove=repaired_standard_forward_secrecy \
  --output=repaired_standard_forward_secrecy.proof.spthy
```

逐条运行后，每条 lemma 的结论与耗时按 §3.6 的文件形式落盘，便于与本仓库
`results/` 中六组补充实验的记录并列比较。

模型内声明的 34 条 lemma：

| # | lemma |
|---:|---|
| 1 | `v7_accept_has_request` |
| 2 | `policy_processing_has_matching_proposal` |
| 3 | `policy_acceptance_has_matching_processing` |
| 4 | `policy_acceptance_installs_matching_roots` |
| 5 | `Cross_Domain_Policy_Consistency` |
| 6 | `repaired_ephemeral_i_reveal_has_creation` |
| 7 | `repaired_ephemeral_r_reveal_has_creation` |
| 8 | `repaired_lowe_data_noninjective_agreement` |
| 9 | `repaired_commit_is_single_use` |
| 10 | `repaired_completed_session_key_secrecy_after_erasure` |
| 11 | `repaired_completed_plaintext_secrecy_after_erasure` |
| 12 | `repaired_conditional_data_origin` |
| 13 | `repaired_lowe_data_injective_agreement` |
| 14 | `repaired_conditional_session_key_secrecy` |
| 15 | `repaired_conditional_data_secrecy` |
| 16 | `Init_before_Register` |
| 17 | `Executable` |
| 18 | `secrecy_session_key` |
| 19 | `secrecy_x` |
| 20 | `secrecy_subject_sk` |
| 21 | `secrecy_domain_sk` |
| 22 | `forward_secrecy_x` |
| 23 | `authentication_registration` |
| 24 | `authentication_access_grant` |
| 25 | `authentication_data_cert` |
| 26 | `authentication_data_origin` |
| 27 | `repaired_authorization_before_send` |
| 28 | `repaired_lowe_data_aliveness` |
| 29 | `repaired_lowe_data_weak_agreement` |
| 30 | `repaired_session_key_secrecy_after_erasure` |
| 31 | `repaired_standard_forward_secrecy` |
| 32 | `repaired_intra_epoch_compromise_resilience` |
| 33 | `repaired_cross_epoch_key_compromise_isolation` |
| 34 | `Cross_Domain_Policy_Consistency_legacy` |

### 3.5 批量运行

不依赖任何包装脚本即可跑完全部性质。以 W1 为例，用 shell 循环即可：

```bash
MODEL=models/supplementary/W1_reveal_matrix/original_reveal_matrix.spthy
OUT=out/W1 && mkdir -p "$OUT"

# 逐条：预算 1800 s，超预算由 timeout 终止（exit 124）
for lemma in w1_o_baseline_key_secrecy w1_o_pce_only_key_secrecy \
             w1_o_pce_only_plaintext_secrecy w1_o_identity_only_plaintext_secrecy; do
  timeout 1800 tamarin-prover "$MODEL" \
    --quit-on-warning --derivcheck-timeout=300 \
    --prove="$lemma" \
    --output="$OUT/$lemma.proof.spthy" \
    --output-json="$OUT/$lemma.trace.json" \
    --output-dot="$OUT/$lemma.trace.dot" \
    >"$OUT/$lemma.stdout.log" 2>"$OUT/$lemma.stderr.log"
done
```

带配置开关时把开关插在 `--prove` 之后，例如 W5 的 special 配置：

```bash
tamarin-prover models/supplementary/W5_epoch_successor/epoch_successor.spthy \
  --quit-on-warning --derivcheck-timeout=300 \
  --prove=classified_successor_origin -DSPECIAL_ATTACK +RTS -N2 -RTS \
  --output=classified_successor_origin.proof.spthy
```

W3 的 13 份配置模型已经把开关展开进文件，**不要**再叠加 `-D`。

### 3.6 输出文件说明

| 文件 | 内容 |
|---|---|
| `<lemma>.stdout.log` | Tamarin 标准输出，含 `verified`／`falsified` 结论与证明步数 |
| `<lemma>.stderr.log` | 阶段标记。出现 `[Saturating Sources] Done` 表示预计算完成、已进入证明搜索；**从未出现该标记的条目卡在预处理**，与搜索耗尽是不同的失败模式 |
| `<lemma>.proof.spthy` | 可重放的证明文件 |
| `<lemma>.time.txt` | UTC 起止、墙钟秒数、完整命令行、工作目录 |
| `<lemma>.status.json` | 机读结论：状态、步数、Tamarin 自报时间、墙钟时间、运行时模型 SHA-256 |
| `<lemma>.trace.json` / `.trace.dot` | 反例／见证迹，运行期产物；需要矢量图时用下面的 `dot` 命令转换 |

迹图渲染（需要 Graphviz）：

```bash
dot -Tpdf <lemma>.trace.dot -o <lemma>.trace.pdf
```

注意：`--output-dot` **只在找到反例时**才产出非空迹；全 `verified` 或全部超预算的运行
会产生零字节 `.dot` 文件，这是预期行为，不是工具故障。

---

## 4 结果与口径

### 4.1 归档结果分布

| 组 | 归档记录 | verified | falsified | timeout |
|---|---:|---:|---:|---:|
| W1 | 58 | 52 | 6 | 0 |
| W2 | 27 | 12 | 0 | 15 |
| W3 | 144 | 120 | 12 | 12 |
| W3 重跑（`opt_20260928T175925Z`） | 24 | 2 | 2 | 20 |
| W4 | 58 | 58 | 0 | 0 |
| W5 | 54 | 38 | 16 | 0 |
| S1 | 28 | 26 | 0 | 2 |

**三种终态必须分开**，混写会误报结论：

| 结论 | 含义 |
|---|---|
| `verified` | 该性质在模型所有被承认的迹上成立；若 lemma 是 `exists-trace`，表示找到所指定见证 |
| `falsified` | `all-traces` 找到反例迹（即攻击）；`exists-trace` 表示所指定见证不可达 |
| `timeout` | 预算内未判定。**既不是成立，也不是反例** |

**时间口径**：报告的是**完整墙钟时间**（装载 + 派生检查 + 预计算 + 依赖证明 + 目标证明）。
Tamarin 自报的 `processing time` 单列，**不称**为“纯证明时间”。
并发数与整机负载会显著影响耗时，必须与时间一起报告。

### 4.2 各组结论的覆盖范围

| 组 | 结论覆盖 |
|---|---|
| W1 | 泄露因果归因对照（无泄露／仅身份签名密钥／仅 PCE 密钥）与长期凭据泄露矩阵；跨 epoch 条目在模型的 epoch 转换与持久事实语义下评估 |
| W2 | 单向显式密钥确认的绑定与擦除后的密钥不可读边界，与模型中的显式擦除规则一一对应 |
| W3 | 唯一性限制的保留与消融成对对照；`restricted_*`／`ablated_*` 配置在诚实密钥条件下评估认证性质 |
| W4 | 六项策略一致性分解义务，覆盖四个配置 |
| W5 | 后继密钥来源、认证与重配置一致性。16 条 `falsified` 落在模型设计时**预先声明的诊断候选**上（`unconditional_successor_authentication_candidate`、`successor_acceptance_injective_candidate`、`accepted_epoch_has_started_candidate`、`special_without_disclosure_authentication_candidate`、`historical_update_freshness_candidate`），用于定位认证边界：其中 `unconditional_...candidate` 被反驳而 `domain_successor_key_authentication` 成立，两者并列说明该认证保证**正依赖**“排除泄露与特殊转换”这两个前提 |
| S1 | 注册—策略顺序限制的成对对照：在所保留的规则与共同限制下，目标条件仍可导出 |

W1–W5 与 S1 是从完整模型派生的**辅助切片**（固定域数、注册与策略同步压缩为前置接口等），
每组结论与其模型声明的配置范围绑定，模型内的 lemma 公式即结论的精确表述。
所有前向保密类结论均建立在 Tamarin 符号模型、显式 compromise 规则、
事件顺序与临时秘密擦除假设之上。

### 4.3 证据支撑的论文主张

| 证据 | 论文落点 |
|---|---|
| W1 泄露因果归因三对照（无泄露／仅身份密钥／仅 PCE 密钥） | 反例归因一节、历史密钥结果行 |
| W1 长期凭据泄露矩阵（11 组组合） | 修复矩阵概括分类 |
| W2 确认对应与擦除后保密 | 确认绑定一节、擦除边界一节 |
| W3 限制消融（144 项） | 建模限制讨论、认证性质与修复讨论 |
| W3 重跑批次（合并口径 136 条有结论） | 回复信并发研究汇总（122 verified ＋ 14 falsified，8 条未判定） |
| W4 六项策略一致性分解义务 | 跨域策略链一节 |
| W5 后继密钥与重配置义务 | 后继密钥与重配置一节 |
| S1 顺序限制消融 | 建模限制讨论 |

完整泄露矩阵逐 case、144 项并发清单、限制逐条分类、事件参数全表与反例可视化轨迹
**不进正文**，全部留在本仓库与回复信材料中。

---

## 5 模型哈希与换行符

本仓库的模型文件统一使用 **LF** 换行。归档时驱动脚本在 Windows 暂存目录先算哈希再上传，
因此归档 `status.json` 里记录的 `model_sha256` 对应的是**暂存换行形态**：

| 组 | 归档原始换行形态 |
|---|---|
| W1、W2、W4、W5、原协议主模型 | CRLF |
| **W3 的 13 份配置模型** | **CRCRLF**（`\r\r\n`，生成器在 Windows 上的产物） |
| S1 | 源文件 CRLF，归档哈希按 **LF** 计算 |

除换行符与下述一行注释外内容逐字节相同。整理发布时，六组补充模型的文件头各删除了
一行起草期遗留的状态注释（与归档运行结果相矛盾，如 `AUTHORED, NOT TAMARIN PARSED OR PROVED.`）。
核对哈希时先把该行按原位置补回（均在文件头注释块内），再换成上表对应的换行形态
计算 SHA-256，即可与 `status.json` 对上。各组删除的行：

| 组 | 删除的行 |
|---|---|
| W1（两份） | `Status: authored; NOT parsed or proved by Tamarin in this environment.` |
| W2 | `Authored only: official Tamarin parsing/proofs have not been run.` |
| W4 | `Status: authored; NOT Tamarin parsed or proved.` |
| W5 | `AUTHORED: NOT TAMARIN PARSED OR PROVED.` |
| S1 | `AUTHORED, NOT TAMARIN PARSED OR PROVED.` |
| W3（13 份） | `AUTHORED, NOT TAMARIN PARSED OR PROVED. See ../README.md.` |

> 注：W3 的 13 份模型在归档换行转换后每行之后多出一个空行；核对 W3 哈希时，
> 需先把相邻空行坍缩回单倍行距，再补回上表所列行并转成 CRCRLF。

| 模型文件 | 归档原始换行 | SHA-256（本仓库 LF 字节） | 归档 `model_sha256` | 匹配 |
|---|---|---|---|---|
| `original/CDDS_PCE_original_full.spthy` | CRLF | `b0a692c3a518cc26db8dd8e36534b8f72c5daa40f88a195ce525bbae5b53df9c` | — | —（非运行输入） |
| `models/repaired/CDDS_AECDHE_repaired.spthy` | CRLF | `e4f7338893c6a383c1150d796c233065a10e86d7fe4f3459aa781af94f524ec0` | — | 源码收录 |
| `S1_restriction_sensitivity/registration_policy_order.spthy` | CRLF | `5ee94370f1dd9e93143e7428e3b05b04a1d4f0f9b8cbc3c1083d7ea944ed9318` | `254AD0565A61DB5756F397C590925ADFD838D7AFF51DC4620FED7AE71B2EFDBB` | LF ✅ |
| `W1_reveal_matrix/original_reveal_matrix.spthy` | CRLF | `f75de34cd300f12bb5780e679698a69fd2869d2762730e395c9e1aa38e660b32` | `24A034C4684072BDCC89E073404302D93E5B9EB2D4A936DAF160E479914DF7C5` | CRLF ✅ |
| `W1_reveal_matrix/repaired_reveal_matrix.spthy` | CRLF | `f172fe578c1c3117606f7f3171366fa6f0567f6f2dbb712b2b41a620a5eeb8d3` | `0A052A26A0E30B475034F0CCDFC7D8EEEA994B611F6200B859902800C515B916` | CRLF ✅ |
| `W2_confirmation_lifecycle/repaired_state_lifecycle.spthy` | CRLF | `c349f95bc7e5c0bf9b216b1cb8c24a26d768b798ac2d20620b0bc74401b52035` | `14E941343C02EB549AC53CB568E14742E6B3F525A3873170A1160887BDEE19F9` | CRLF ✅ |
| `W3_concurrent_agreement/original_ablated_two.spthy` | CRCRLF | `70103b71225756319944465c4b506cb7d1e7486cf0aeebeed4ecd0dd4f3107cd` | `83F325D77C2511C31C2312058FF92D5A58EE5406FCE048E1CF888571F24AF5E4` | CRCRLF ✅ |
| `W3_concurrent_agreement/original_ablated_unbounded.spthy` | CRCRLF | `7c731ee7c2fa22d9dfd2af90405350463a13da4f35c59430e82c8e183548aae4` | `209E037C09BE01F20F0CAA8A31945C8EA86C6E13CED7DD3781A9B861EDE167FA` | CRCRLF ✅ |
| `W3_concurrent_agreement/original_local_receiver_two.spthy` | CRCRLF | `928e9bf009248b67ae2f3f2252ae1b585179018e3ded29b8d380b44883b10a65` | `1B102FAE46B7A9FD8714A359B5BDB7D2663DACD5B75E0C1D6799ABC2D6DC0B36` | CRCRLF ✅ |
| `W3_concurrent_agreement/original_local_receiver_unbounded.spthy` | CRCRLF | `5390b9d10d0b6040e85d16bb7fd1ada0c6b129401ac1f3d699df62c763b437cd` | `7EF466292A4FDB8CDD279E1B5FFE47B8B305720DEC72AAFCEA9DBA003B717A92` | CRCRLF ✅ |
| `W3_concurrent_agreement/original_multi_ablated_two.spthy` | CRCRLF | `a87e6a6bbbac39e63e6cb5b968546a3b4e117a1c4cc47342c0bcb6affb39a3fa` | `72A905E72534A6E02030AFAD763DDAA27018031DB4E0CD24B91D979929021D01` | CRCRLF ✅ |
| `W3_concurrent_agreement/original_multi_local_receiver_two.spthy` | CRCRLF | `e3380dfa64ff568528b606d80e15457c0687c94a50a30a09cc8084744992dd5f` | `4B87C79AC1533E35B8C271ECEC4266701E2F41DDAF5EC4D581F4C7D074B311B1` | CRCRLF ✅ |
| `W3_concurrent_agreement/original_multi_restricted_two.spthy` | CRCRLF | `92402b9271a904f775e0766a8125d2a648c7898062de1738bccd6b67a0c0725b` | `9C1CA31AD45C87F8E0B6969470394C84F94DE3866C296EE0C79ECEE6A1E9C7EC` | CRCRLF ✅ |
| `W3_concurrent_agreement/original_restricted_two.spthy` | CRCRLF | `9b8555fad0ce8f04342a21f513024c94c2e46210f85a816cbcb2bd6b925613ce` | `EDB51BBFCE2EBAF1B7124F877487698CC2F164CB98CE49564C7EFFEA5AD4F079` | CRCRLF ✅ |
| `W3_concurrent_agreement/repaired_ablated_two.spthy` | CRCRLF | `6f27fe4bbecc621a92d01548f05fb933ae666d0e67ef7bab70b69695794346c5` | `5C8A230412F8C78B5B8CC1683AB026A31FF2FB5DDF23599DE6D871270CB5EB30` | CRCRLF ✅ |
| `W3_concurrent_agreement/repaired_ablated_unbounded.spthy` | CRCRLF | `972bf4cd9f742f01dcc45e8cf8e07aacb1ca0d04885bc6cc722a2690357978c4` | `552B218D0FCC31149751E63F80AD1A6452B671E1072A6DDE297178F62238BA53` | CRCRLF ✅ |
| `W3_concurrent_agreement/repaired_multi_ablated_two.spthy` | CRCRLF | `86063ce1b639d7db1d48fa6d15d09edf6d28d68f1b6f0bac61bb30dc07654f79` | `ACA48EC21EB0A86C257B3E7A813F73840F624A6E3311EEC733FD2BE0E0AB2C53` | CRCRLF ✅ |
| `W3_concurrent_agreement/repaired_multi_restricted_two.spthy` | CRCRLF | `5fa89e16d6f1f5a1cece23dff6efa929fb084df4912e2db787829d12eb9a13c4` | `8E215453CB006B1932002067ED6EB9BF0F489015AFEDE6E1183DBB4970550F9B` | CRCRLF ✅ |
| `W3_concurrent_agreement/repaired_restricted_two.spthy` | CRCRLF | `0c543aff0f1fe7e819855c6d444cf338d918ffceb4f5d41949d36c1d38185f5d` | `65DA901B8125697481675E0B066CA20DA217FB56FCDD27E074D6783E4B7968F7` | CRCRLF ✅ |
| `W4_policy_decomposition/policy_decomposition.spthy` | CRLF | `883ae8c3a124f7a775dc9dd7f8d98f0c9bd70891820ac6b453310c691a17af62` | `938E678F07C657511627B12B543235AC9FD0639E0FDA8FFBF31F7AEDA18DEE06` | CRLF ✅ |
| `W5_epoch_successor/epoch_successor.spthy` | CRLF | `7270f738253b9b314025f978305a7f2da45236b5aeafe79884cc4d7a9c0d8f93` | `9FF5A592164B07ADD83BA67E234952C03E982393DC91E6BFF23265EBE6083BE2` | CRLF ✅ |

`timeout_optimization/` 下的 5 份优化重跑模型与上表同名配置模型**仅差事实命名**
（事实名内编码一次性泄露权限），是重跑批次 `opt_20260928T175925Z` 的实际运行输入。
它们**未删除任何状态注释行**（文件头本无起草期戳），核对哈希只需 LF→CRLF 换行转换；
注意该批次 `status.json` 的 `model_sha256` 以**小写**十六进制存储：

| 模型文件 | 归档原始换行 | SHA-256（本仓库 LF 字节） | 归档 `model_sha256` | 匹配 |
|---|---|---|---|---|
| `timeout_optimization/repaired_ablated_two.spthy` | CRLF | `7a65316a7c3444f9814356c65ee3d804d2f27de7f2a67fc047f2711831f785b5` | `f17cc98f281a455bd5d5099ea45dfacbd1852482f01aed9ccddaf366c6c9491c` | CRLF ✅ |
| `timeout_optimization/repaired_multi_ablated_two.spthy` | CRLF | `980265a2db409a4f84b2ffc3e417521a851423ac8a9f8602dcd8256136fdeb58` | `d61606dd5fec5ba0b7c1c11295198533630b9a40c97c8860d40b8d7d6b8bc112` | CRLF ✅ |
| `timeout_optimization/repaired_multi_restricted_two.spthy` | CRLF | `8da9d873b751253f1e05ab5e2cff86e0c747f41a9d665e5eb5a4eb181a5e107e` | `78f971ca026ba9f62fae946f3ae37805c6e1c1b32580ffa1be991c3e42049337` | CRLF ✅ |
| `timeout_optimization/original_multi_local_receiver_two.spthy` | CRLF | `940e266a2f614ef2e92d1440093c968d35a648b7338a519f2e55bfc384dc06c7` | `2e5f97231d82f8d188c0825b997b0b9c82ad5d2f23c128aea7523f5a677088e5` | CRLF ✅ |
| `timeout_optimization/repaired_reveal_matrix.spthy` | CRLF | `06bb40f59fcaf0d03f7341db879e102d23e630aae5f6fdf0c5995f9e863c1899` | `92ca718daef77a0be2c06825cbb3cc19718d318311034cd36662c656975b6966` | CRLF ✅ |

结果文件（`status.json`、日志、trace 产物与逐条模型快照）未做任何内容改写，
仓库按 §5 口径统一以 LF 存储；重跑批次内的 `.spthy` 快照在暂存盘为 CRLF，
其归档哈希对应 CRLF 字节（§5 表）。

> **文件命名**：模型文件名不带版本号，便于长期引用与稳定链接。原协议模型对应归档中的
> `CDDS_PCE_original_full_v4.spthy`，修复模型对应 `CDDS_AECDHE_repaired_optimized_v8.spthy`；
> 内容与来源逐字节一致，仅换行符按上表归一化为 LF。修复模型内部的 theory 名为
> `CDDS_matched_v8`，保留原名以便与历史记录逐条交叉核对。

---

## 6 记录口径

本仓库逐条收录各组批次的归档记录，并在此列出与历史材料对齐时需要用到的口径。

| # | 事项 | 口径 |
|---|---|---|
| 1 | W2 批次 | 以本仓库归档的逐条记录为准：27 条 `status.json`（verified 12／timeout 15）。同批次 `run_manifest.json` 记 finished 28，作者《实验总账》记性质数 30、已结算 25（成立 19／反例 2／未判定 4）；三套口径并列可查 |
| 2 | W1 范围 | W1 声明 66 条性质，本仓库收录归档中已结算的 58 条（verified 52／falsified 6）；作者《实验总账》另记 8 条未结算，其 `unsettled` 清单见该批次 `包索引.json` |
| 3 | 原协议 lemma 名 | 以本仓库 `CDDS_PCE_original_full.spthy` 中的声明为准（含 `forward_secrecy_x`）；更早的 `v0/proof_logs/v4验证结果汇总.md` 使用过不同的命名 |
| 4 | W1 长预算 | 驱动中的预算覆盖值为 7200 s（`historical_pce_after_epoch`、`successor_only`）与 10800 s（`key_lifecycle`）；每条归档条目的完整墙钟时间与命令行见对应 `time.txt` |
| 5 | W2 批次身份 | 收录批次为 `w2_20260928T084144Z`，批次内的暂停与恢复过程完整保留在该组的 `pause_record.md` |
| 6 | 证明文件覆盖 | W1 58、W4 58、W5 54、W3 133、S1 26、W2 12 条附 `proof.spthy`；超预算条目按设计不产出证明文件，其未判定状态记录在 `status.json` 的 `timeout` 字段 |
| 7 | W3 合并口径 | 回复信的并发研究汇总合并原批次与重跑批次：144（120 verified／12 falsified／12 timeout）＋重跑结算 4（2 verified／2 falsified）＝ **136 条有结论（122／14），8 条未判定**。另有 2 条重跑目标（`multi_ablated_two`、`multi_restricted_two` 的 `reachable_two_distinct_contexts`）stdout 已打印 verified 但进程在渲染阶段超预算，按 `status.json` 保守口径未计入，证据未改写（见 §3.4 重跑小节注） |

---

## 7 引用与许可

使用本仓库的模型或结果，请引用对应论文（DOI／卷期待补）。
使用 Tamarin Prover 请引用其官方文献，本仓库使用 **1.10.0**。

