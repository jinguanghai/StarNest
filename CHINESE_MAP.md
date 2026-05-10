# StarNest 中英文映射表 / Chinese-English Mapping

星巢 (XingChao / StarNest) 架构根植于中医五脏理论 (TCM Five-Organs Theory)。
本文件记录所有中文概念→英文变量名→英文解释的三向映射。

StarNest's architecture is rooted in Traditional Chinese Medicine's Five-Organs Theory.
This document records the three-way mapping: Chinese concepts → English variable names → English explanations.

---

## 核心架构 / Core Architecture

### 五脏 → Five Organs

| 中文 Chinese | 拼音 Pinyin | 英文目录 English Dir | 英文解释 English Explanation |
|---|---|---|---|
| 心 | Xīn | `organs/heart.py` | DMN Scheduler, Signal Hub, FangJi Formula Engine |
| 肝 | Gān | `organs/liver.py` | Three-Layer Memory, Vector Index, Truth Mirror (ZhaoYaoJing) |
| 脾 | Pí | `organs/spleen.py` | Armory (CangJianGe), Tool Matching, Sword Forge (ZhuJianLu) |
| 肺 | Fèi | `organs/lungs.py` | Inquiry Path (WenJianLu), Celestial Command (HunTianLing), Scene Perception |
| 肾 | Shèn | `organs/kidneys.py` | Eight Extremes Diagnosis, Self-Audit Mirror (ZiJingShi), Deep Diagnosis |

### 五境 → Five Classics (Cognition Pipeline)

| 中文 Chinese | 英文 English | 文件 File | 解释 |
|---|---|---|---|
| 正境 | Proper Realm | `protocols/proper_classic.py` | Define problem boundary |
| 反境 | Counter Realm | `protocols/counter_classic.py` | Deconstruct obstacles and risks |
| 合境 | Unity Realm | `protocols/unity_classic.py` | Generate execution plan |
| 超越境 | Transcend Realm | `protocols/transcend_classic.py` | Innovation, harm reduction |
| 本源境 | Origin Realm | `protocols/origin.py` | Archive experience, feedback loop |

### 君臣佐使 → Formula Pattern (Ruler-Minister-Assistant-Envoy)

| 角色 Role | 中文 Chinese | 文件 File | 解释 |
|---|---|---|---|
| 君 (Ruler) | 君 | `protocols/formula.py` | Primary function |
| 臣 (Minister) | 臣 | `protocols/formula.py` | Auxiliary helpers |
| 害 (Harm) | 害 | `protocols/harm_assist.py` | Side effects / risks |
| 佐 (Assist) | 佐 | `protocols/harm_assist.py` | Harm prevention / mitigation |
| 使 (Envoy) | 使 | `protocols/formula.py` | Feedback / notification |

---

## 目录映射 / Directory Mapping

| 原目录 Old Dir | 中文 Chinese | 新目录 New Dir | 英文解释 |
|---|---|---|---|
| `wuzang/` | 五脏 | `organs/` | Five TCM organs (core architecture) |
| `donglixue/` | 动力学 | `dynamics/` | Dynamics engine (8 extremes, π-φ, qi-blood) |
| `jingluo/` | 经络 | `meridian/` | Meridian signal channels (inter-organ communication) |
| `cangjiange/` | 藏剑阁 | `armory/` | Hidden Sword Pavilion (tool repository) |
| `zhixing/` | 执行 | `execution/` | Execution layer (forge, pipeline, task planning) |
| `wujing/` | 五经 | `protocols/` | Five Classics (LLM protocol layer) |
| `zijingshi/` | 自镜室 | `introspection/` | Self-Mirror Room (code introspection) |
| `jiemian/` | 界面 | `interface/` | User interface (celestial command GUI) |
| `jiyi_gongxiang/` | 记忆共享 | `shared_memory/` | Shared memory (lineage / puxi) |
| `jiyi/` | 记忆 | `memory/` | Organ-local memory |
| `huanjing/` | 环境 | `runtime/environment/` | Environment configuration |
| `peizhi/` | 配置 | `runtime/config/` | Configuration files |
| `rizhi/` | 日志 | `runtime/logs/` | Runtime logs |
| `wangluo/` | 网络 | `runtime/network/` | Network layer |
| `jinhua/` | 进化 | `evolution/` | System evolution (copy + upgrade) |
| `bianchengti/` | 编程体 | `bodies/prog_body/` | Programming Body (π, write-permission) |
| `yunxingti/` | 运行体 | `bodies/runtime_body/` | Runtime Body (Ω, read-only) |
| `fuzhiti/` | 附肢体 | `bodies/aux_body/` | Auxiliary Body (φ, sandbox verification) |
| `rukou.py` | 入口 | `star_nest/entry.py` | Entry point |

---

## 关键文件映射 / Key File Mapping

| 原文件 Old File | 中文 Chinese | 新文件 New File | 解释 |
|---|---|---|---|
| `wenjianlu.py` | 问剑路 | `inquiry_path.py` | Inquiry Path: input barrier, pre-detection |
| `zhaoyaojing.py` | 照妖镜 | `truth_mirror.py` | Truth Mirror: malware/virus detection |
| `bajidongli.py` | 八极动力 | `eight_extremes.py` | Eight Extremes Dynamics |
| `jianjinrenzhi.py` | 渐进认知 | `progressive_cognition.py` | Progressive cognition engine |
| `quanjuzhuangtai.py` | 全局状态 | `global_state.py` | Global state vector (19 fields) |
| `qixue_xunhuan.py` | 气血循环 | `qi_blood.py` | Qi-blood circulation cycle |
| `junchenzuoshi.py` | 君臣佐使 | `formula.py` | Formula pattern (Ruler-Minister-Assistant-Envoy) |
| `renzhibao.py` | 认知包 | `cognition_package.py` | RenzhiBao: 3-layer cognition protocol |
| `haizuoxieyi.py` | 害佐协议 | `harm_assist.py` | Harm-Assist protocol |
| `zhujianlu.py` | 铸剑炉 | `forge.py` | Sword Forge: 7-stage code generation |
| `jingluo.py` | 经络 | `channel.py` | Meridian channel: signal hub |
| `qilv.py` | 七律 | `seven_laws.py` | Seven Laws: dynamic rhythm |
| `huntianling.py` | 浑天令 | `celestial_command.py` | Celestial Command: tkinter dark terminal |
| `ceshi_quanbu.py` | 测试全部 | `test_all.py` | Full test suite |
| `ceshi_jiyi.py` | 测试记忆 | `test_memory.py` | Memory test suite |

---

## 六势态 / Six States (Diagnosis Levels)

| 中文 Chinese | 英文 English | 解释 |
|---|---|---|
| 太阳 | TaiYang | Maximum Yang: high confidence, direct execution |
| 阳明 | YangMing | Bright Yang: moderate, confirmation needed |
| 少阳 | ShaoYang | Lesser Yang: low risk, dialogue |
| 太阴 | TaiYin | Maximum Yin: knowledge feeding |
| 少阴 | ShaoYin | Lesser Yin: deep review required |
| 厥阴 | JueYin | Reverting Yin: danger, blocking |

## 三体 / Three Bodies (Trinity Architecture)

| 中文 Chinese | 英文 English | 符号 Symbol | 权限 Permission |
|---|---|---|---|
| 编程体 | Programming Body | π | Read-Write (code generation) |
| 运行体 | Runtime Body | Ω | Read-Only (monitoring) |
| 附肢体 | Auxiliary Body | φ | Read-Only (sandbox verification) |
