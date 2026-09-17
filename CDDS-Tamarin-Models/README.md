# CDDS Tamarin Models

本目录包含面向零信任云—边—端环境的 CDDS（Cross-Domain Data Sharing）协议两份 Tamarin 源码，用于对照原始 PCE 数据传输方案与 AECDHE 基础修复方案。
## 目录结构

```text
models/
├── original/
│   └── CDDS_PCE_original_full_v4.spthy
└── repaired/
    └── CDDS_AECDHE_repaired_full_v4.spthy
```

## 模型说明

- `original`：完整原协议对照模型。协议规则以 `PT_CDDS.spthy` 为基线，保留域初始化与重配置、主体注册、策略同步、Merkle 状态、访问授权、PCE 数据传输以及攻击者能力，并加入用于对照分析的安全性质。
- `repaired`：基于同一完整基线的基础修复模型。它保留原有攻击者能力和主要协议流程，重点将长期 PCE 公钥封装的数据路径替换为经过授权与 transcript 绑定的临时 Diffie–Hellman 密钥协商，并加入会话状态与临时秘密擦除规则。

修复主要涉及 `Subject_Access_Request`、`Domain_Access_Verification`、`Object_Data_Encryption` 和 `Subject_Data_Decryption` 四条既有规则；其余新增规则用于临时状态、擦除和泄露边界建模。

## 使用方法

安装 [Tamarin Prover](https://tamarin-prover.com/) 后，可在本目录执行：

```bash
tamarin-prover models/original/CDDS_PCE_original_full_v4.spthy --quit-on-warning
tamarin-prover models/repaired/CDDS_AECDHE_repaired_full_v4.spthy --quit-on-warning
```

两份模型中的可达性与安全性质应分别运行和比较。任何安全结论都应以对应源码版本的实际 Tamarin 输出为准。
