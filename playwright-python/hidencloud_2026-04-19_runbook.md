# HidenCloud 4/19 单次 Renew 执行计划

## 目标
在 **2026-04-19** 自动打开：
`https://dash.hidencloud.com/service/207229/manage`

并执行以下流程：
1. 自动打开目标页
2. 截图 1：目标页（登录后首屏）
3. 守门判断：页面/会话状态是否仍对应 `Due date = 20 Apr 2026`
4. 若不匹配则终止，避免误点
5. 截图 2：点击 Renew 前
6. 自动点击绿色 `Renew`
7. 截图 3：点击 Renew 后
8. 根据页面状态和截图，形成 Word 报告

## 当前实现
- 浏览器：Epiphany（apt 原生）
- 桌面：Xvfb + fluxbox + x11vnc + noVNC
- 点击层：`wmctrl + xdotool`
- 报告层：`python3-docx`

## 产物目录
`/root/.openclaw/workspace/playwright-python/artifacts/hidencloud-renew-2026-04-19/`

预期文件：
- `01-target-page.png`
- `02-before-renew.png`
- `03-after-renew-click.png`
- `run.log`
- `hidencloud-renew-report-2026-04-19.docx`

## 报告用途
- 固化 4/19 当天执行证据
- 看清“点击 Renew 后下一步页面到底长什么样”
- 作为后续生成**每周计划**的依据

## 后续 weekly 计划方向
如果 4/19 报告确认：
- 页面布局稳定
- Renew 后反馈稳定
- 成功判定明确

则下一步可固化为：
- 每周一次执行
- 固定检查 Due date / Last renewal date
- 自动点击 Renew
- 自动生成周报文档
