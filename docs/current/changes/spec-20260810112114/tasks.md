# QCVMT 前端改造 — 可执行开发计划

> **变更标识**：spec-20260810112114  
> **生成日期**：2026-08-10  
> **输入依据**：Frontend Technical Design (S00601) + analysis.md + proposal.md  

---

## Phase 1 — 前端基础骨架

### 任务 1.1 初始化 Vite + React 18 + TypeScript 项目

- [ ] **目标**：建立可独立构建运行的 React 前端项目骨架
- [ ] **新建目录**：`qcvmt-frontend/`（与后端项目 `src/` 同级）
- [ ] **操作文件**：
  - 新增：`qcvmt-frontend/package.json`
  - 新增：`qcvmt-frontend/index.html`
  - 新增：`qcvmt-frontend/tsconfig.json`
  - 新增：`qcvmt-frontend/tsconfig.node.json`

```json
// package.json scripts
{
  "dev": "vite",
  "build": "tsc --noEmit && vite build",
  "preview": "vite preview",
  "lint": "eslint src --ext .ts,.tsx --fix",
  "test": "vitest",
  "test:ci": "vitest run --coverage"
}
```

- [ ] **依赖安装**（运行时）：
  `antd@^5` `axios@^1` `keycloak-js@^25` `react-router-dom@^6` `zustand@^4`
  `react-i18next` `i18next` `react-hook-form` `@hookform/resolvers`
  `zod@^3` `dayjs@^1` `@ant-design/icons` `react@^18` `react-dom@^18`

- [ ] **开发依赖安装**：
  `@vitejs/plugin-react` `vite@^5` `typescript@^5` `vitest`
  `@testing-library/react` `@testing-library/jest-dom` `jsdom`
  `eslint` `prettier` `eslint-plugin-react-hooks` `eslint-plugin-react-refresh`
  `@types/react` `@types/react-dom`

- [ ] **入口文件**：
  - 新增：`qcvmt-frontend/src/main.tsx`（占位符，渲染 `<App />`）
  - 新增：`qcvmt-frontend/src/App.tsx`（占位符，显示 "QCVMT Loading..."）
  - 新增：`qcvmt-frontend/src/vite-env.d.ts`

- [ ] **验收标准**：`npm run dev` 浏览器访问 `http://localhost:5173` 显示 "QCVMT Loading..."

---

### 任务 1.2 配置 Vite（proxy、alias、环境变量）

- [ ] **新增文件**：
  - `qcvmt-frontend/vite.config.ts`
  - `qcvmt-frontend/.env`
  - `qcvmt-frontend/.env.development`
  - `qcvmt-frontend/.env.production`

```ts
// vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: { alias: { '@': path.resolve(__dirname, 'src') } },
  server: {
    port: 5173,
    proxy: {
      '/api': { target: 'http://localhost:8080', changeOrigin: true },
    },
  },
})
```

```ini
# .env.development
VITE_API_BASE_URL=/api
VITE_KEYCLOAK_URL=http://localhost:8180
VITE_KEYCLOAK_REALM=qcvmt
VITE_KEYCLOAK_CLIENT_ID=qcvmt-frontend

# .env.production
VITE_API_BASE_URL=/api
VITE_KEYCLOAK_URL=https://keycloak.example.com
VITE_KEYCLOAK_REALM=qcvmt
VITE_KEYCLOAK_CLIENT_ID=qcvmt-frontend
```

- [ ] `tsconfig.json` 中 `"paths": { "@/*": ["src/*"] }`

- [ ] **验收标准**：
  - `npm run dev` 启动成功
  - `VITE_API_BASE_URL` 在代码中可通过 `import.meta.env.VITE_API_BASE_URL` 访问
  - `npm run build` 构建成功无 TS 错误

---

### 任务 1.3 配置 ESLint + Prettier + VSCode 设置

- [ ] **新增文件**：
  - `qcvmt-frontend/.eslintrc.cjs`
  - `qcvmt-frontend/.prettierrc`
  - `qcvmt-frontend/.prettierignore`

```json
// .prettierrc
{ "semi": false, "singleQuote": true, "trailingComma": "all", "printWidth": 100 }
```

- [ ] package.json 中 script：`"lint": "eslint src --ext .ts,.tsx --fix"`

- [ ] **验收标准**：`npm run lint` 无报错

---

### 任务 1.4 配置 Ant Design 主题与全局样式

- [ ] **新增文件**：
  - `qcvmt-frontend/src/styles/theme.ts`
  - `qcvmt-frontend/src/styles/global.css`

```ts
// src/styles/theme.ts
import type { ThemeConfig } from 'antd'

export const antdTheme: ThemeConfig = {
  token: {
    colorPrimary: '#1677ff',
    borderRadius: 6,
    fontFamily: "'Segoe UI', Roboto, sans-serif",
  },
}
```

- [ ] `global.css` 包含：重置样式 + MODERN TERMINALS 品牌色系基础变量
- [ ] **验收标准**：`<ConfigProvider theme={antdTheme}>` 在 `App.tsx` 中可应用

---

### 任务 1.5 创建基础目录结构

- [ ] **新建以下空目录**（在 `qcvmt-frontend/src/` 下）：

```
lib/          # 第三方库初始化
router/       # 路由
stores/       # Zustand stores
api/          # API 模块
hooks/        # 自定义 Hooks
pages/        # 页面组件
components/   # 可复用组件
types/        # TypeScript 类型
utils/        # 工具函数
locales/      # i18n JSON
assets/images/# 静态图片资源
```

- [ ] **验收标准**：目录结构完整，`npm run build` 成功

---

### 任务 1.6 Phase 1 验证

- [ ] `npm run dev` 启动成功
- [ ] `npm run build` 无 TS 编译错误
- [ ] `npm run lint` 无 eslint 错误
- [ ] 目录结构符合 Section 9 规范

---

## Phase 2 — API 层与 TypeScript 类型

### 任务 2.1 通用 API 类型定义

- [ ] **新增文件**：`qcvmt-frontend/src/api/types.ts`

```ts
// src/api/types.ts
export interface ApiResponse<T> {
  code: number
  message: string
  data: T
  timestamp: number
}

export interface PageParams {
  page?: number
  size?: number
}

export interface PageResponse<T> {
  content: T[]
  totalElements: number
  totalPages: number
  number: number
  size: number
}

export const ERROR_CODES = {
  400: '请求参数错误',
  401: '未登录或登录过期',
  403: '权限不足',
  404: '资源不存在',
  500: '服务器内部错误',
  503: 'N4 系统连接失败',
} as const
```

- [ ] **验收标准**：TypeScript 编译无错误

---

### 任务 2.2 Axios 实例 + 请求/响应拦截器

- [ ] **新增文件**：`qcvmt-frontend/src/lib/axios.ts`

```ts
// src/lib/axios.ts
import axios from 'axios'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

apiClient.interceptors.request.use((config) => {
  const token = (window as any).__keycloak?.token
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

apiClient.interceptors.response.use(
  (response) => response.data,
  async (error) => {
    if (error.response?.status === 401) {
      // 触发重新登录（Phase 3 由 keycloak 接管）
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default apiClient
```

- [ ] **测试命令**：`npx vitest run src/lib/axios.test.ts`
- [ ] **验收标准**：拦截器逻辑单元测试通过

---

### 任务 2.3 核心业务类型定义（5 个文件）

依据 analysis.md Section 1.2 的实体和 Frontend Tech Design Section 19 的类型设计：

- [ ] **新增文件**：`qcvmt-frontend/src/types/user.ts`

```ts
export interface User {
  id: number
  qcid: string
  username: string
  role: 'ADMIN' | 'USER'
  parent: string
  createtime: string
}

export interface CreateUserRequest {
  qcid: string
  username: string
  role: 'ADMIN' | 'USER'
  parent: string
}

export type UpdateUserRequest = Partial<CreateUserRequest>

export interface ShowLog {
  userlogid: number
  userid: string
  username: string
  qcid: string
  logintime: string
  operation: string
}
```

- [ ] **新增文件**：`qcvmt-frontend/src/types/vessel.ts`

```ts
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

export type CreateVesselRequest = Omit<Vessel, 'id'>
export type UpdateVesselRequest = Partial<CreateVesselRequest>

export interface VesselCol {
  vcid: number
  vesselid: string
  deck_hold: 'A' | 'B'
  bay: string
  rowStart: string
  rowEnd: string
  tierStart: string
  tierEnd: string
}

export interface VesselRefuel {
  vrid: number
  vesselid: string
  is_refuel: string
}
```

- [ ] **新增文件**：`qcvmt-frontend/src/types/colorSet.ts`

```ts
export interface ColSet {
  colsetid: number
  color: string
  boxcase: string
}

export type CreateColSetRequest = Omit<ColSet, 'colsetid'>
export type UpdateColSetRequest = Partial<CreateColSetRequest>
```

- [ ] **新增文件**：`qcvmt-frontend/src/types/terminal.ts`

```ts
export interface TerminalView {
  vessels: Vessel[]
  workQueue: WorkQueueResult
  colorSets: ColSet[]
  rob: RobContainer[]
  vesselId: string
  bay: string
  deckHold: string
  qType: string
  remainContainers: number
  dateTimeNow: string
}

export interface WorkQueueResult {
  qorder: string
  vesselId: string
  minBay: string
  maxBay: string
  deckHold: string
  sequences: SequenceVO[]
}

export interface SequenceVO {
  currentPosSlot: string
  plannedPosSlot: string
  qtype: 'LOAD' | 'DISCH'
  qdeck: string
  qrow: string
  status: string
  bay: string
  isOog: string
  isPowered: string
  isTank: string
  isDg: string
  isQuad: boolean
  isTandem: boolean
  isTwin: boolean
  isSingle: boolean
  isTwenty: boolean
  cellType: CellType
}

export type CellType =
  | 'inactive' | 'unable' | 'empty'
  | 'discharge' | 'load' | 'complexunit'
  | 'twenty' | 'refuel'

export interface RobContainer {
  slot: string
  containerId: string
  bay: string
  row: string
  tier: string
}

import type { Vessel } from './vessel'
import type { ColSet } from './colorSet'
```

- [ ] **新增文件**：`qcvmt-frontend/src/types/bayConfig.ts`

```ts
export interface BaySize {
  matrixid: number
  cmtype: string
  cmrow: string
  cmtier: string
  active: string
}

export interface OperationLog {
  operlogid: number
  username: string
  function: string
  actiontype: string
  valuechange: string
  time: string
}
```

- [ ] **验收标准**：所有类型文件 `tsc --noEmit` 无错误

---

### 任务 2.4 API 模块（9 个）

每个模块均基于 `apiClient`，返回 `Promise<ApiResponse<T>>`。

#### 2.4.1 terminal API

- [ ] **新增文件**：`qcvmt-frontend/src/api/terminal.ts`

```ts
import apiClient from '@/lib/axios'
import type { ApiResponse } from './types'
import type { TerminalView } from '@/types/terminal'

export const terminalApi = {
  query(qcNum: string): Promise<ApiResponse<TerminalView>> {
    return apiClient.get('/api/terminal/query', { params: { qcNum } })
  },
}
```

#### 2.4.2 user API

- [ ] **新增文件**：`qcvmt-frontend/src/api/user.ts`
  - `list(params: PageParams)` → `GET /api/users`
  - `create(data: CreateUserRequest)` → `POST /api/users`
  - `update(id, data: UpdateUserRequest)` → `PUT /api/users/{id}`
  - `remove(id)` → `DELETE /api/users/{id}`
  - `logs(id)` → `GET /api/users/{id}/logs`

#### 2.4.3 vessel API

- [ ] **新增文件**：`qcvmt-frontend/src/api/vessel.ts`
  - `list(params)` → `GET /api/vessels`
  - `create(data)` → `POST /api/vessels`
  - `update(id, data)` → `PUT /api/vessels/{id}`
  - `remove(id)` → `DELETE /api/vessels/{id}`

#### 2.4.4 colorSet API

- [ ] **新增文件**：`qcvmt-frontend/src/api/colorSet.ts`
  - `list` → `GET /api/color-sets`
  - `create` → `POST /api/color-sets`
  - `update(id, data)` → `PUT /api/color-sets/{id}`

#### 2.4.5 vesselColor API

- [ ] **新增文件**：`qcvmt-frontend/src/api/vesselColor.ts`
  - `list` → `GET /api/vessel-colors`
  - `create` → `POST /api/vessel-colors`
  - `remove(id)` → `DELETE /api/vessel-colors/{id}`

#### 2.4.6 vesselRefuel API

- [ ] **新增文件**：`qcvmt-frontend/src/api/vesselRefuel.ts`
  - `list` → `GET /api/vessel-refuels`
  - `create(data)` → `POST /api/vessel-refuels`
  - `remove(id)` → `DELETE /api/vessel-refuels/{id}`

#### 2.4.7 bayConfig API

- [ ] **新增文件**：`qcvmt-frontend/src/api/bayConfig.ts`
  - `get()` → `GET /api/bay-config`
  - `update(data)` → `PUT /api/bay-config`

#### 2.4.8 operationLog API

- [ ] **新增文件**：`qcvmt-frontend/src/api/operationLog.ts`
  - `list(params)` → `GET /api/operation-logs`

#### 2.4.9 importExport API

- [ ] **新增文件**：`qcvmt-frontend/src/api/importExport.ts`
  - `importVessel(file: File)` → `POST /api/import/vessel`（multipart）
  - `exportLogs(from, to)` → `GET /api/export/logs?from=x&to=y`（blob）

- [ ] **验收标准**：`npm run build` 成功；每个模块的 `tsc --noEmit` 无类型错误

---

### 任务 2.5 API 层单元测试

- [ ] **新增文件**：`qcvmt-frontend/src/lib/axios.test.ts`
  - 验证拦截器对 401 跳转的处理
- [ ] **新增文件**：`qcvmt-frontend/src/api/terminal.test.ts`
  - 使用 `vitest` mock axios，验证 `terminalApi.query('QC01')` 正确发送请求
- [ ] **测试命令**：`npx vitest run src/api/ src/lib/`
- [ ] **预期结果**：所有测试用例 pass
- [ ] **验收标准**：测试覆盖率 ≥ 80% 针对 API 层

---

## Phase 3 — 认证 / 路由 / i18n / 布局

### 任务 3.1 Keycloak 集成初始化

- [ ] **新增文件**：`qcvmt-frontend/src/lib/keycloak.ts`

```ts
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
    checkLoginIframe: false, // 开发阶段关闭 iframe，生产环境按运维配置开启
  })
}

export default keycloak
```

- [ ] **新增文件**：`qcvmt-frontend/public/silent-check-sso.html`

```html
<!doctype html>
<html>
<body>
<script>parent.postMessage(location.href, location.origin)</script>
</body>
</html>
```

- [ ] **验收标准**：Keycloak 实例初始化无报错；`initKeycloak()` 可在 `main.tsx` 入口调用

---

### 任务 3.2 Zustand Stores（auth + app + terminal placeholder）

- [ ] **新增文件**：`qcvmt-frontend/src/stores/auth.ts`

```ts
import { create } from 'zustand'
import keycloak from '@/lib/keycloak'
import type { User } from '@/types/user'

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isAdmin: boolean
  token: string
  roles: string[]
  login: () => Promise<void>
  logout: () => Promise<void>
  refreshUser: (user: User) => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isAdmin: false,
  token: '',
  roles: [],
  login: async () => {
    if (!keycloak.authenticated) await keycloak.login()
  },
  logout: async () => { await keycloak.logout() },
  refreshUser: (user: User) => {
    set({
      user,
      isAuthenticated: true,
      isAdmin: keycloak.realmAccess?.roles?.includes('qcvmt-admin') ?? false,
      token: keycloak.token ?? '',
      roles: keycloak.realmAccess?.roles ?? [],
    })
  },
}))
```

- [ ] **新增文件**：`qcvmt-frontend/src/stores/app.ts`

```ts
import { create } from 'zustand'

interface AppState {
  locale: 'en' | 'zh-CN' | 'zh-TW'
  sidebarCollapsed: boolean
  setLocale: (locale: AppState['locale']) => void
  toggleSidebar: () => void
}

export const useAppStore = create<AppState>((set) => ({
  locale: 'en',
  sidebarCollapsed: false,
  setLocale: (locale) => set({ locale }),
  toggleSidebar: () => set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),
}))
```

- [ ] `src/stores/terminal.ts`：Phase 4 创建
- [ ] **验收标准**：Zustand stores 可被 hooks 正常订阅

---

### 任务 3.3 i18n 迁移（properties → JSON + react-i18next）

- [ ] **新增文件**：
  - `qcvmt-frontend/src/locales/en.json`
  - `qcvmt-frontend/src/locales/zh-CN.json`
  - `qcvmt-frontend/src/locales/zh-TW.json`

> **迁移来源**：后端 `src/main/resources/messages_en.properties` 等  
> 将所有 `key=value` 格式转换为 JSON 嵌套对象（如 `nav.home` → `{ "nav": { "home": "首页" }}`）

- [ ] **新增文件**：`qcvmt-frontend/src/lib/i18n.ts`

```ts
import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import en from '@/locales/en.json'
import zhCN from '@/locales/zh-CN.json'
import zhTW from '@/locales/zh-TW.json'

i18n.use(initReactI18next).init({
  resources: {
    en: { translation: en },
    'zh-CN': { translation: zhCN },
    'zh-TW': { translation: zhTW },
  },
  lng: navigator.language.startsWith('zh') ? 'zh-CN' : 'en',
  fallbackLng: 'en',
  interpolation: { escapeValue: false },
})

export default i18n
```

- [ ] **测试命令**：运行脚本对比 properties 和 json 文件的 key 完整性
  ```bash
  # 检查 en.json 是否包含所有 properties 中的 key
  node -e "
  const fs=require('fs'); 
  const props=fs.readFileSync('src/main/resources/messages_en.properties','utf8');
  const keys=[...props.matchAll(/^[^#][^=]+=/gm)].map(m=>m[0].slice(0,-1).trim().replace(/\\./g,'.'));
  const json=JSON.parse(fs.readFileSync('qcvmt-frontend/src/locales/en.json','utf8'));
  const jsonKeys=Object.keys(json).flat(Infinity);
  const missing=keys.filter(k=>!Object.keys(JSON.parse(JSON.stringify(json))).includes(k));
  console.log('Missing keys:',missing.length?missing:'none')
  "
  ```
- [ ] **验收标准**：`i18next.t('key')` 在三个语言切换时返回正确翻译

---

### 任务 3.4 路由定义 + AuthGuard

- [ ] **新增文件**：`qcvmt-frontend/src/router/index.tsx`

  路由表（按 proposal.md Section 4.2）：
  - `/login` → `LoginPage`（公开）
  - `/terminal` → `TerminalPage`（AuthGuard，qcvmt-admin / qcvmt-user）
  - `/admin` → `AdminLayout`（AuthGuard，requireAdmin）
    - index → `DashboardPage`
    - `users` / `users/new` / `users/:id/edit` / `users/:id/logs`
    - `vessels` / `vessels/new` / `vessels/:id/edit`
    - `color-sets` / `color-sets/new` / `color-sets/:id/edit`
    - `vessel-colors` / `vessel-colors/new` / `vessel-colors/:id/edit`
    - `vessel-refuels` / `vessel-refuels/new` / `vessel-refuels/:id/edit`
    - `bay-config`
    - `import`
    - `export`
  - `*` → 重定向到 `/terminal`

- [ ] **新增文件**：`qcvmt-frontend/src/components/common/AuthGuard.tsx`

```tsx
import { Navigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/auth'
import keycloak from '@/lib/keycloak'

interface AuthGuardProps {
  children: React.ReactNode
  requireAdmin?: boolean
}

export function AuthGuard({ children, requireAdmin }: AuthGuardProps) {
  const { isAuthenticated, isAdmin } = useAuthStore()

  if (!keycloak.authenticated || !isAuthenticated) return null

  if (requireAdmin && !isAdmin) {
    return <Navigate to="/terminal" replace />
  }

  return <>{children}</>
}
```

- [ ] **验收标准**：
  - 未登录访问 `/terminal` → 触发 `keycloak.login()` 重定向
  - 非 admin 用户访问 `/admin/users` → 重定向到 `/terminal`

---

### 任务 3.5 布局组件（TerminalLayout + AdminLayout + AppHeader）

- [ ] **新增文件**：`qcvmt-frontend/src/components/layout/TerminalLayout.tsx`
  - 全屏无 header 布局，深色背景（匹配旧 `tqcvmt.jsp` 样式）
  - 仅渲染子组件（Bay Plan 区域全屏）

- [ ] **新增文件**：`qcvmt-frontend/src/components/layout/AdminLayout.tsx`
  - Ant Design `Layout` + `Menu` 侧边栏 + `<Outlet />`
  - 菜单项：用户管理、船舶管理、颜色设置、加油管理、贝位颜色、Bay 尺寸、导入、导出
  - 按 `isAdmin` / `roles` 控制菜单可见性（受限账户仅显示 vessel-refuels / vessel-colors）

- [ ] **新增文件**：`qcvmt-frontend/src/components/layout/AppHeader.tsx`
  - MODERN TERMINALS 品牌 Logo
  - 当前用户名 + 登出按钮
  - 语言切换器（en / 繁体 / 简体）

- [ ] **验收标准**：
  - `AdminLayout` 渲染侧边栏所有菜单项正确
  - 受限账户（`limitAccount` 角色）仅见指定菜单
  - 语言切换器调用 `i18n.changeLanguage()`

---

### 任务 3.6 LoginPage 组件

- [ ] **新增文件**：`qcvmt-frontend/src/pages/login/LoginPage.tsx`
  - Keycloak 重定向登录页（无手动表单）
  - 显示 Loading + 品牌 Logo
  - 登录失败时显示错误 + 重试按钮

- [ ] **验收标准**：
  - 访问 `/login` 自动调用 `keycloak.login()`
  - 登录成功后跳转 `/terminal`

---

### 任务 3.7 Zod 验证 Schema（迁移自 JSP 内联 JS）

- [ ] **新增文件**：`qcvmt-frontend/src/utils/validators.ts`

```ts
import { z } from 'zod'

// 奇偶校验（rowStart 与 rowEnd 必须同奇偶）
export const tierParityRefine = z.object({
  rowStart: z.string().regex(/^\d+$/).max(3),
  rowEnd: z.string().regex(/^\d+$/).max(3),
}).refine(
  (d) => Number(d.rowStart) <= Number(d.rowEnd),
  { message: 'Start Row cannot be larger than End Row', path: ['rowEnd'] }
).refine(
  (d) => Number(d.rowStart) % 2 === Number(d.rowEnd) % 2,
  { message: 'Start Row and End Row must be both odd or even', path: ['rowEnd'] }
)

export const vesselColorSchema = z.object({
  vesselid: z.string().min(1, 'Vessel Visit Id cannot be empty').max(30),
  deck_hold: z.enum(['A', 'B']),
  bay: z.string().min(1).max(10).regex(/^\d+$/, 'Bay must be numeric'),
  rowStart: z.string().min(1).regex(/^\d+$/),
  rowEnd: z.string().min(1).regex(/^\d+$/),
  tierStart: z.string().max(2).regex(/^\d*$/).optional().default('00'),
  tierEnd: z.string().max(3).regex(/^\d*$/).optional().default('20'),
}).superRefine((d, ctx) => {
  if (Number(d.rowStart) > Number(d.rowEnd))
    ctx.addIssue({ code: 'custom', message: 'Start Row > End Row', path: ['rowEnd'] })
  if (Number(d.rowStart) % 2 !== Number(d.rowEnd) % 2)
    ctx.addIssue({ code: 'custom', message: 'Rows must be same parity', path: ['rowEnd'] })
})

export const vesselSchema = z.object({
  vesselid: z.string().min(1, 'Vessel Id required').max(30),
  deck_hold: z.enum(['A', 'B']),
  bay: z.string().min(1).regex(/^\d+$/),
  rowStart: z.string().regex(/^\d+$/),
  rowEnd: z.string().regex(/^\d+$/),
  tierStart: z.string().regex(/^\d*$/).optional(),
  tierEnd: z.string().regex(/^\d*$/).optional(),
})

export const userSchema = z.object({
  qcid: z.string().min(1, 'QCID required').max(20),
  username: z.string().min(1, 'Username required').max(50),
  role: z.enum(['ADMIN', 'USER']),
  parent: z.string().max(50).optional().default(''),
})

export const colorSetSchema = z.object({
  color: z.string().min(1, 'Color required'),
  boxcase: z.enum(['inactive','unable','empty','discharge','load','complexunit','twenty','refuel']),
})
```

- [ ] **新增文件**：`qcvmt-frontend/src/utils/validators.test.ts`
  - 测试 `vesselColorSchema`：奇数+偶数 → 报错；奇数+奇数 → 通过
  - 测试 bay 必须为数字

- [ ] **测试命令**：`npx vitest run src/utils/`
- [ ] **验收标准**：所有验证器单元测试通过

---

### 任务 3.8 公共组件（ConfirmDialog + SearchBar）

- [ ] **新增文件**：`qcvmt-frontend/src/components/common/ConfirmDialog.tsx`
  - 封装 `Modal.confirm`（替代 JSP 中 21 处重复的 `sh()` 确认函数）
  - Props：`title`, `content`, `onConfirm`, `onCancel`

- [ ] **新增文件**：`qcvmt-frontend/src/components/common/SearchBar.tsx`
  - Ant Design `Input.Search`，Props：`placeholder`, `onSearch`

- [ ] **验收标准**：组件可正常渲染

---

## Phase 4 — 核心业务模块（QC 终端页）

### 任务 4.1 usePolling 自适应轮询 Hook（高优先级，高风险）

- [ ] **新增文件**：`qcvmt-frontend/src/hooks/usePolling.ts`

**核心逻辑（迁移自 vmt.js L60-173，三种模式）**：

```
模式 1 (manual)：用户手动点击触发，不轮询
模式 2 (auto)：自动轮询，固定 interval（默认 15000ms）
模式 3 (adaptive)：自适应退避
  - 连续成功 → interval = 15000ms
  - 连续超时 1 次 → 20000ms
  - 连续超时 2 次 → 25000ms
  - 连续超时 3+ 次 → 30000ms（上限）
  - 成功后重置为 15000ms
```

```ts
import { useCallback, useEffect, useRef } from 'react'

type PollingMode = 'manual' | 'auto' | 'adaptive'

interface UsePollingOptions {
  mode: PollingMode
  initialInterval?: number  // ms, 默认 15000
  maxInterval?: number      // ms, 默认 30000
  step?: number             // ms, 默认 5000
}

interface UsePollingReturn {
  start: () => void
  stop: () => void
  currentInterval: number
  timeoutCount: number
}

export function usePolling(
  fetcher: () => Promise<void>,
  options: UsePollingOptions = { mode: 'adaptive' }
): UsePollingReturn {
  const intervalRef = useRef(options.initialInterval ?? 15000)
  const timeoutCountRef = useRef(0)
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  const schedule = useCallback(() => {
    if (timerRef.current) clearTimeout(timerRef.current)
    timerRef.current = setTimeout(async () => {
      try {
        await fetcher()
        // 成功 → 重置
        timeoutCountRef.current = 0
        intervalRef.current = options.initialInterval ?? 15000
      } catch {
        timeoutCountRef.current += 1
        const max = options.maxInterval ?? 30000
        const step = options.step ?? 5000
        intervalRef.current = Math.min(
          (options.initialInterval ?? 15000) + timeoutCountRef.current * step,
          max
        )
      } finally {
        if (options.mode !== 'manual') schedule()
      }
    }, intervalRef.current)
  }, [fetcher, options])

  const start = useCallback(() => {
    timeoutCountRef.current = 0
    intervalRef.current = options.initialInterval ?? 15000
    schedule()
  }, [schedule])

  const stop = useCallback(() => {
    if (timerRef.current) clearTimeout(timerRef.current)
  }, [])

  useEffect(() => () => stop(), [stop])

  return {
    start,
    stop,
    currentInterval: intervalRef.current,
    timeoutCount: timeoutCountRef.current,
  }
}
```

- [ ] **新增文件**：`qcvmt-frontend/src/hooks/__tests__/usePolling.test.ts`

测试场景：
- 连续成功：interval 保持 15000ms
- 连续超时 1/2/3 次：interval 分别为 20000/25000/30000ms
- 超时后成功：interval 重置为 15000ms
- mode='manual'：不调用 start 不触发

- [ ] **测试命令**：`npx vitest run src/hooks/`
- [ ] **验收标准**：所有测试用例 pass

---

### 任务 4.2 useServerClock Hook

- [ ] **新增文件**：`qcvmt-frontend/src/hooks/useServerClock.ts`

**迁移逻辑（来自 vmt.js `setTime() + showTime() + calculateCurrentTime()`）**：
- 接收 API 返回的服务器时间 `serverTime: string`
- 计算本地时钟与服务器时钟的偏移量 `offset = serverTime - Date.now()`
- 使用 `setInterval(1000ms)` 每秒更新显示时间 = `Date.now() + offset`

```ts
import { useState, useEffect, useRef } from 'react'

export function useServerClock(serverTime: string | null) {
  const [displayTime, setDisplayTime] = useState('')
  const offsetRef = useRef(0)

  useEffect(() => {
    if (!serverTime) return
    offsetRef.current = new Date(serverTime).getTime() - Date.now()
  }, [serverTime])

  useEffect(() => {
    const id = setInterval(() => {
      const now = new Date(Date.now() + offsetRef.current)
      setDisplayTime(now.toISOString().replace('T', ' ').slice(0, 19))
    }, 1000)
    return () => clearInterval(id)
  }, [])

  return displayTime
}
```

- [ ] **新增文件**：`qcvmt-frontend/src/hooks/__tests__/useServerClock.test.ts`
- [ ] **测试命令**：`npx vitest run src/hooks/`
- [ ] **验收标准**：时钟每秒更新；传入新 serverTime 后偏移量重新校准

---

### 任务 4.3 terminal Store（Zustand）

- [ ] **新增文件**：`qcvmt-frontend/src/stores/terminal.ts`

```ts
import { create } from 'zustand'
import { terminalApi } from '@/api/terminal'
import type { TerminalView, CellType } from '@/types/terminal'

interface TerminalState {
  data: TerminalView | null
  signalStatus: 'green' | 'red'
  isLoading: boolean
  error: string | null
  fetchTerminalData: (qcNum: string) => Promise
  reset: () => void
}

export const useTerminalStore = create<TerminalState>((set) => ({
  data: null,
  signalStatus: 'red',
  isLoading: false,
  error: null,

  fetchTerminalData: async (qcNum: string) => {
    set({ isLoading: true, error: null })
    try {
      const res = await terminalApi.query(qcNum)
      set({
        data: res.data,
        signalStatus: 'green',
        isLoading: false,
      })
    } catch (e: any) {
      set({
        signalStatus: 'red',
        error: e?.message ?? 'Unknown error',
        isLoading: false,
      })
      throw e
    }
  },

  reset: () => set({ data: null, signalStatus: 'red', isLoading: false, error: null }),
}))
```

- [ ] **验收标准**：`fetchTerminalData('QC01')` 成功时 signalStatus='green'；失败时 signalStatus='red'

---

### 任务 4.4 Bay Plan CSS 样式迁移

- [ ] **新增文件**：`qcvmt-frontend/src/styles/bay-plan.module.css`

从 `tqcvmt.jsp` 内联 CSS 迁移，8 种 cell type 的 className：

| CSS Class | 背景色 | 字体 | 条件 |
|-----------|-------|------|------|
| `.inactive` | ColSet `inactive` 颜色 | 默认 | 非活跃位置 |
| `.unable` | ColSet `unable` 颜色 | 默认 | 禁用位置 |
| `.empty` | ColSet `empty` 颜色 | 默认 | 空位 |
| `.discharge` | ColSet `discharge` 颜色 | 默认 | 卸箱（DISCH） |
| `.load` | ColSet `load` 颜色 | 默认 | 装箱（LOAD） |
| `.complexunit` | ColSet `complexunit` 颜色 | 默认 | 连体箱 |
| `.twenty` | ColSet `inactive` 背景 + 红色文字 | 红色文字 | 20ft 箱 |
| `.refuel` | 红色背景 + 红色文字 | 红色 | 加油区域 |
| `.dgInd` | 黄色背景 + 红色文字 | 绝对定位右上角 | 危险品集装箱 |

```css
/* src/styles/bay-plan.module.css */
.cell {
  width: 40px;
  height: 28px;
  border: 1px solid #666;
  text-align: center;
  font-size: 11px;
  padding: 2px;
  position: relative;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.inactive  { background-color: #cccccc; }
.unable    { background-color: #333333; color: #999; }
.empty     { background-color: #ffffff; }
.discharge { background-color: #00b050; }
.load      { background-color: #0070c0; color: #fff; }
.complexunit { background-color: #ffc000; }
.twenty    { background-color: #cccccc; color: #ff0000; font-weight: bold; }
.refuel    { background-color: #ff0000; color: #fff; }

.dgInd {
  position: absolute;
  top: 0; right: 0;
  background: #ffee00;
  color: #ff0000;
  font-size: 9px;
  padding: 0 2px;
  line-height: 12px;
  font-weight: bold;
}
```

- [ ] **验收标准**：CSS Modules 正确作用域隔离，无全局冲突

---

### 任务 4.5 BayCell 组件（React.memo 优化，高风险）

- [ ] **新增文件**：`qcvmt-frontend/src/components/bay/BayCell.tsx`

**渲染规则（迁移自 `CellDaoImpl.buildBay()` 中的 400 行逻辑）**：

```tsx
import { memo } from 'react'
import styles from '@/styles/bay-plan.module.css'
import type { CellType } from '@/types/terminal'

interface BayCellProps {
  type: CellType
  label?: string
  isDg?: boolean
  bgColor?: string   // ColSet 中对应颜色的精确 RGB
}

export const BayCell = memo(function BayCell({ type, label, isDg, bgColor }: BayCellProps) {
  return (
    <td
      className={`${styles.cell} ${styles[type]}`}
      style={bgColor ? { backgroundColor: bgColor } : undefined}
    >
      {label}
      {isDg && <span className={styles.dgInd}>DG</span>}
    </td>
  )
}, (prev, next) => {
  return (
    prev.type === next.type &&
    prev.label === next.label &&
    prev.isDg === next.isDg &&
    prev.bgColor === next.bgColor
  )
})
```

- [ ] **关键业务规则**（必须在组件注释中标注，不可遗漏）：
  1. **20ft 箱检测**：仅在 `DISCH` 模式、单 Bay、偶数 Bay 时触发，`isTwenty = true`
  2. **连体箱**：`complexunit` 可能跨 Bay 显示，需标记在两个相邻 Bay 的同一位置
  3. **DG 标识**：`isDg === '1'` 时显示 DG 角标（旧代码使用 `==` 比较，前端使用字符串比较）
  4. **Tier 编号**：Hold: 00/02/04/06/08/10...; Deck: 78/80/82...（由后端在 JSON 中提供）

- [ ] **新增文件**：`qcvmt-frontend/src/components/bay/__tests__/BayCell.test.ts`
  - 测试：给定 `type='discharge'` → 渲染绿色背景
  - 测试：`isDg=true` → 渲染 DG 角标
  - 测试：`type='twenty'` → 红色文字

- [ ] **测试命令**：`npx vitest run src/components/bay/`
- [ ] **验收标准**：`React.memo` 避免未变化单元格重渲染；所有 CellType 视觉样式与旧系统截图一致

---

### 任务 4.6 SignalIndicator 组件

- [ ] **新增文件**：`qcvmt-frontend/src/components/bay/SignalIndicator.tsx`

```tsx
interface SignalIndicatorProps {
  status: 'green' | 'red'
}

export function SignalIndicator({ status }: SignalIndicatorProps) {
  return (
    <img
      src={status === 'green' ? '/images/green.gif' : '/images/red.gif'}
      alt={`Signal ${status}`}
      width={20}
      height={20}
    />
  )
}
```

- [ ] **复制文件**：将旧系统的 `green.gif` 和 `red.gif` 复制到 `qcvmt-frontend/public/images/`
- [ ] **验收标准**：`status='green'` 显示绿灯；`status='red'` 显示红灯

---

### 任务 4.7 BayPlanGrid 网格组件（核心，高风险）

- [ ] **新增文件**：`qcvmt-frontend/src/components/bay/BayPlanGrid.tsx`

**网格布局逻辑**（迁移自旧 `buildBay()` HTML table 结构）：

```
┌─────────────────────────────────────────────────┐
│  Bay 名称标题                                     │
├──────┬──────┬──────┬──────┬──────┬──────┬───── ─┤
│ Tier │ Row02│ Row04│ Row06│ Row08│ Row10│       │  Hold 区
├──────┼──────┼──────┼──────┼──────┼──────┼───── ─┤  (Tiers 00-20)
│ Tier │ Row02│ Row04│ Row06│ Row08│ Row10│       │
├──────┴──────┴──────┴──────┴──────┴──────┴───── ─┤
│         甲板（Deck）                               │
├──────┬──────┬──────┬──────┬──────┬──────┬───── ─┤  Deck 区
│ Tier │ Row02│ Row04│ Row06│ Row08│ Row10│       │  (Tiers 78-99)
└──────┴──────┴──────┴──────┴──────┴──────┴───── ─┘
```

- Tier label 作为行标题（从 `workQueue.sequences` 和 `Vessel` 配置的 tierStart/tierEnd 生成）
- Row label 作为列标题（从 `rowStart` 到 `rowEnd`，步长 2）
- 每个单元格 = `BayCell`，由 `SequenceVO` 映射到 row+tier 位置

```tsx
import { BayCell } from './BayCell'
import type { WorkQueueResult, TerminalView } from '@/types/terminal'
import type { Vessel } from '@/types/vessel'

interface BayPlanGridProps {
  data: TerminalView
  colorMap: Record<string, string>  // ColSet.boxcase → color hex
}

export function BayPlanGrid({ data, colorMap }: BayPlanGridProps) {
  const { workQueue, vessels } = data
  const vessel = vessels[0] ?? null
  if (!vessel) return null

  const rows: number[] = []
  for (let r = Number(vessel.rowStart); r <= Number(vessel.rowEnd); r += 2) rows.push(r)

  const holdTiers: number[] = []
  const deckTiers: number[] = []
  // Hold tiers: 00,02,...20; Deck tiers: 78,80,... (from vessel config)
  // ... build grid
  // For each cell position: find matching SequenceVO by (row, tier)
  // Map to CellType based on qtype and slot occupancy

  return (
    <table>
      <thead>
        <tr>
          <th>Tier</th>
          {rows.map((r) => <th key={r}>{r}</th>)}
        </tr>
      </thead>
      <tbody>
        {holdTiers.map((tier) => (
          <tr key={tier}>
            <td>{tier}</td>
            {rows.map((row) => {
              const cell = getCellAt(workQueue.sequences, row, tier)
              return (
                <BayCell
                  key={`${row}-${tier}`}
                  type={cell?.cellType ?? 'empty'}
                  label={cell?.plannedPosSlot ?? ''}
                  isDg={cell?.isDg === '1'}
                  bgColor={cell ? colorMap[cell.cellType] : undefined}
                />
              )
            })}
          </tr>
        ))}
        {/* separator */}
        {deckTiers.map(/* similar */)}
      </tbody>
    </table>
  )
}
```

- [ ] **新增文件**：`qcvmt-frontend/src/components/bay/__tests__/BayPlanGrid.test.ts`
  - 测试：给定完整 `TerminalView` → 渲染正确数量的单元格
  - 测试：空 workQueue → 不渲染 Bay 表格
  - 测试：20ft 箱逻辑正确触发

- [ ] **测试命令**：`npx vitest run src/components/bay/`
- [ ] **验收标准**：Bay Plan 视觉效果与旧系统截图对比无差异；渲染时间 < 200ms

---

### 任务 4.8 TerminalPage 页面容器

- [ ] **新增文件**：`qcvmt-frontend/src/pages/terminal/TerminalPage.tsx`

**页面结构**（迁移自 `tqcvmt.jsp` 头部信息区）：

```
┌───────────────────────────────────────────────────────────┐
│  MODERN TERMINALS  QC No: [QC01]  Bay: [01/03]  活动: DISCH │
│  Signal: [🟢]     剩余: 150   船名: VESSEL_A   时间: 2026… │
├───────────────────────────────────────────────────────────┤
│  [BayPlanGrid 全屏渲染]                                     │
└───────────────────────────────────────────────────────────┘
```

- 从 URL query 参数获取 `qcNum`（如 `/terminal?qcNum=QC01`）
- 使用 `usePolling` 启动自适应轮询
- 使用 `useServerClock` 显示服务器时间
- 骨架屏：首次加载时显示 `Skeleton`
- 错误时：显示 `Result` 组件 + 重试按钮

```tsx
import { useEffect } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { Skeleton, Result, Button } from 'antd'
import { useTerminalStore } from '@/stores/terminal'
import { usePolling } from '@/hooks/usePolling'
import { useServerClock } from '@/hooks/useServerClock'
import { BayPlanGrid } from '@/components/bay/BayPlanGrid'
import { SignalIndicator } from '@/components/bay/SignalIndicator'

export default function TerminalPage() {
  const [params] = useSearchParams()
  const qcNum = params.get('qcNum') ?? ''
  const navigate = useNavigate()
  const { data, signalStatus, isLoading, error, fetchTerminalData } = useTerminalStore()

  const { start, stop } = usePolling(async () => {
    await fetchTerminalData(qcNum)
  }, { mode: 'adaptive', initialInterval: 15000 })

  const displayTime = useServerClock(data?.dateTimeNow ?? null)

  useEffect(() => {
    if (qcNum) start()
    return stop
  }, [qcNum])

  if (!qcNum) {
    return <Result status="warning" title="Missing QC Number" />
  }

  if (isLoading && !data) return <Skeleton active />

  if (error && !data) {
    return (
      <Result
        status="error"
        title="Failed to load terminal data"
        extra={<Button onClick={() => fetchTerminalData(qcNum)}>Retry</Button>}
      />
    )
  }

  if (!data) return null

  const colorMap: Record<string, string> = {}
  data.colorSets.forEach((cs) => { colorMap[cs.boxcase] = cs.color })

  return (
    <div style={{ background: '#1a1a1a', minHeight: '100vh', color: '#fff' }}>
      {/* Header */}
      <div style={{ display: 'flex', gap: 16, padding: '8px 16px' }}>
        <span>QC No: {qcNum}</span>
        <span>Bay: {data.bay}</span>
        <span>Activity: {data.qType}</span>
        <SignalIndicator status={signalStatus} />
        <span>Remain: {data.remainContainers}</span>
        <span>Vessel: {data.vesselId}</span>
        <span>Time: {displayTime}</span>
      </div>
      {/* Bay Plan */}
      <BayPlanGrid data={data} colorMap={colorMap} />
    </div>
  )
}
```

- [ ] **验收标准**：
  - 访问 `/terminal?qcNum=QC01` 触发轮询
  - Bay Plan 正确渲染
  - 超时后信号指示变红，恢复后变绿
  - 轮询间隔自适应（15s → 20s → 25s → 30s → 成功后回 15s）
  - `loadTimeCount`（LOAD 完成后继续显示 N 个周期）由前端 hook 控制

---

### 任务 4.9 DashboardPage（管理后台首页）

- [ ] **新增文件**：`qcvmt-frontend/src/pages/admin/DashboardPage.tsx`
  - 显示欢迎信息
  - 快速导航卡片（按权限展示：用户管理、船舶管理等）
  - 使用 `useAuthStore.isAdmin` 控制管理功能可见性

- [ ] **验收标准**：admin 用户看到完整导航；受限账户仅看到允许模块

---

## Phase 5 — 管理后台子页面（5A - 5E）

> 每个模块均为标准 CRUD 模式：List（Table + Pagination）+ Form（React Hook Form + Zod）+ Delete Confirm

---

### 任务 5A — 用户管理（UserList / UserForm / UserLogs）

#### 5A.1 UserList

- [ ] **新增文件**：`qcvmt-frontend/src/pages/admin/UserList.tsx`
  - Ant Design `Table`，列：QCID、Username、Role、Parent、CreateTime、操作
  - 操作按钮：编辑（跳转 `/admin/users/:id/edit`）、查看日志（`/admin/users/:id/logs`）、删除
  - 顶部"创建用户"按钮（跳转 `/admin/users/new`）
  - 分页：使用 `Pagination`，页码参数 `page/size` 传入 `userApi.list()`
  - 删除：弹出 `ConfirmDialog`，调用 `userApi.remove(id)`，成功后刷新列表

- [ ] **验收标准**：列表分页正常；CRUD 操作全部成功

#### 5A.2 UserForm（创建/编辑复用）

- [ ] **新增文件**：`qcvmt-frontend/src/pages/admin/UserForm.tsx`
  - 编辑模式从 URL 参数 `id` 判断，调用 `userApi.list` 加载数据回填表单
  - 表单字段：QCID、Username、Role（Select）、Parent
  - 提交：新建 → `userApi.create()`；编辑 → `userApi.update()`
  - 验证：使用 `userSchema`（Zod）

- [ ] **验收标准**：新建、编辑、验证全部通过

#### 5A.3 UserLogs

- [ ] **新增文件**：`qcvmt-frontend/src/pages/admin/UserLogs.tsx`
  - 展示用户操作日志（`ShowLog` 列表）
  - 调用 `userApi.logs(userId)`
  - Table 列：登录时间、操作类型、QCID

- [ ] **验收标准**：日志列表正确加载，分页正常

---

### 任务 5B — 船舶管理（VesselList / VesselForm）

#### 5B.1 VesselList

- [ ] **新增文件**：`qcvmt-frontend/src/pages/vessel/VesselList.tsx`
  - Table 列：Vessel Id、Deck/Hold、Bay、Row Range、Tier Range
  - 顶部搜索（关键词过滤 Vessel Id）
  - 删除确认

#### 5B.2 VesselForm

- [ ] **新增文件**：`qcvmt-frontend/src/pages/vessel/VesselForm.tsx`
  - 表单字段：Vessel Id（readonly 编辑模式）、Deck/Hold（Select）、Bay、RowStart/RowEnd、TierStart/TierEnd
  - 验证：`vesselSchema` + `tierParityRefine`（奇偶校验）
- [ ] **验收标准**：tierStart/tierEnd 联动正确；新建/编辑正常

---

### 任务 5C — 颜色设置（ColorSetList / ColorSetForm）

- [ ] **新增文件**：`qcvmt-frontend/src/pages/color/ColorSetList.tsx`
  - Table 列：颜色标识（boxcase text）、颜色预览（色块）、操作
  - 注意：`boxcase` 是固定枚举（inactive/unable/empty/discharge/load/complexunit/twenty/refuel），不可新增

- [ ] **新增文件**：`qcvmt-frontend/src/pages/color/ColorSetForm.tsx`
  - Ant Design `ColorPicker` 组件替代旧的 `jquery.soColorPicker`
  - 显示颜色 HEX 值 + 实时预览
  - 验证：`colorSetSchema`
- [ ] **验收标准**：颜色选择器正常工作；颜色值保存为 HEX 格式

---

### 任务 5D — 贝位颜色（VesselColorList / VesselColorForm）

- [ ] **新增文件**：`qcvmt-frontend/src/pages/vesselColor/VesselColorList.tsx`
  - Table 列：Vessel Id、Deck/Hold、Bay、Row Range、Tier Range

- [ ] **新增文件**：`qcvmt-frontend/src/pages/vesselColor/VesselColorForm.tsx`
  - 关键验证：`rowStart` 和 `rowEnd` 必须同奇偶（奇偶校验，从 JSP 内联 JS 迁移）
  - 使用 `vesselColorSchema`（Zod）
  - 表单：Vessel Id、Deck/Hold、Bay、Row Start/End、Tier Start/End
- [ ] **验收标准**：奇数+偶数 row 提交时报验证错误；同奇偶通过

---

### 任务 5E — 加油管理（VesselRefuelList / VesselRefuelForm）

- [ ] **新增文件**：`qcvmt-frontend/src/pages/vesselRefuel/VesselRefuelList.tsx`
  - Table 列：Vessel Id、Is Refuel（是/否）、操作
  - 受限账户可见此页面

- [ ] **新增文件**：`qcvmt-frontend/src/pages/vesselRefuel/VesselRefuelForm.tsx`
  - 表单：Vessel Id（Select 从 `vesselApi.list` 获取）、Is Refuel（Switch）
- [ ] **验收标准**：加油状态更新成功；受限账户可见本页面

---

### 任务 5F — Bay 尺寸配置（BaySizeForm）

- [ ] **新增文件**：`qcvmt-frontend/src/pages/bayConfig/BaySizeForm.tsx`
  - 表单展示矩阵配置（`T_CELLMATRIX` 对应）
  - 加载 `GET /api/bay-config` 数据
  - 更新 `PUT /api/bay-config`
  - 使用 Ant Design `Form.List` 支持动态字段
- [ ] **验收标准**：加载并保存 Bay 尺寸配置，数据正确

---

### 任务 5G — 导入/导出页面

#### 5G.1 ImportPage

- [ ] **新增文件**：`qcvmt-frontend/src/pages/importExport/ImportPage.tsx`
  - Ant Design `Upload` 组件，支持 CSV/Excel 文件
  - 上传 → `importExportApi.importVessel(file)`（`multipart/form-data`）
  - 进度条 + 成功/失败结果展示
- [ ] **验收标准**：文件上传后显示成功/失败结果

#### 5G.2 ExportPage

- [ ] **新增文件**：`qcvmt-frontend/src/pages/importExport/ExportPage.tsx`
  - Ant Design `DatePicker.RangePicker` 选择日期范围
  - 点击导出 → 触发 `importExportApi.exportLogs(from, to)` → 文件下载
  - 使用 `Blob` + `URL.createObjectURL()` 实现浏览器下载
- [ ] **验收标准**：选择日期后点击下载，浏览器成功下载 Excel/CSV 文件

---

### 任务 5.7 管理页面表单验证统一测试

- [ ] **测试命令**：`npx vitest run`
- [ ] **预期结果**：所有 5A-5G 页面的表单验证测试 pass
- [ ] **验收标准**：每个模块至少有表单验证单元测试

---

## Phase 6 — 旧代码清理

### 任务 6.1 功能对比检查清单

- [ ] **操作**：
  1. 新旧系统并行运行
  2. 逐一检查 21 个旧 JSP 页面在新系统中的对应功能
  3. 对照 `analysis.md` Section 4.3 10 条业务链路逐一验证

| 旧 JSP | 新组件 | 状态 |
|--------|--------|------|
| `tqcvmt.jsp` | `TerminalPage` + `BayPlanGrid` | □ |
| `admin.jsp` | `DashboardPage` | □ |
| `userDetail.jsp` + `update.jsp` | `UserForm` | □ |
| `log.jsp` | `UserLogs` | □ |
| `vesselManage.jsp` + `vesselDetail.jsp` + `updateVessel.jsp` | `VesselList` + `VesselForm` | □ |
| `colorManage.jsp` + `colSetDetail.jsp` + `updateColSet.jsp` | `ColorSetList` + `ColorSetForm` | □ |
| `vesselColorManage.jsp` + `vesselColorDetail.jsp` | `VesselColorList` + `VesselColorForm` | □ |
| `vesselRefuelManage.jsp` + `vesselRefuelDetail.jsp` | `VesselRefuelList` + `VesselRefuelForm` | □ |
| `setbaysize.jsp` | `BaySizeForm` | □ |
| `importPage.jsp` | `ImportPage` | □ |
| `exportPage.jsp` | `ExportPage` | □ |

- [ ] **验收标准**：所有 21 个页面功能对比通过，无遗漏

---

### 任务 6.2 后端 webapp 目录清理

- [ ] **操作路径**（后端项目）：
  - 删除：`src/main/webapp/`（整个目录含 21 个 JSP、vmt.js、box.css 等）
  - 删除：`src/main/webapp/WEB-INF/web.xml`
  - 删除：`src/main/webapp/WEB-INF/springMVC-servlet.xml`
  - 删除：旧 jQuery 文件：`jquery-1.11.1.min.js`、`jquery.bgiframe-2.1.2.js`、`jquery.soColorPicker-1.0.js`
  - 删除：`src/main/resources/system.properties`（已迁移至 `application.yml`）
  - 删除：IE 兼容代码（`expression()` 等，在已删除的 JSP 中）
  - 删除：`InternalResourceViewResolver` 配置（Spring Boot 不再需要）

- [ ] **编译验证**：`./gradlew build` 无错误（后端不再依赖 JSP 视图解析器）
- [ ] **验收标准**：
  - `src/main/webapp/` 目录完全移除
  - 后端 `pom.xml` / `build.gradle` 不再引用 JSP 相关依赖
  - 后端 `./gradlew build` 成功
  - `TC8` 通过：旧 webapp 目录已清理

---

## Phase 7 — 构建部署配置

### 任务 7.1 Docker 多阶段构建

- [ ] **新增文件**：`qcvmt-frontend/Dockerfile`

```dockerfile
# Build stage
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

---

### 任务 7.2 Nginx 配置

- [ ] **新增文件**：`qcvmt-frontend/nginx.conf`

```nginx
server {
    listen 80;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;

    # SPA History 模式 fallback
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API 代理到后端
    location /api/ {
        proxy_pass http://qcvmt-api:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_connect_timeout 30s;
        proxy_read_timeout 30s;
    }

    # 静态资源长缓存
    location ~* \.(js|css|png|jpg|gif|svg|woff2?)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

- [ ] **验收标准**：
  - `docker build -t qcvmt-frontend .` 构建成功
  - Nginx 正确代理 `/api/*` 到后端
  - SPA History 模式：直接访问子路由不 404

---

### 任务 7.3 CI/CD Pipeline（GitHub Actions 示例）

- [ ] **新增文件**：`qcvmt-frontend/.github/workflows/ci.yml`

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test-and-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci
      - run: npm run lint
      - run: npm run test:ci
      - run: npm run build
      - run: |
          BUNDLE_SIZE=$(du -sb dist | cut -f1)
          echo "Bundle size: $BUNDLE_SIZE bytes"
          # gzip 大小 < 300KB (307200 bytes)

  docker:
    runs-on: ubuntu-latest
    needs: test-and-build
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t qcvmt-frontend:${{ github.sha }} .
      - run: echo "Docker image built"
```

- [ ] **验收标准**：CI Pipeline 运行 lint + test + build 全部通过；Docker 镜像构建成功

---

## 整体验收汇总

### Definition of Done 检查清单

- [ ] **AC1**：21 个旧 JSP 页面在新系统中有对应功能 ✅
- [ ] **AC2**：23 个 REST API 端点全部对接成功 ✅
- [ ] **AC3**：Keycloak OIDC 登录/登出/Token 刷新正常 ✅
- [ ] **AC4**：Bay Plan 渲染与旧系统视觉效果一致（截图对比）✅
- [ ] **AC5**：自适应轮询 3 种模式全部正常（15s → 20s → 25s → 30s）✅
- [ ] **AC6**：3 种语言切换正常（EN / 繁体中文 / 简体中文）✅
- [ ] **AC7**：管理后台所有 CRUD 操作正常 ✅
- [ ] **AC8**：导入/导出功能正常（文件上传 + 日志下载）✅
- [ ] **AC9**：权限控制（admin / user / 受限账户）正确 ✅
- [ ] **TC1**：TypeScript 无 `any` 类型（`tsc --noEmit` 通过）✅
- [ ] **TC2**：单元测试覆盖 hooks 和核心组件（`vitest`）✅
- [ ] **TC3**：首次加载 FCP < 2s（路由懒加载 `React.lazy`）✅
- [ ] **TC4**：Bay Plan 渲染 < 200ms（`React.memo` 优化）✅
- [ ] **TC5**：Bundle 大小 < 300KB gzip ✅
- [ ] **TC6**：`npm run build` 无错误无警告 ✅
- [ ] **TC7**：Docker 镜像构建成功 ✅
- [ ] **TC8**：旧 `webapp/` 目录已清理 ✅

---

## 依赖关系与执行顺序

```
Phase 1（基础骨架）
  └── Phase 2（API 层）→ 需后端 REST API 就绪
        └── Phase 3（认证/路由/i18n）→ 需 Keycloak realm 配置完成
              └── Phase 4（核心业务）→ 高风险，需 N4 测试环境联调
                    └── Phase 5（管理页面）
                          └── Phase 6（旧代码清理）→ 需全部功能验证通过
                                └── Phase 7（部署配置）
```

| 阶段 | 阻塞依赖 |
|------|---------|
| Phase 2 | 后端 Spring Boot 3 REST API 已就绪 |
| Phase 3 | Keycloak `qcvmt` realm 及 `qcvmt-frontend` client 配置完成 |
| Phase 4 | N4 测试环境可用（用于联调轮询数据） |
| Phase 6 | Phase 1-5 全部功能验收通过 |

---

## 风险缓解补充

| 风险 | 缓解措施 |
|------|---------|
| Bay Plan 漏边界用例 | 开发阶段与旧系统并行运行，截图逐 Bay 对比 |
| 轮询逻辑行为不一致 | `usePolling.test.ts` 覆盖 3 种模式所有场景 |
| Keycloak realm 不匹配 | 开发用独立 realm，联调前与运维对齐 client/role 配置 |
| 受限账户权限 | 单元测试覆盖非 admin 用户路由守卫 |

---

## 补全

> **追加日期**：2026-08-10
> **来源**：design.md / S00601 核对后，tasks.md 中 design scope 内未覆盖项

### Task 8.1: 路由懒加载 + React ErrorBoundary 全局错误捕获

- [ ] **目标**：满足 TC3（FCP < 2s）的实现手段——路由级代码分割；满足 S00601 监控要求——Phase 1 实现 `ErrorBoundary` + `window.onerror` 基础错误捕获，为后续接入 Sentry 打基础。

- [ ] **文件:**
  - Modify: `qcvmt-frontend/src/router/index.tsx`（将各 page import 改为 `React.lazy(() => import(...))`，外层包裹 `<Suspense fallback={<Spin fullscreen />}>`）
  - Create: `qcvmt-frontend/src/components/common/ErrorBoundary.tsx`
  - Modify: `qcvmt-frontend/src/App.tsx`（在根组件外层包裹 `<ErrorBoundary>`）
  - Modify: `qcvmt-frontend/src/main.tsx`（添加 `window.onerror` 和 `window.addEventListener('unhandledrejection', ...)` 全局监听，`console.error` 输出）
  - Test: `qcvmt-frontend/src/components/common/__tests__/ErrorBoundary.test.ts`

- [ ] **涉及的类/方法/接口：**
  - `React.lazy`、`React.Suspense`（React 内置）
  - `class ErrorBoundary extends React.Component`（React 官方错误边界 API）
  - `window.onerror`、`window.onunhandledrejection`

- [ ] **分步实施要求：**
  1. 在 `router/index.tsx` 中，将所有 `import XxxPage from '@/pages/...'` 改为 `const XxxPage = React.lazy(() => import('@/pages/...'))`
  2. 在路由 `<RouterProvider>` 外层包裹 `<Suspense fallback={<Spin size="large" fullscreen />}>`
  3. 创建 `ErrorBoundary.tsx`，实现 `componentDidCatch(error, errorInfo)` → `console.error('Uncaught error:', error, errorInfo)`，渲染 fallback UI（Ant Design `Result` 组件 + 重试按钮）
  4. 在 `App.tsx` 根组件最外层包裹 `<ErrorBoundary>`
  5. 在 `main.tsx` 入口文件添加：
     ```ts
     window.onerror = (msg, src, line, col, error) => {
       console.error('[Global Error]', msg, src, line, col, error)
     }
     window.addEventListener('unhandledrejection', (event) => {
       console.error('[Unhandled Rejection]', event.reason)
     })
     ```

- [ ] **测试命令及预期结果：**
  - `npx vitest run src/components/common/__tests__/ErrorBoundary.test.ts`：模拟子组件 throw → ErrorBoundary 渲染 fallback UI，console.error 被调用
  - `npm run build`：构建产物拆分为多个 chunk（每个路由一个），主 chunk gzip < 100KB

- [ ] **验收标准：**
  - TC3 满足：首次加载只下载主 chunk + 当前路由 chunk，FCP < 2s
  - 子组件运行时错误 → ErrorBoundary 捕获并显示友好 fallback，不白屏
  - 未捕获的 Promise rejection → console.error 输出，不影响应用稳定性

- [ ] **依赖和兼容性注意事项：**
  - React.lazy 要求组件必须 `export default`；当前 tasks.md 中所有 page 组件均使用 `export default function XxxPage()`，兼容
  - ErrorBoundary 仅捕获 render 阶段和生命周期错误，异步错误（如 Promise rejection）需 `window.onerror` 补充
  - `Spin` 组件需从 `antd` 导入，已在任务 1.4 安装 antd，无需新增依赖

---

### Task 8.2: 管理列表页 Spin 加载态 + Empty 空态统一规范

- [ ] **目标**：满足 S00601 明确要求的「列表页使用 Ant Design `Spin` 加载态和 `Empty` 空态」，确保所有 5A–5G 列表页视觉体验一致。

- [ ] **文件:**
  - Modify: `qcvmt-frontend/src/pages/admin/UserList.tsx`（在 Table 外层条件渲染：`isLoading ? <Spin /> : data.length === 0 ? <Empty /> : <Table />`）
  - Modify: `qcvmt-frontend/src/pages/vessel/VesselList.tsx`（同上）
  - Modify: `qcvmt-frontend/src/pages/color/ColorSetList.tsx`（同上）
  - Modify: `qcvmt-frontend/src/pages/vesselColor/VesselColorList.tsx`（同上）
  - Modify: `qcvmt-frontend/src/pages/vesselRefuel/VesselRefuelList.tsx`（同上）

- [ ] **涉及的类/方法/接口：**
  - `Spin`、`Empty`（均来自 `antd`，已安装）

- [ ] **分步实施要求：**
  在每个列表组件中，将 `useEffect` 中调用 API 时的状态管理统一为：
  ```tsx
  const [isLoading, setIsLoading] = useState(true)
  const [data, setData] = useState([])

  // fetch data...

  if (isLoading) return <Spin size="large" style={{ display: 'flex', justifyContent: 'center', marginTop: 100 }} />
  if (data.length === 0) return <Empty description="暂无数据" />
  return <Table dataSource={data} ... />
  ```

- [ ] **测试命令及预期结果：**
  - `npx vitest run`：现有列表页测试用例中，mock API 返回空数组 → 渲染 `Empty`；mock 延迟 → 渲染 `Spin`

- [ ] **验收标准：**
  - 所有 5 个列表页（UserList / VesselList / ColorSetList / VesselColorList / VesselRefuelList）在加载中显示 Spin、数据为空时显示 Empty

- [ ] **依赖和兼容性注意事项：**
  - 不新增依赖，`Spin` 和 `Empty` 来自 antd（已在任务 1.4 安装）
  - 此任务为对现有 Phase 5A–5G 任务描述的增补规范，不改变文件结构和 API 接口
