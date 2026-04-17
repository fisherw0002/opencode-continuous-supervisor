# HidenCloud Renew 自动化计划

## 目标
- 页面：`https://dash.hidencloud.com/service/207229/manage`
- 周期：`7 天`
- 触发时间：`Due date 前一天（< 1 day left）`
- 目标动作：点击绿色 `Renew` 按钮

## 当前已确认行为
- 服务 ID：`207229`
- 页面标题区域：`Free Server #207229`
- 关键字段：
  - `Due date`
  - `Last renewal date`
  - `Next Invoice`
- 关键按钮：
  - `Login to Panel`
  - `Copy IP`
  - `Copy UUID`
  - `Renew`
  - `Delete`

## Renew 按钮行为（已人工验证）
### 未到可续费窗口时
- 点击 `Renew` 会弹窗
- 提示内容：
  - `Renewal Restricted`
  - `You can only renew your free service when there is less than 1 day left before it expires.`
  - `Your service expires in 3 days.`
- 此时不会续费成功，`Due date` 不变

### 到可续费窗口后（待自动化实测）
- 已知成功后：`Due date` 会变成 `7 天后的时间`
- 仍待确认：
  - 是否有确认弹窗
  - 是否跳转页面
  - 是否有 toast/成功提示

## 推荐实现路线
1. 优先尝试接口化（后续有空抓 Renew 请求）
2. 当前先做 UI 自动化：
   - 读取 `Due date`
   - 如果今天已经进入 `due - 1 day` 窗口，则点击 `Renew`
   - 识别 `Renewal Restricted` 弹窗/页面文本
   - 成功后校验 `Due date` 是否增加
3. 如果未来再次遇到 CF/登录失效，则人工兜底

## 脚本
- `hidencloud_check_due.py`：只检查到期日
- `hidencloud_auto_renew.py`：自动续费主脚本
  - 默认 dry-run（只判断，不点击）
  - 加 `--run` 才真正点击 `Renew`

## 调度逻辑
- 每天运行一次检查脚本
- 只要 `today >= due_date - 1 day`，就允许尝试续费
- 执行成功后应观察到：`Due date` 增加 7 天
- 需要后续再加：日志去重/避免重复点
