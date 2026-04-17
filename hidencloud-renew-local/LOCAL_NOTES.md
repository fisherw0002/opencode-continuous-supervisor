# 本地运行改造进度

## 已完成
- 从 Epiphany `cookies.sqlite` 提取出 HidenCloud cookie
- 生成 `.env.local`，包含 `HIDEN_COOKIE`
- 复制上游仓库到 `hidencloud-renew-local/`
- 增加本地运行入口：`run_local_check.sh`

## 当前目标
先做一次本地 dry-run / check：
- 验证现有 cookie 是否有效
- 验证能否读取到服务页/续期状态
- 暂不以“必须成功续期”为第一目标

## 后续目标
- 如能正常读到服务状态，则继续限制到你的 service `207229`
- 再决定是否需要补只检查模式 / 定时 / 周计划
