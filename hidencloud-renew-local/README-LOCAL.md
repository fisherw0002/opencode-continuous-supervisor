# HidenCloud Renew Local（服务器本地正式版）

## 当前正式方案（已切换）
- **不再**假设每次都从 Epiphany 自动刷新 cookie
- `.env.local` 只作为**初始种子 cookie**来源
- 脚本运行后，上游逻辑会把最新 cookie 滚动写入本地缓存：`hiden_cookies_US.json`
- 下次运行优先使用这个本地缓存 cookie
- 如果 cookie 失效，则报错并停止，等待你手动走一次 VNC 登录，再重新导出 cookie 作为新的种子

## 当前状态
- 已生成：`.env.local`（包含初始 `HIDEN_COOKIE`）
- 本地滚动缓存：`hiden_cookies_US.json`
- 支持多账号：可继续追加 `HIDEN_COOKIE_2`, `HIDEN_COOKIE_3`...
- 只处理目标服务：`TARGET_SERVICE_IDS=207229`

## 多账号预留
参考文件：`.env.accounts.example`

## 定时计划
- 每天 **19:00** 执行一次检查
- 由 systemd timer 触发 `run_scheduled_check.py`
- 检查结束后输出：
  - 完整日志：`logs/scheduled-check.log`
  - 最新简报：`logs/latest-summary.txt`

## cookie 失效后的人工兜底
1. 你手动走一次 VNC 登录 HidenCloud
2. 执行：`bash reseed_cookie_from_vnc.sh`
3. 重新把最新 cookie 写回 `.env.local`
4. 后续定时任务继续用新的种子 cookie + 滚动缓存跑

## 相关文件
- `export_epiphany_hiden_cookie.py`：从 Epiphany 导出 HidenCloud cookie
- `reseed_cookie_from_vnc.sh`：VNC 手动登录后的 cookie 重新播种入口
- `run_local_check.py`：手动检查入口
- `run_scheduled_check.py`：定时检查入口
- `.env.local`：初始种子 cookie + 目标服务配置
- `hiden_cookies_US.json`：滚动更新后的本地 cookie 缓存
- `.env.accounts.example`：多账号模板
- `README-OPS.md`：本地正式版运维手册
- `MAINTENANCE.md`：长期维护说明
