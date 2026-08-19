# Baseline-Library-2026-08-19

## Summary

| Metric | Value |
| --- | --- |
| Total Cases | 7 |
| Source Query | baseline-library-push |

## Cases

| Test Case ID | Case Name | Module | Priority | Status | Severity | Platform | Match Score |
| --- | --- | --- | --- | --- | --- | --- | ---: |
| BL-24172 | 操作员查看指定岸桥的实时作业视图 | 岸桥终端监控 | High | Active | high | Web | 100.0 |
| BL-25503 | qcvmt login | login | High | Active | high | Web | 100.0 |
| BL-24178 | 正确显示加油区域高亮标识 | 岸桥终端监控 | Medium | Active | medium | Web | 100.0 |
| BL-24072 | 防止数据导入导出重复提交 | 数据导入导出 | Medium | Active | medium | Web | 100.0 |
| BL-24350 | 验证贝位号非整数时系统返回正确的错误信息 | 岸桥贝位查询接口 | Low | Active | low | Web | 100.0 |
| BL-24188 | 未登录用户尝试访问页面被拒绝 | 岸桥终端监控 | Medium | Active | medium | Web | 100.0 |
| BL-24221 | 防止修改船舶重复提交 | 修改船舶 | Medium | Active | medium | Web | 100.0 |

## Case Details (Full Fields)

| Test Case ID | Title | Scenario | Pre Condition | Test Script | Expected Result | Platform | Updated By | Updated At |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BL-24172 | 操作员查看指定岸桥的实时作业视图 | 终端显示 - 正常 | 已登录操作员账号；系统已配置船舶贝位结构；N4系统连接正常；已分配QC编号{{qc_id}} | 1. 登录后访问QC终端页面{{qc_terminal_url}}；2. 系统自动根据QC编号{{qc_id}}查询N4系统作业队列；3. 查看贝位视图表格 | 1. QC终端页面成功加载；2. 系统返回该岸桥的作业数据；3. 正确显示贝位矩阵、集装箱位置和剩余数量 | Web | tony.z.ye | 2026-08-19T09:10:25Z |
| BL-25503 | qcvmt login | qcvnt login | login qcvmt | open https://qcvmt.getsvc.com/<br />login with user name: admin. password: 123456, qc id QC86 | can be open<br />login success | Web | tony.z.ye | 2026-08-19T06:54:34.491Z |
| BL-24178 | 正确显示加油区域高亮标识 | 终端显示 - 正常 | 已登录操作员账号；系统已配置船舶加油区域；当前QC编号{{qc_id}}对应的船舶启用了加油功能 | 1. 访问QC终端页面{{qc_terminal_url}}；2. 查看页面顶部加油状态指示器；3. 查看贝位矩阵中加油区域的单元格 | 1. 页面成功加载；2. 顶部显示"加油状态: 启用"及红色指示灯；3. 加油区域单元格以红色边框高亮显示 | Web | tony.z.ye | 2026-08-13T01:22:42Z |
| BL-24072 | 防止数据导入导出重复提交 | 重复提交 - 异常 | 已登录管理员账号；已进入操作页面 | 填写完整表单 快速连续点击提交按钮{{3}}次 | 表单内容已填写完整 系统仅保存一条记录，防止重复创建 | Web | tony.z.ye | 2026-08-13T01:19:42Z |
| BL-24350 | 验证贝位号非整数时系统返回正确的错误信息 | 贝位号非整数异常处理 | 操作员已登录；N4作业队列中含有非整数贝位号 | 发起贝位查询 GET /user/BusiQuery?qcNum={{qcNum}} 系统处理贝位号时检测到非整数格式 验证返回的错误响应 | 请求正确发送 系统检测到贝位号非整数，抛出GeneralException 返回错误XML，包含'error_bay_number_integer'提示信息 | Web | tony.z.ye | 2026-08-13T01:19:36Z |
| BL-24188 | 未登录用户尝试访问页面被拒绝 | 权限控制 - 异常 | 用户未登录；直接访问页面URL | 1. 直接访问URL {{qc_terminal_url}}；2. 观察页面响应 | 1. 直接访问目标URL；2. 系统重定向至登录页面，不允许访问 | Web | tony.z.ye | 2026-08-13T01:19:30Z |
| BL-24221 | 防止修改船舶重复提交 | 重复提交 - 异常 | 已登录管理员账号；已进入操作页面 | 填写完整表单 快速连续点击提交按钮{{3}}次 | 表单内容已填写完整 系统仅保存一条记录，防止重复创建 | Web | tony.z.ye | 2026-08-13T01:19:24Z |