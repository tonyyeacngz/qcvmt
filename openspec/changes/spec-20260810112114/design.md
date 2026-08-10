# 技术设计文档

> **生成日期**：2026-08-10  
> **变更标识**：spec-20260810112114  
> **关联分析**：[analysis.md](../../docs/current/analysis.md) | [proposal.md](proposal.md)

---

## 1. 总体方案

### 1.1 架构概览

QCVMT 前端从 JSP 服务端渲染迁移至 **React 18 SPA + REST JSON API** 前后端分离架构。

```
┌──────────────┐     ┌──────────────┐     ┌──────────────────┐
│   浏览器      │     │  Nginx 反代   │     │   Keycloak       │
│  React SPA   │────▶│  静态资源     │     │   OIDC Provider  │
│  keycloak-js │     │  /api/* 代理  │◀────│                  │
└──────────────┘     └──────┬───────┘     └──────────────────┘
                           │ /api/*
                           ▼
                    ┌──────────────────┐
                    │  QCVMT API       │
                    │  Spring Boot 3   │
                    │  JWT 验证        │
                    └──────┬───────────┘
                           │
                    ┌──────┴───────────┐
                    │                  │
               ┌────▼────┐      ┌─────▼─────┐
               │ MySQL   │      │ N4 Oracle │
               │ (本地)   │      │ (只读)     │
               └─────────┘      └───────────┘
```

### 1.2 关键决策

| 决策点 | 选型 | 理由 |
|--------|------|------|
| UI 框架 | React 18 | 生态成熟，Hooks 适合状态管理 |
| 构建工具 | Vite 5 | 快速 HMR，原生 ESM |
| 状态管理 | Zustand | 轻量、无 boilerplate、TypeScript 友好 |
| UI 组件库 | Ant Design 5 | 表格/表单/分页成熟，企业级管理后台首选 |
| HTTP 客户端 | Axios | 拦截器、Token 注入、错误处理 |
| 认证 | keycloak-js | Keycloak 官方 JS 适配器 |
| 表单 | React Hook Form + Zod | 高性能 + 类型安全 schema 验证 |
| 路由 | React Router 6 | 嵌套路由、loader 支持 |
| i18n | react-i18next | React 生态最成熟 |
| 日期 | dayjs | 轻量，替代旧 `Date.prototype.format` |
| 测试 | Vitest + React Testing Library | 与 Vite 生态一致 |

### 1.3 前后端职责划分

| 职责 | 前端 (React SPA) | 后端 (Spring Boot 3) |
|------|-----------------|-------------------|
| 页面渲染 | 完全负责 | 不负责 |
| 路由管理 | React Router | 不负责 |
| 表单验证 | 前端校验 + 后端校验 | 最终校验 |
| 认证 | keycloak-js 获取 Token | JWT 验证 |
| 授权 | 路由守卫 + 按钮级控制 | `@PreAuthorize` |
| Bay Plan 渲染 | 基于 JSON 数据渲染 | 只返回结构化数据 |
| 轮询控制 | 前端控制间隔和策略 | 不负责 |
| 业务规则校验 | 不负责 | 唯一权威 |
| 数据库操作 | 不负责 | 完全负责 |
| N4 查询 | 不负责 | 完全负责 |
| i18n | 前端 i18n | 后端错误消息 i18n |

---

## 2. 组件架构与数据流

### 2.1 项目目录结构

```
qcvmt-frontend/
├── index.html
├── vite.config.ts
├── tsconfig.json
├── package.json
├── .env                          # 默认环境变量
├── .env.development              # 开发环境
├── .env.production               # 生产环境
├── Dockerfile
├── nginx.conf
├── public/
│   ├── favicon.ico
│   └── silent-check-sso.html     # Keycloak 静默 SSO 检查
└── src/
    ├── main.tsx                  # 入口：初始化 Keycloak、i18n、渲染 App
    ├── App.tsx                   # 根组件：路由 + 布局
    ├── vite-env.d.ts
    ├── assets/images/
    │   ├── green.gif             # 保留自旧项目
    │   └── red.gif               # 保留自旧项目
    ├── lib/
    │   ├── keycloak.ts           # Keycloak 实例创建与初始化
    │   ├── axios.ts              # Axios 实例 + 拦截器
    │   └── i18n.ts               # i18next 配置
    ├── router/
    │   └── index.tsx             # 路由定义 + AuthGuard
    ├── stores/
    │   ├── auth.ts               # 用户认证状态、Token、角色
    │   ├── terminal.ts           # Bay Plan 实时数据状态
    │   └── app.ts                # 全局 UI 状态（语言、侧边栏）
    ├── api/
    │   ├── types.ts              # ApiResponse, PageResponse, PageParams
    │   ├── terminal.ts           # /api/terminal
    │   ├── user.ts               # /api/users
    │   ├── vessel.ts             # /api/vessels
    │   ├── colorSet.ts           # /api/color-sets
    │   ├── vesselColor.ts        # /api/vessel-colors
    │   ├── vesselRefuel.ts       # /api/vessel-refuels
    │   ├── bayConfig.ts          # /api/bay-config
    │   ├── operationLog.ts       # /api/operation-logs
    │   └── importExport.ts       # /api/import, /api/export
    ├── hooks/
    │   ├── usePolling.ts         # 自适应轮询
    │   ├── useServerClock.ts     # 服务器时间同步
    │   └── usePermission.ts      # 权限判断
    ├── pages/
    │   ├── login/LoginPage.tsx
    │   ├── terminal/TerminalPage.tsx
    │   ├── admin/
    │   │   ├── DashboardPage.tsx
    │   │   ├── UserList.tsx
    │   │   ├── UserForm.tsx
    │   │   ├── UserLogs.tsx
    │   │   ├── VesselList.tsx
    │   │   ├── VesselForm.tsx
    │   │   ├── ColorSetList.tsx
    │   │   ├── ColorSetForm.tsx
    │   │   ├── VesselColorList.tsx
    │   │   ├── VesselColorForm.tsx
    │   │   ├── VesselRefuelList.tsx
    │   │   ├── VesselRefuelForm.tsx
    │   │   ├── BaySizeForm.tsx
    │   │   ├── ImportPage.tsx
    │   │   └── ExportPage.tsx
    ├── components/
    │   ├── layout/
    │   │   ├── AppHeader.tsx
    │   │   ├── AdminLayout.tsx
    │   │   └── TerminalLayout.tsx
    │   ├── bay/
    │   │   ├── BayPlanGrid.tsx
    │   │   ├── BayCell.tsx
    │   │   └── SignalIndicator.tsx
    │   └── common/
    │       ├── ConfirmDialog.tsx
    │       ├── SearchBar.tsx
    │       └── AuthGuard.tsx
    ├── types/
    │   ├── user.ts
    │   ├── vessel.ts
    │   ├── colorSet.ts
    │   ├── terminal.ts
    │   └── bayConfig.ts
    ├── locales/
    │   ├── en.json
    │   ├── zh-TW.json
    │   └── zh-CN.json
    ├── utils/
    │   ├── validators.ts         # Zod schemas
    │   └── format.ts
    └── styles/
        ├── theme.ts              # Ant Design 主题 token
        ├── bay-plan.module.css
        └── global.css
```

### 2.2 QC 终端页数据流（核心）

```
TerminalPage 挂载
    │
    ▼
usePolling(qcNum) ─── 初始化 ──→ thisInterval = 15000ms
    │
    ▼ (每 thisInterval 毫秒)
terminal store.fetchTerminalData(qcNum)
    │
    ▼
terminalApi.query(qcNum)
    │
    ▼ (HTTP)
GET /api/terminal/query?qcNum=xxx
    │
    ▼ (JSON 响应)
ApiResponse<TerminalView>
    │
    ├──→ state.vessels
    ├──→ state.workQueue
    ├──→ state.colorSets
    ├──→ state.robContainers
    └──→ state.signalStatus = 'green'
    │
    ▼ (React re-render)
BayPlanGrid (接收 props)
    │
    ▼ (遍历 SequenceVO[])
BayCell (React.memo —— 跳过未变化单元格)
    │
    ▼
根据 type + colorMap 决定 CSS 类和背景色
    │
useServerClock ──→ 每秒更新 current_date / current_time
SignalIndicator ──→ green.gif / red.gif
```

### 2.3 管理后台数据流

```
Page 组件 (useEffect / 事件触发)
    │
    ▼
api/*.ts (HTTP 请求)
    │
    ▼
Axios 实例 (注入 Bearer Token)
    │
    ▼ (JSON 响应)
ApiResponse<T> / PageResponse<T>
    │
    ├── 成功 → antd message 提示 + 更新 Table/Form
    └── 失败 → antd message.error 提示
```

### 2.4 认证流程

```
用户访问应用
    │
    ▼
keycloak.init({ onLoad: 'check-sso' })
    │
    ├── 未登录 → 重定向到 Keycloak 登录页
    │                │
    │                ▼ (登录成功)
    │           返回 Access Token + Refresh Token
    │
    └── 已登录 (SSO) → 静默返回 Token
    │
    ▼
存储到 auth store (Zustand)
    │
    ▼
GET /api/users/me (Bearer Token) → 获取 User 信息 → 存入 auth store
    │
    ▼
AuthGuard 放行 → 渲染对应页面
    │
    ▼ (Token 即将过期)
keycloak.updateToken(30) → 刷新 Access Token
```

---

## 3. 数据模型

### 3.1 核心类型定义

#### `src/types/terminal.ts`

```typescript
export interface TerminalView {
  vessels: Vessel[]
  workQueue: WorkQueueResult
  colorSets: ColSet[]
  robContainers: RobContainer[]
}

export interface WorkQueueResult {
  qorder: string
  vesselId: string
  minBay: string
  maxBay: string
  deckHold: string            // "A" (Deck) | "B" (Hold)
  qType: string               // "LOAD" | "DISCH"
  remainContainers: number
  sequences: SequenceVO[]
}

export interface SequenceVO {
  currentPosSlot: string
  plannedPosSlot: string
  qtype: string               // "LOAD" | "DISCH"
  qdeck: string
  qrow: string
  status: string
  bay: string
  isOog: string               // "0" | "1"
  isPowered: string           // "0" | "1"
  isTank: string              // "0" | "1"
  isDg: string                // "0" | "1"
  isQuad: boolean
  isTandem: boolean
  isTwin: boolean
  isSingle: boolean
  complexunit: string         // "" | "0" | "1"
  twentyInd: string           // null | "Y"
}

export interface ColSet {
  colsetid: number
  color: string               // 十六进制颜色值
  boxcase: string             // 箱型标识
}

export interface RobContainer {
  slot: string
  bay: string
  type: string
}
```

#### `src/types/user.ts`

```typescript
export interface User {
  id: number
  keycloakId: string
  qcid: string
  username: string
  role: 'ADMIN' | 'USER'
  parent: string
  createtime: string          // ISO 格式
}
```

#### `src/types/vessel.ts`

```typescript
export interface Vessel {
  id: number
  vesselid: string
  deck_hold: 'A' | 'B'
  bay: string
  rowStart: string
  rowEnd: string
  tierStart: string
  tierEnd: string
}
```

#### `src/api/types.ts`

```typescript
export interface ApiResponse<T> {
  code: number
  message: string
  data: T
  timestamp: number
}

export interface PageResponse<T> {
  content: T[]
  totalElements: number
  totalPages: number
  number: number              // 当前页码（0-based）
  size: number
}

export interface PageParams {
  page?: number
  size?: number
  keyword?: string
}
```

### 3.2 Zod Schema 验证（迁移自 JSP 验证逻辑）

```typescript
// src/utils/validators.ts
import { z } from 'zod'

export const vesselColorSchema = z.object({
  vesselid: z.string().min(1, 'Vessel Visit Id 不能为空').max(30),
  deck_hold: z.enum(['A', 'B']),
  bay: z.string().min(1).max(10).regex(/^\d+$/, 'Bay 应为数字'),
  rowStart: z.string().min(1).max(2).regex(/^\d+$/),
  rowEnd: z.string().min(1).max(3).regex(/^\d+$/),
  tierStart: z.string().max(2).regex(/^\d*$/).optional(),
  tierEnd: z.string().max(3).regex(/^\d*$/).optional(),
}).refine(
  (data) => Number(data.rowStart) <= Number(data.rowEnd),
  { message: '起始 Row 不能大于结束 Row' }
).refine(
  (data) => Number(data.rowStart) % 2 === Number(data.rowEnd) % 2,
  { message: '起始 Row 和结束 Row 应同为奇数或同为偶数' }
)
```

---

## 4. 接口与配置变化

### 4.1 Axios 实例与拦截器

```typescript
// src/lib/axios.ts
import axios from 'axios'
import keycloak from './keycloak'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 3000,
  headers: { 'Content-Type': 'application/json' }
})

apiClient.interceptors.request.use((config) => {
  const token = keycloak.token
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

apiClient.interceptors.response.use(
  (response) => response.data,
  async (error) => {
    if (error.response?.status === 401) {
      await keycloak.login()
    }
    return Promise.reject(error)
  }
)

export default apiClient
```

### 4.2 API 端点映射（完整）

| 旧 URL | 新 REST API | 方法 | 数据格式 | 前端 API 模块 |
|--------|------------|------|---------|-------------|
| `BusiQuery.html?qcNum=xxx` | `GET /api/terminal/query?qcNum=xxx` | GET | JSON | `terminalApi.query()` |
| `all.html` | `GET /api/users?page=0&size=10` | GET | JSON | `userApi.list()` |
| `save.html` (POST) | `POST /api/users` | POST | JSON | `userApi.create()` |
| `update.html` (POST) | `PUT /api/users/{id}` | PUT | JSON | `userApi.update()` |
| `del.html?id=x` | `DELETE /api/users/{id}` | DELETE | JSON | `userApi.delete()` |
| `log.html?id=x` | `GET /api/users/{id}/logs` | GET | JSON | `userApi.logs()` |
| `allVessel.html` | `GET /api/vessels` | GET | JSON | `vesselApi.list()` |
| `saveVessel.html` | `POST /api/vessels` | POST | JSON | `vesselApi.create()` |
| `updateVessel.html` | `PUT /api/vessels/{id}` | PUT | JSON | `vesselApi.update()` |
| `delVessel.html?id=x` | `DELETE /api/vessels/{id}` | DELETE | JSON | `vesselApi.delete()` |
| `searchVessel.html?key=x` | `GET /api/vessels?keyword=x` | GET | JSON | `vesselApi.list({ keyword })` |
| `allColSet.html` | `GET /api/color-sets` | GET | JSON | `colorSetApi.list()` |
| `saveColSet.html` | `POST /api/color-sets` | POST | JSON | `colorSetApi.create()` |
| `updateColSet.html` | `PUT /api/color-sets/{id}` | PUT | JSON | `colorSetApi.update()` |
| `allVesselCol.html` | `GET /api/vessel-colors` | GET | JSON | `vesselColorApi.list()` |
| `saveVesselCol.html` | `POST /api/vessel-colors` | POST | JSON | `vesselColorApi.create()` |
| `delVesselCol.html?id=x` | `DELETE /api/vessel-colors/{id}` | DELETE | JSON | `vesselColorApi.delete()` |
| `allVesselRefuel.html` | `GET /api/vessel-refuels` | GET | JSON | `vesselRefuelApi.list()` |
| `updateVesselRefuelStatus.html` | `POST /api/vessel-refuels` | POST | JSON | `vesselRefuelApi.create()` |
| `delVesselRefuel.html?id=x` | `DELETE /api/vessel-refuels/{id}` | DELETE | JSON | `vesselRefuelApi.delete()` |
| `setbay.html` | `GET /api/bay-config` | GET | JSON | `bayConfigApi.get()` |
| `updateBay.html` | `PUT /api/bay-config` | PUT | JSON | `bayConfigApi.update()` |
| `importVessel.html` | `POST /api/import/vessel` | POST | multipart | `importExportApi.importVessel()` |
| `exportLogs.html` | `GET /api/export/logs?from=x&to=y` | GET | file | `importExportApi.exportLogs()` |

### 4.3 环境变量配置

```bash
# .env.development
VITE_API_BASE_URL=http://localhost:8080
VITE_KEYCLOAK_URL=http://localhost:8180
VITE_KEYCLOAK_REALM=qcvmt
VITE_KEYCLOAK_CLIENT_ID=qcvmt-frontend

# .env.production
VITE_API_BASE_URL=/api
VITE_KEYCLOAK_URL=https://keycloak.example.com
VITE_KEYCLOAK_REALM=qcvmt
VITE_KEYCLOAK_CLIENT_ID=qcvmt-frontend
```

### 4.4 Keycloak 配置

```typescript
// src/lib/keycloak.ts
import Keycloak from 'keycloak-js'

const keycloak = new Keycloak({
  url: import.meta.env.VITE_KEYCLOAK_URL,
  realm: import.meta.env.VITE_KEYCLOAK_REALM,
  clientId: import.meta.env.VITE_KEYCLOAK_CLIENT_ID,
})

export async function initKeycloak(): Promise<boolean> {
  return keycloak.init({
    onLoad: 'check-sso',
    silentCheckSsoRedirectUri: `${window.location.origin}/silent-check-sso.html`,
    pkceMethod: 'S256',
    checkLoginIframe: true,
    checkLoginIframeInterval: 5,
  })
}

export default keycloak
```

---

## 5. 关键组件设计

### 5.1 BayCell（核心渲染组件）

| CSS 类 | 条件 | 样式 |
|--------|------|------|
| `.inactive` | 非活跃位置 | 背景色 = ColSet 中 `inactive` 颜色 |
| `.unable` | 禁用位置 | 背景色 = ColSet 中 `unable` 颜色 |
| `.empty` | 空位 | 背景色 = ColSet 中 `empty` 颜色 |
| `.discharge` | 卸箱 | 背景色 = ColSet 中 `discharge` 颜色 |
| `.load` | 装箱 | 背景色 = ColSet 中 `load` 颜色 |
| `.complexunit` | 连体箱 | 背景色 = ColSet 中 `complexunit` 颜色 |
| `.twenty` | 20ft 箱 | 红色文字 + inactive 背景 |
| `.refuel` | 加油区域 | 红色背景 + 红色文字 |
| `span.dgind` | 危险品标识 | 黄色背景 + 红色文字，绝对定位右上角 |

**优化策略**：`React.memo` 包裹，仅当 `SequenceVO` 属性变化时才重新渲染。

### 5.2 usePolling Hook（迁移自 vmt.js 自适应轮询）

| 状态变量 | 用途 | 初始值 |
|---------|------|--------|
| `refreshMode` | 轮询模式 (1/2/3) | 3 |
| `thisInterval` | 当前轮询间隔 (ms) | 15000 |
| `timeOutTimes` | 连续超时次数 | 0 |
| `lastTimeOut` | 上次是否超时 | false |
| `signalStatus` | 信号指示状态 | 'red' |

**自适应退避策略**：
- 成功 → `timeOutTimes = 0`，逐步恢复（30s → 25s → 20s → 15s）
- 超时 → `thisInterval` 递增（15s → 20s → 25s → 30s）
- 使用 `useRef` 管理定时器避免闭包问题

### 5.3 权限矩阵

| 路由 | qcvmt-admin | qcvmt-user |
|------|-------------|-----------|
| `/terminal` | 可访问 | 可访问 |
| `/admin` | 可访问 | 不可访问 |
| `/admin/users/**` | 可访问 | 不可访问 |
| `/admin/vessels/**` | 可访问 | 不可访问 |
| `/admin/color-sets/**` | 可访问 | 不可访问 |
| `/admin/vessel-refuels/**` | 可访问 | 可访问（受限账户） |
| `/admin/vessel-colors/**` | 可访问（受限账户） | 不可访问 |
| `/admin/bay-config` | 可访问 | 不可访问 |
| `/admin/import` | 可访问 | 不可访问 |
| `/admin/export` | 可访问 | 不可访问 |

---

## 6. 错误处理策略

### 6.1 分层错误处理

| 层级 | 处理方式 |
|------|---------|
| **Axios 拦截器** | 401 → 重新登录；403 → 权限不足提示；500 → 通用错误提示 |
| **API 层** | 解析 `ApiResponse.code`，非 200 抛出 `BusinessError` |
| **Hook 层** | catch 后设置 `signalStatus = 'red'` 或 `error` 状态 |
| **组件层** | `error` state → 显示 `Result` 组件；`message.error(msg)` 提示 |

### 6.2 错误码映射

```typescript
export const ERROR_MESSAGES: Record<number, string> = {
  400: '请求参数错误',
  401: '未登录或登录过期',
  403: '权限不足',
  404: '资源不存在',
  500: '服务器内部错误',
  503: 'N4 系统连接失败',
}
```

---

## 7. 兼容性与回滚

### 7.1 兼容性

| 维度 | 策略 |
|------|------|
| 浏览器 | 支持 Chrome 90+（工控屏通常为现代浏览器） |
| 旧 URL 兼容 | Nginx 配置 rewrite 规则，旧 JSP URL 重定向到 SPA 对应路由 |
| API 版本 | Phase 1 使用无版本前缀 `/api/*`，后续如需 v2 可加 `/api/v2/*` |

### 7.2 回滚策略

| 场景 | 回滚方式 |
|------|---------|
| 前端部署失败 | 回滚 Docker 镜像至上一版本 |
| API 对接异常 | Nginx 临时将特定路由指回旧 WAR |
| 功能缺失 | 保留旧系统并行运行，验证完全后下线 |

---

## 8. 测试策略

### 8.1 测试分层

| 层级 | 工具 | 覆盖目标 |
|------|------|---------|
| 单元测试 | Vitest | hooks（`usePolling`, `useServerClock`）、validators、api 模块 |
| 组件测试 | React Testing Library | `BayPlanGrid`、`BayCell`、表单组件 |
| E2E 测试 | Playwright（可选） | 登录流程、核心页面导航 |

### 8.2 关键测试场景

| 场景 | 测试内容 |
|------|---------|
| 自适应轮询 | 连续超时 → 间隔递增；成功 → 间隔恢复 |
| Bay Plan 渲染 | 给定 `SequenceVO[]` → 正确渲染 CSS 类（8 种类型全覆盖） |
| 表单验证 | `vesselColorSchema` 的奇偶校验、`tierStart`/`tierEnd` 联动 |
| Token 过期 | 401 响应 → 触发重新登录 |
| 权限控制 | 非 admin 用户 → 无法访问管理页面 |
| DG 标识 | `isDg === "1"` → 渲染黄色/红色标记 |
| 20ft 箱检测 | DISCH + 单 Bay + 偶数 Bay → 触发 `twentyInd` 逻辑 |

### 8.3 性能基准

| 指标 | 目标值 | 措施 |
|------|--------|------|
| 首次加载 (FCP) | < 2s | 路由懒加载 `React.lazy` + 代码分割 |
| Bay Plan 渲染 | < 200ms | `React.memo` 跳过未变化单元格 |
| 轮询开销 | 最小化 | 自适应间隔（迁移旧逻辑） |
| Bundle 大小 | < 300KB gzip | Ant Design 按需导入 + tree-shaking |

---

## 9. 部署配置

### 9.1 Docker 多阶段构建

```dockerfile
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

### 9.2 Nginx 配置要点

| 路径 | 处理方式 |
|------|---------|
| `/` | 返回 `index.html`（SPA History 模式） |
| `/static/` | 静态资源（long-term cache + hash 文件名） |
| `/api/*` | 反向代理到后端 `http://qcvmt-api:8080` |
| 旧 JSP URL | rewrite → SPA 对应路由 |

### 9.3 Vite 开发代理

```typescript
// vite.config.ts
export default defineConfig({
  plugins: [react()],
  resolve: { alias: { '@': path.resolve(__dirname, 'src') } },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
    },
  },
})
```

---

## 10. 旧系统 → 新系统映射（完整）

| 旧文件 | 新文件/组件 | 迁移策略 |
|--------|-----------|---------|
| `index.jsp` | `router` 默认路由 + `AuthGuard` | Rewrite |
| `login.jsp` | `LoginPage.tsx` + Keycloak OIDC | Rewrite |
| `loginAdmin.jsp` | 移除（Keycloak 统一登录） | Remove |
| `tqcvmt.jsp` | `TerminalPage.tsx` + `BayPlanGrid.tsx` + `BayCell.tsx` | Rewrite |
| `vmt.js` → 轮询 | `hooks/usePolling.ts` | Refactor |
| `vmt.js` → 时间同步 | `hooks/useServerClock.ts` | Refactor |
| `vmt.js` → XML 解析 | 移除（改用 JSON API） | Remove |
| `vmt.js` → `checkNumber()` | `src/utils/validators.ts` (Zod) | Refactor |
| `vmt.js` → `Date.prototype.format()` | dayjs | Remove |
| `vmt.js` → 信号指示 | `SignalIndicator.tsx` | Refactor |
| `admin.jsp` | `DashboardPage.tsx` | Rewrite |
| `userDetail.jsp` / `update.jsp` | `UserForm.tsx`（复用） | Rewrite |
| `log.jsp` | `UserLogs.tsx` | Rewrite |
| `setbaysize.jsp` | `BaySizeForm.tsx` | Rewrite |
| `colorManage.jsp` | `ColorSetList.tsx` | Rewrite |
| `colSetDetail.jsp` / `updateColSet.jsp` | `ColorSetForm.tsx`（复用） | Rewrite |
| `vesselManage.jsp` | `VesselList.tsx` | Rewrite |
| `vesselDetail.jsp` / `updateVessel.jsp` | `VesselForm.tsx`（复用） | Rewrite |
| `vesselRefuelManage.jsp` | `VesselRefuelList.tsx` | Rewrite |
| `vesselRefuelDetail.jsp` | `VesselRefuelForm.tsx` | Rewrite |
| `vesselColorManage.jsp` | `VesselColorList.tsx` | Rewrite |
| `vesselColorDetail.jsp` | `VesselColorForm.tsx` | Rewrite |
| `importPage.jsp` | `ImportPage.tsx` | Rewrite |
| `exportPage.jsp` | `ExportPage.tsx` | Rewrite |
| `box.css` | `global.css` + `bay-plan.module.css` | Refactor |
| `colorPickerStyle.css` | Ant Design `ColorPicker` | Remove |
| `jquery.soColorPicker-1.0.js` | Ant Design `ColorPicker` | Remove |
| `jquery.bgiframe-2.1.2.js` | 移除（IE6 修复） | Remove |
| `jquery-1.11.1.min.js` | 移除（React 替代） | Remove |
| `green.gif` / `red.gif` | `src/assets/images/` 保留 | Keep |
| `messages_en.properties` | `src/locales/en.json` | Move |
| `messages_zh_TW.properties` | `src/locales/zh-TW.json` | Move |
| `messages_zh_CN.properties` | `src/locales/zh-CN.json` | Move |
| `system.properties` | 后端 `application.yml` | Remove |
| `springMVC-servlet.xml` | 移除（Spring Boot 配置替代） | Remove |
| `web.xml` | 移除（Spring Boot 内嵌 Tomcat） | Remove |
| JSP 内联 `<style>` (#d1 × 21) | `AdminLayout.tsx` 统一布局 | Refactor |
| JSP 内联 `sh()` 函数 (× 21) | `usePermission.ts` + `ConfirmDialog.tsx` | Refactor |
| `<pg:pager>` 分页标签 | Ant Design `Pagination` | Rewrite |
| IE `expression()` CSS | 移除 | Remove |
