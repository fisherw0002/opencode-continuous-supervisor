# opencode-continuous-supervisor：来源、框架、文件与设计依据

## 目标
这个 skill 的目标不是证明 ACP 能不能用，而是解决一个更具体的问题：

> bot 可以拉起 OpenCode / ACP 去干活，但它和 OpenCode 都会停，没有“持续激活机制”。

因此本 skill 聚焦：
1. 持久会话（persistent session）
2. 不绑定聊天（non-chat-bound / no thread bind）
3. 持续激活（watchdog / supervisor / re-prompt / revive）
4. 明确的验收停止条件（acceptance criteria）

---

## 这套思路分别来自哪里

### 一、官方资料直接支持的部分

#### 1. OpenClaw ACP Agents
来源：
- `/usr/lib/node_modules/openclaw/docs/tools/acp-agents.md`

直接支持的结论：
- ACP session 可以是 persistent / session 模式
- 聊天绑定（`--bind here`、`thread: true`、topic/thread binding）是额外路由层，不是 ACP 本体必选项
- 因此“persistent ACP + 不绑定聊天”是成立的

这个 skill 借用了什么：
- 持久 ACP 会话本身是合理的基础能力
- 聊天绑定应该显式禁用，除非用户明确要求

#### 2. OpenClaw Background Tasks
来源：
- `/usr/lib/node_modules/openclaw/docs/automation/tasks.md`

直接支持的结论：
- tasks 是 ledger / tracking，不是 scheduler
- tasks 记录 detached work 的状态：queued / running / succeeded / failed / timed_out / cancelled / lost
- runtime 的真相源应该来自 task / session / stream，而不是用户感受或文件时间

这个 skill 借用了什么：
- watchdog 应优先看 runtime truth source
- `run completed` 不等于 `delivery accepted`
- 监督器不应主要依赖文件 mtime

#### 3. OpenClaw ACP bridge 文档
来源：
- `https://github.com/openclaw/openclaw/blob/main/docs.acp.md`

直接支持的结论：
- ACP bridge 的核心是 session mapping
- ACP world 与 Gateway session world 之间需要稳定映射
- 持续会话要靠 mapping / resume / reuse 才稳定

这个 skill 借用了什么：
- 会话注册表（session registry）是必要层
- repo/project 与 session 之间需要稳定对应关系

---

### 二、社区资料启发的部分

#### 4. opencode-acp-control
来源：
- `https://clawhub.ai/berriosb/opencode-acp-control-3`

直接可借的东西：
- `initialize`
- `session/new`
- `session/load`
- `session/prompt`
- `session/cancel`
- 使用 `stopReason` 作为一轮结束信号
- 显式保存 process/session identifiers

不照搬的部分：
- 裸 background process 控制方式
- 高频轮询本身
- 直接把整套执行层抄进来

在本 skill 里的体现：
- `scripts/opencode-sessionctl.sh`
- `scripts/opencode-watchdog.py`

#### 5. occ (OpenCode Controller)
来源：
- `https://clawhub.ai/gongxh13/occ`

直接可借的东西：
- `query / create / continue` 的思路
- 一个项目尽量复用一条主 session
- server/session 的复用优先于反复新开

不照搬的部分：
- runtime 自动装依赖
- child_process / 本地 server 直控实现
- 把执行层做得过于“野”

在本 skill 里的体现：
- `scripts/opencode-session-registry.py`

#### 6. Mission Control / controller 思路
来源：
- 小妹检索回来的 Reddit / YouTube / community 线索
- 例如：多 OpenCode session 持续运行，需要 mission control / controller

直接可借的东西：
- “光有 session 不够，还要 controller” 这个产品分层
- 持续运行、恢复、重试、续推要有独立控制层

在本 skill 里的体现：
- watchdog / supervise-once / state-machine 的整体结构

---

### 三、来自大王与小弟过去 24 小时聊天的直接经验

这部分不是外部资料，而是本地真实失败/成功样本。

观察到的问题：
1. 一次次新开 `mode: run`，导致一轮一停
2. 一旦出现 thread bind / current-chat bind，聊天容易被劫持
3. 单靠 cron + 文件 mtime 判断，无法真正知道 session 是否卡死 / waiting / terminal
4. 有时 ACP runtime 非绑定聊天其实能正常工作，但仍缺“停了以后继续推”的机制

由这些样本直接推导出的需要：
- 需要 persistent session
- 需要 session registry
- 需要 watchdog
- 需要 acceptance criteria，否则 run 完成不等于任务完成

---

## 目前 skill 里的文件分别干什么

### `SKILL.md`
说明这个 skill 什么时候触发、解决什么问题、包含哪些组件。

### `references/minimal-components.md`
最小组件划分：
- 持久会话控制器
- 会话注册表
- 监督器

### `references/decision-guide.md`
什么时候该选这种架构，什么时候不该。

### `references/state-machine.md`
把 runtime lifecycle 与 supervisor decision 分开：
- lifecycle：active / waiting_bootstrap / stalled / dead
- decision：ok / reprompt / revive

### `scripts/opencode-sessionctl.sh`
半可执行控制器：
- ensure / status / prompt / cancel / close / history / read

### `scripts/opencode-session-registry.py`
项目目录 -> 主 session 名 映射层。

### `scripts/opencode-watchdog.py`
读取 session 状态与近期 history，输出监督判断 JSON。

### `scripts/opencode-supervise-once.sh`
跑一次监督循环：
- registry ensure
- watchdog inspect
- 如有必要，对同一 session 再 prompt 一轮

### `assets/default-continue-prompt.txt`
默认续推 prompt。

---

## 哪些结论是“资料直接支持”的，哪些是“工程推断”的

### 资料直接支持
- ACP 可以 persistent
- ACP 可以不绑定聊天
- tasks 是账本，不是调度器
- controller / mission control 是社区常见补层
- 会话映射 / resume / reuse 是持续工作的关键一环

### 工程推断
- 我们应把 session registry 单独做一层
- watchdog 主要看 task/session/stream truth，而不是 mtime
- `run completed` 只能算一轮结束，不能算真正交付完成
- 需要 acceptance criteria 才能决定什么时候停止自动激活

---

## 当前版本的能力边界

### 已经做到
- 能控制持久 session
- 能给项目稳定分配主 session 名
- 能判断基本的 revive / reprompt / ok
- 能单次自动续推同一条 session

### 还没完全做到
- 完整接入 `openclaw tasks` 解析
- 更细的 waiting/stalled 分类
- 多工作流 acceptance criteria
- 常驻 supervisor / cron / systemd 版本
- bot 集成层

---

## 为什么先做成半可执行 skill，而不是直接接 bot

因为这里最容易犯的错是：
- 先把半成品接到 bot 身上
- 然后一边调 bot，一边调 controller，一边调 watchdog
- 最后根本分不清是哪层在炸

所以先把 skill 本身做成：
- 思路清楚
- 文件齐全
- 脚本能跑
- 再谈接 bot

这是为了降低调试复杂度。
