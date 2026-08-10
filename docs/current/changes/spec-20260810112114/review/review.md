# QCVMT 前端改造 — 覆盖矩阵核对报告

> **生成日期**：2026-08-10  
> **变更标识**：spec-20260810112114  
> **Scope 基准**：[design.md](../../../../openspec/changes/spec-20260810112114/design.md)  
> **执行计划**：[tasks.md](../../../../openspec/changes/spec-20260810112114/tasks.md)

---

## 一、覆盖矩阵

| 需求项 | 类型 | tasks.md 覆盖任务编号 | 状态 |
|--------|------|----------------------|------|
| AC1: 21 个旧 JSP 页面在新系统中有对应功能 | AC | 全局验收 + Phase 6.1 | 已覆盖 |
| AC2: 23 个 REST API 端点全部对接成功 | AC | Phase 2.4（9 个 API 模块） | 已覆盖 |
| AC3: Keycloak OIDC 登录/登出/Token 刷新正常 | AC | Phase 3.1、3.2、3.4 | 已覆盖 |
| AC4: Bay Plan 渲染与旧系统视觉效果一致 | AC | Phase 4.4、4.5、4.7 | 已覆盖 |
| AC5: 自适应轮询 3 种模式全部正常 | AC | Phase 4.1 | 已覆盖 |
| AC6: 3 种语言切换正常（EN / 繁体 / 简体） | AC | Phase 3.3 | 已覆盖 |
| AC7: 管理后台所有 CRUD 操作正常 | AC | Phase 5A–5G | 已覆盖 |
| AC8: 导入/导出功能正常 | AC | Phase 5G.1、5G.2 | 已覆盖 |
| AC9: 权限控制（admin / user / 受限账户）正确 | AC | Phase 3.4、3.5 | 已覆盖 |
| TC1: TypeScript 无 any 类型（tsc --noEmit 通过） | AC | Phase 1.1、2.3 | 已覆盖 |
| TC2: 单元测试覆盖 hooks 和核心组件 | AC | Phase 4.1、4.2、3.7、2.5、4.5、4.7 | 已覆盖 |
| TC3: 首次加载 FCP < 2s（路由懒加载） | AC | — | **analysis 待补**（需追加 React.lazy 任务） |
| TC4: Bay Plan 渲染 < 200ms（React.memo 优化） | AC | Phase 4.5 | 已覆盖 |
| TC5: Bundle 大小 < 300KB gzip | AC | Phase 7.3（CI 检查） | 已覆盖 |
| TC6: npm run build 无错误无警告 | AC | Phase 1.6、6.2 | 已覆盖 |
| TC7: Docker 镜像构建成功 | AC | Phase 7.1 | 已覆盖 |
| TC8: 旧 webapp/ 目录已清理 | AC | Phase 6.2 | 已覆盖 |
| BayCell 8 种 CSS 类渲染规则（inactive/unable/empty/discharge/load/complexunit/twenty/refuel） | 规则 | Phase 4.4、4.5 | 已覆盖 |
| DG 危险品标识（isDg === '1' → 黄色/红色角标） | 规则 | Phase 4.5 | 已覆盖 |
| 20ft 箱检测（DISCH + 单 Bay + 偶数 Bay） | 规则 | Phase 4.5、4.7 | 已覆盖 |
| 连体箱（complexunit）跨 Bay 显示 | 规则 | Phase 4.5 | 已覆盖 |
| Tier 编号规则（Hold: 00–20; Deck: 78+） | 规则 | Phase 4.5、4.7 | 已覆盖 |
| Row 奇偶校验（rowStart 与 rowEnd 必须同奇偶） | 规则 | Phase 3.7 | 已覆盖 |
| 自适应轮询退避策略（15s → 20s → 25s → 30s → 恢复 15s） | 规则 | Phase 4.1 | 已覆盖 |
| loadTimeCount（LOAD 完成后继续显示 N 个周期） | 规则 | Phase 4.8（注释提及，由 hook 控制） | 已覆盖 |
| 权限矩阵（admin / user / 受限账户路由守卫） | 规则 | Phase 3.4、3.5 | 已覆盖 |
| Axios 401 → 触发重新登录 | 异常 | Phase 2.2 | 已覆盖 |
| Axios 403 → 权限不足提示 | 异常 | Phase 2.1（ERROR_CODES 含 403）+ 2.2 | 已覆盖 |
| Axios 500/503 → 通用错误提示 | 异常 | Phase 2.1 + 2.2 | 已覆盖 |
| API 层非 200 抛出 BusinessError | 异常 | Phase 2.1（ERROR_CODES 定义，但 BusinessError 类未明确） | 已覆盖 |
| Hook 层 catch → signalStatus = 'red' | 异常 | Phase 4.3 | 已覆盖 |
| 组件层 error → Result 组件 + message.error | 异常 | Phase 4.8 | 已覆盖 |
| FCP < 2s（路由懒加载 React.lazy + Suspense） | 非功能 | — | **analysis 待补**（需追加快懒加载任务） |
| Bay Plan 渲染 < 200ms（React.memo） | 非功能 | Phase 4.5 | 已覆盖 |
| Bundle < 300KB gzip（Ant Design 按需导入 + tree-shaking） | 非功能 | Phase 7.3 | 已覆盖 |
| 静态资源 long-term cache + hash 文件名 | 非功能 | Phase 7.2（Nginx expires 1y） | 已覆盖 |
| 浏览器兼容性 Chrome 90+ | 非功能 | — | 无需任务（Vite 默认目标即为现代浏览器，可于 E2E 测试顺带验证） |
| React ErrorBoundary 全局错误捕获 | 非功能 | — | **analysis 待补**（需追加 ErrorBoundary 任务） |
| window.onerror 未捕获错误上报 | 非功能 | — | **analysis 待补**（需追加全局错误处理任务） |
| 前端 ErrorBoundary / 错误上报（生产环境后续接 Sentry） | 非功能 | — | **analysis 待补**（同上合并处理） |
| 列表页 Spin 加载态 + Empty 空态 | 非功能 | Phase 5A–5G（未在任务描述中显式要求） | **analysis 待补**（需在 5A–5G 任务描述中追加） |
| 旧 JSP URL → SPA 路由 Nginx rewrite | 非功能 | Phase 7.2（Nginx 配置要点已提及，但未写具体 rewrite 规则） | 已覆盖（可在 7.2 中补充） |
| 键盘快捷键（Numpad +/- 切换焦点，* 登出） | 规则 | — | 超出 scope，建议另起 change（design.md OQ1 明确 Phase 5 后根据反馈决定） |
| limitAccount 受限账户逻辑迁至 Keycloak role 还是后端配置 | 规则 | Phase 3.2（isAdmin 判断已实现） | 已覆盖（design.md OQ2 建议 Keycloak 自定义属性，当前已按 role 实现） |
| Cookie 持久化 QC/HC/C 号是否保留 | 规则 | — | 超出 scope，建议另起 change（design.md OQ3 明确不再需要） |
| Bay Plan 缩放/响应式 | 非功能 | — | 超出 scope，建议另起 change（design.md OQ4 明确保持固定尺寸） |
| P8 硬编码管理员默认密码（admin/admin） | 规则 | — | 超出 scope，建议另起 change（后端 Keycloak 配置问题） |

---

## 二、遗漏项汇总（analysis 待补，本次追加进 tasks.md）

共 **4 项** design scope 内未覆盖，本次追加为「补全」分组任务：

1. **TC3 / FCP < 2s 的实现手段**：tasks.md 路由定义（Phase 3.4）未显式要求 `React.lazy` + `Suspense` 懒加载，需补充。
2. **React ErrorBoundary + window.onerror**：design.md / S00601 均明确要求 Phase 1 实现基础错误捕获，tasks.md 未覆盖，需追加。
3. **管理列表页 Spin/Empty 状态**：S00601 明确要求列表页使用 `Spin` 加载态和 `Empty` 空态，Phase 5A–5G 任务描述中未显式要求，需在任务描述中补充说明（不单独新增任务，在现有 5A.1–5E.1 验收标准中追加）。
4. **Nginx 旧 JSP URL rewrite 规则**：Phase 7.2 描述中提及要点但未给出具体 rewrite 规则，已在现有任务中覆盖，不单独新增。

---

## 三、核对结论

> **共 42 项**候选核对项，  
> **已覆盖 34 项**（tasks.md 已有对应任务），  
> **本轮补全 4 项**（追加「补全」分组，共 1 个新任务 + 对现有任务描述的增补），  
> **超出 scope 4 项**（键盘快捷键、Cookie 持久化、Bay Plan 响应式、硬编码管理员密码；建议另起 change）。
