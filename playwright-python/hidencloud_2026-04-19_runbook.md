# HidenCloud 4/19 单次 Renew 执行计划

## 目标
在 **2026-04-19** 自动打开：
`https://dash.hidencloud.com/service/207229/manage`

并执行以下守门逻辑：
1. 登录后的**第一个画面截图**
2. 判断页面/会话状态是否仍对应：`Due date = 20 Apr 2026`
3. 若不匹配，则**终止**，避免误点
4. 若匹配，则继续执行 Renew 流程
5. 点击后**再次截图**
6. 判断是否成功，并保留“成功后的下一步页面状态”证据

## 当前版本（已落地）
已完成：
- 自动打开已登录的 Epiphany 浏览器环境
- 自动截图 `01-before.png`
- 自动检查 session_state 是否仍包含：
  - 目标 URL
  - `20 Apr 2026`
- 自动再截图 `02-after-guard.png`
- 运行日志输出到：
  - `artifacts/hidencloud-renew-2026-04-19/run.log`

## 还差一层（下一步补）
为了真正“自动点击 Renew”，需要补 UI 交互层。当前最稳做法有两个候选：

### 方案 A：xdotool 坐标点击
优点：快，和当前普通浏览器兼容
缺点：依赖窗口位置/分辨率稳定

### 方案 B：切到可编程浏览器 profile（长期更优）
优点：能精确点按钮、读文本、判断成功
缺点：当前 HidenCloud 对服务器环境风控较强，前期成本高

## 推荐落地顺序
1. 先保住 **4/19 自动打开 + 前后截图 + due 守门**
2. 再补一次性点击层（优先 xdotool）
3. 成功后看 4/19 产物里的截图，确认“成功后的下一步页面状态”

## 产物目录
`/root/.openclaw/workspace/playwright-python/artifacts/hidencloud-renew-2026-04-19/`

预期文件：
- `01-before.png`
- `02-after-guard.png`
- `run.log`

## 成功判定（当前定义）
- 最低要求：拿到 4/19 当天的前后截图和日志
- 更高要求：点击后 Due date 不再是 `20 Apr 2026`
- 最终目标：拿到“成功 renew 后页面长什么样”的证据图
