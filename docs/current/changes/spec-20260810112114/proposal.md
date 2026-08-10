# 变更提案

> **生成日期**：2026-08-10  
> **变更标识**：spec-20260810112114  
> **关联分析**：[analysis.md](../../docs/current/analysis.md)

---

## 1. 背景与问题

QCVMT（码头岸桥集装箱作业管理系统）当前基于 Spring MVC 3.0.1 + JSP + jQuery 1.11.1 构建，Java 7，部署为 WAR 包。系统存在以下核心问题：

1. **前后端强耦合**（[P1]）：Bay Plan HTML 表格由后端 `CellDaoImpl.buildBay()` 生成，前端通过 `innerHTML` 注入，无法独立部署
2. **数据交换格式脆弱**（[P2]）：`Busihandler.returnResponse()` 返回自定义 XML（非标准 XML、非 JSON），前端使用字符串截取解析，维护困难
3. **Session 认证阻碍分离**（[P6]）：`SecurityInterceptor` + HTTP Session 存储用户状态，无法支持前后端分离部署
4. **安全风险**（[P8]）：用户密码明文存储，无 CSRF 保护，硬编码管理员默认密码
5. **IE 兼容代码负担**（[P4]）：`expression()`, `bgiframe`, `window.event` 等 IE5/6 兼容代码已无业务价值
6. **无工程化支撑**（[P5][P9][P10]）：无前端构建工具、无 TypeScript 类型安全、无自动化测试，回归风险极高

后端已完成 Spring Boot 3 + REST API 改造设计（参见 S00600 执行计划），前端需同步完成从 JSP 到 React SPA 的改造，实现完整的前后端分离架构。

---

## 2. 变更目标

| 目标编号 | 目标描述 | 对应问题 |
|---------|---------|---------|
| G1 | 建立 React 18 + Vite 5 + TypeScript 5 前端项目，可独立构建部署 | P4, P5, P9 |
| G2 | 前端通过 REST JSON API 与后端交互，废弃自定义 XML 数据格式 | P1, P2 |
| G3 | 认证体系迁移至 Keycloak OIDC，前端使用 `keycloak-js` | P6, P8 |
| G4 | 21 个 JSP 页面全部重写为 React 组件，保留业务功能一致性 | P1, P3, P7 |
| G5 | 核心业务逻辑（自适应轮询、Bay Plan 渲染、时间同步）在前端重构 | P1 |
| G6 | 支持 3 种语言（EN / 繁体中文 / 简体中文）| i18n 迁移 |
| G7 | 消除所有 IE 兼容代码和 JSP 模板 | P4 |
| G8 | 前端独立 Docker 化部署，Nginx 反向代理 | P5 |

---

## 3. 变更范围

### 3.1 范围内（In Scope）

| 类别 | 具体内容 |
|------|---------|
| **新项目搭建** | `qcvmt-frontend/` React 18 + Vite 5 + TypeScript 5 项目 |
| **API 层** | 9 个 API 模块（Axios + 拦截器 + Token 注入）+ TypeScript 类型定义 |
| **认证** | Keycloak OIDC 集成（`keycloak-js`）、`AuthGuard` 路由守卫、Zustand auth store |
| **路由** | React Router 6 + 路由懒加载（`React.lazy`） |
| **状态管理** | Zustand stores（auth, terminal, app） |
| **核心页面** | `TerminalPage`（Bay Plan 实时显示）+ `BayPlanGrid` + `BayCell` + `SignalIndicator` |
| **核心 Hooks** | `usePolling`（自适应轮询）、`useServerClock`（服务器时间同步）、`usePermission`（权限判断） |
| **管理页面** | 用户管理、船舶管理、颜色设置、加油管理、贝位颜色、Bay 尺寸、导入导出（共 15 个页面组件） |
| **共享组件** | `AdminLayout`, `TerminalLayout`, `AppHeader`, `ConfirmDialog`, `SearchBar` |
| **i18n** | `react-i18next`，`messages_*.properties` → `en.json` / `zh-TW.json` / `zh-CN.json` |
| **表单** | React Hook Form + Zod schema 验证 |
| **样式** | Ant Design 5 主题 + CSS Modules（`bay-plan.module.css`） |
| **部署** | Docker 多阶段构建 + Nginx 配置 |
| **测试** | Vitest + React Testing Library（hooks 和核心组件） |
| **旧代码清理** | 从后端项目移除 `src/main/webapp/`、`web.xml`、`springMVC-servlet.xml` |

### 3.2 非目标（Out of Scope）

| 类别 | 排除原因 |
|------|---------|
| 后端 REST API 实现 | 已在 S00600 后端执行计划中独立覆盖 |
| 重新设计业务逻辑 | Bay Plan 渲染规则、轮询策略保持不变，仅迁移实现方式 |
| 移动端适配 | 系统仅在码头工控屏/PC 使用，无需响应式设计 |
| SSR / SSG | 纯 SPA 满足需求，无 SEO 要求 |
| 微前端 | 项目规模不需要，单 SPA 即可 |
| WebSocket / SSE 实时推送 | 保留现有轮询模式，后续迭代可评估 |
| Keycloak 服务器部署与配置 | 由运维/基础设施团队独立负责 |
| N4 系统集成改造 | 保持现有 Oracle 只读直连方式 |
| 数据库 Schema 迁移 | 后端执行计划覆盖 |

---

## 4. 交付结果

| 阶段 | 交付物 | 验收标准 |
|------|-------|---------|
| Phase 1 — 基础骨架 | `qcvmt-frontend/` 项目、Vite 配置、ESLint/Prettier、依赖安装 | `npm run dev` 启动成功，`npm run build` 构建成功 |
| Phase 2 — API 层 | `src/api/`（9 个模块）、`src/types/`（5 个类型文件）、`src/lib/axios.ts` | 单元测试通过，API 调用可正确发送请求 |
| Phase 3 — 认证/路由/i18n | Keycloak 集成、路由器、i18n 迁移、布局组件、`LoginPage` | Keycloak 登录 → Token → 路由跳转 → 布局渲染链路通过 |
| Phase 4 — 核心业务 | `TerminalPage`、`BayPlanGrid`、`usePolling`、`useServerClock`、`DashboardPage` | Bay Plan 正确渲染，轮询正常，信号指示正确 |
| Phase 5 — 管理页面 | 用户管理、船舶管理、颜色设置等全部 CRUD 页面 | 所有管理后台增删改查正常，表单验证正确 |
| Phase 6 — 旧代码清理 | 后端 `webapp/` 目录移除 | 功能对比测试：旧系统 vs 新系统全部通过 |
| Phase 7 — 部署 | `Dockerfile`、`nginx.conf`、CI/CD 配置 | Docker 镜像构建成功，Nginx 代理正确 |

---

## 5. 验收标准

### 5.1 功能验收

| 编号 | 验收项 | 验证方式 |
|------|-------|---------|
| AC1 | 21 个旧 JSP 页面在新系统中有对应功能 | 功能对比测试清单 |
| AC2 | 23 个 REST API 端点已对接并正常工作 | API 集成测试 |
| AC3 | Keycloak OIDC 登录/登出/Token 刷新正常 | 端到端登录流程验证 |
| AC4 | Bay Plan 渲染与旧系统视觉效果一致 | 截图对比 + 边界用例验证 |
| AC5 | 自适应轮询 3 种模式全部工作（15s → 20s → 25s → 30s） | 单元测试 + 网络模拟 |
| AC6 | 3 种语言切换正常（EN / 繁体中文 / 简体中文） | 手动验证 |
| AC7 | 管理后台所有 CRUD 操作正常 | 功能测试 |
| AC8 | 导入/导出功能正常 | 端到端测试 |
| AC9 | 权限控制（admin / user / 受限账户）正确 | 角色矩阵验证 |

### 5.2 技术验收

| 编号 | 验收项 | 验证方式 |
|------|-------|---------|
| TC1 | TypeScript 无 `any` 类型（除第三方库） | `tsc --noEmit` 检查 |
| TC2 | 单元测试覆盖 hooks 和核心组件 | `vitest run --coverage` |
| TC3 | 首次加载 FCP < 2s | Lighthouse 测量 |
| TC4 | Bay Plan 渲染 < 200ms | 性能测试 |
| TC5 | Bundle 大小 < 300KB gzip | `npm run build` 输出检查 |
| TC6 | `npm run build` 无错误无警告 | CI 检查 |
| TC7 | Docker 镜像构建成功 | `docker build` 验证 |
| TC8 | 旧 `webapp/` 目录已清理 | 目录检查 |

---

## 6. 假设与依赖

### 6.1 假设

| 编号 | 假设内容 |
|------|---------|
| A1 | 后端 Spring Boot 3 REST API 已按 S00600 执行计划完成或同步开发 |
| A2 | Keycloak 服务器已部署并配置好 `qcvmt` realm、`qcvmt-frontend` client、角色 |
| A3 | N4 集成方式保持不变（Oracle 只读直连），由后端负责 |
| A4 | 工控屏分辨率固定，Bay Plan 保持固定尺寸 |
| A5 | 3 种语言的翻译内容从 `messages_*.properties` 直接迁移，无需新增翻译 |

### 6.2 外部依赖

| 依赖 | 提供方 | 阻塞阶段 |
|------|-------|---------|
| 后端 REST API 就绪 | 后端团队 | Phase 2 起 |
| Keycloak realm/client 配置 | 运维/基础设施 | Phase 3 起 |
| MySQL 数据库 Schema | 后端团队 | Phase 2 起 |
| Docker Registry 访问权限 | 运维 | Phase 7 |
| N4 测试环境 | N4 团队 | Phase 4 起（联调） |

---

## 7. 时间规划（7 个阶段）

```
Phase 1  ██████░░░░░░░░░░░░░░░░  基础骨架（低）
Phase 2  ████████████░░░░░░░░░░  API 层（低）
Phase 3  ██████████████████░░░░  认证/路由/i18n（中）
Phase 4  ██████████████████████  核心业务（高）
Phase 5  ██████████████████████  管理页面（低）
Phase 6  ██████████████████░░░░  旧代码清理（中）
Phase 7  ████████████░░░░░░░░░░  部署配置（低）
```

| 阶段 | 前置依赖 | 风险等级 |
|------|---------|---------|
| Phase 1 | 无 | 低 |
| Phase 2 | Phase 1 | 低（需后端 API 已就绪） |
| Phase 3 | Phase 1, 2 | 中（Keycloak 配置需与后端一致） |
| Phase 4 | Phase 1-3 | **高**（核心业务页面，Bay Plan 渲染逻辑复杂） |
| Phase 5 | Phase 1-4 | 低（CRUD 页面模式统一） |
| Phase 6 | Phase 1-5 全部完成 | 中（需确保无遗漏功能） |
| Phase 7 | Phase 1-6 | 低 |
