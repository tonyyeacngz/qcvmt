# 现状分析与影响评估

> **生成日期**：2026-08-10  
> **变更标识**：spec-20260810112114  
> **范围**：QCVMT 前端从 JSP + jQuery 服务端渲染迁移至 React 18 SPA + REST JSON API

---

## 1. 当前实现状态

### 1.1 技术栈现状

| 维度 | 当前技术选型 | 待迁移目标 |
|------|-------------|-----------|
| 后端框架 | Spring MVC 3.0.1 + Hibernate 3.2.6 | Spring Boot 3（已完成设计，参见执行计划） |
| 语言版本 | Java 7 | Java 17 |
| 构建工具 | Maven WAR 包 | Gradle（后端）+ Vite 5（前端） |
| 前端框架 | JSP + JSTL 1.2 + jQuery 1.11.1 | React 18 + TypeScript 5 |
| 数据库 | Oracle 10g/11g（C3P0 连接池） | MySQL（本地）+ Oracle（N4 只读） |
| 认证方式 | HTTP Session + `SecurityInterceptor` | Keycloak OIDC + JWT |
| 国际化 | Spring `ResourceBundleMessageSource`（3 种语言） | `react-i18next` |
| 数据交换格式 | 自定义 XML（非标准） | REST JSON API |

### 1.2 核心模块清单

#### 1.2.1 岸桥作业监控（核心域）

| 文件路径 | 关键符号 | 职责 |
|---------|---------|------|
| `src/main/java/com/springMVC/control/CellControl.java` | `CellControl` | Spring MVC 控制器，路由 `/user/BusiQuery`，协调 DAO 调用 |
| `src/main/java/com/accenture/vmt/Busihandler.java` | `Busihandler.returnResponse()` | 核心业务入口：获取作业队列 → 构建 HTML 表格 → 写入 XML 响应 |
| `src/main/java/com/springMVC/dao/CellDaoImpl.java` | `CellDaoImpl`（1884 行） | 数据访问层：查询 N4、构建舱位矩阵、计算单元格信息 |
| `src/main/java/com/springMVC/entity/SequenceVO.java` | `SequenceVO` | 作业序列值对象：`current_pos_slot`, `planned_pos_slot`, `qtype`, `is_dg`, `complexunit` 等 |

#### 1.2.2 用户认证与管理（支撑域）

| 文件路径 | 关键符号 | 职责 |
|---------|---------|------|
| `src/main/java/com/springMVC/control/UserControl.java` | `UserControl`（550 行） | 用户 CRUD、登录/登出、日志导出、船舶导入 |
| `src/main/java/com/springMVC/dao/UserDaoImpl.java` | `UserDaoImpl` | 用户数据访问、登录验证、日志记录 |
| `src/main/java/com/springMVC/filter/SecurityInterceptor.java` | `SecurityInterceptor` | Session 认证拦截器，检查 `Constants.USER_LOGIN` |
| `src/main/java/com/springMVC/entity/User.java` | `User` | 用户实体：`userid`, `QCID`, `NAME`, `PASSWORD`, `ROLE`, `PARENT` |

#### 1.2.3 实体与配置（共享域）

| 实体 | 表名 | 关键字段 |
|------|------|---------|
| `Vessel` | `T_Vessel` | `vmid`, `vesselid`, `deck_hold`, `bay`, `rowstart/rowend`, `tierstart/tierend` |
| `VesselCol` | `T_VESSELCOL` | `vcid`, `vesselid`, `deck_hold`, `bay`, `rowstart/rowend`, `tierstart/tierend` |
| `VesselRefuel` | `T_VESSELREFUEL` | `vrid`, `vesselid`, `is_refuel` |
| `ColSet` | `T_COLSET` | `colsetid`, `COLOR`, `BOXCASE` |
| `CellMatrix` | `T_CELLMATRIX` | `matrixid`, `cmtype`, `cmrow`, `cmtier`, `active` |
| `BaySize` | 配置对象 | `holdTiers` |
| `ShowLog` | `T_SHOWLOG` | `userlogid`, `USERID`, `USERNAME`, `QCID`, `LOGINTIME`, `OPERATION` |
| `OperationLog` | `T_OPERATIONLOG` | `OPERLOGID`, `USERNAME`, `FUNCTION`, `ACTIONTYPE`, `VALUECHANGE`, `TIME` |

### 1.3 前端执行流程（tqcvmt.jsp + vmt.js）

```
浏览器加载 tqcvmt.jsp
    ↓
vmt.js 初始化全局变量（refreshMode=3, thisInterval=15000ms）
    ↓
getData() 发起 AJAX GET /user/BusiQuery.html?qcNum=xxx
    ↓
CellControl.busiQuery() → Busihandler.returnResponse()
    ↓
CellDaoImpl.getCells()：
  ├── getQorder() → 查询 N4 inv_wq/inv_wi 获取作业顺序
  ├── checkSequenceList() → 校验 Bay 数量 ≤ 2
  ├── getSequenceList() → 获取活跃作业项
  ├── getROBList() → 获取剩余在船集装箱
  ├── getCellMatrixFromnN4() → 获取船舶舱位矩阵
  └── buildBay() → 生成 HTML 表格字符串
    ↓
Busihandler 组装 XML 响应（<dateTimeNow>, <bayNm>, <table_info> 等）
    ↓
vmt.js callBack()：
  ├── 检测 Session 过期（响应含 login 页面）
  ├── 字符串截取解析 XML（getBaseContent, getListContent, getTimeContent）
  ├── 更新 DOM 头部信息（bayNm, QCAct, rmain, reful, Vessl）
  ├── innerHTML 注入 HTML 表格到 #tableList
  ├── 更新信号指示灯（green.gif / red.gif）
  └── 时间同步（setTime + showTime）
    ↓
自适应退避：成功 → 恢复 15s；连续超时 → 递增至 20s/25s/30s
    ↓
setTimeout(getData, thisInterval) 继续轮询
```

---

## 2. 需求理解

### 2.1 改造目标

| 目标 | 描述 |
|------|------|
| **前后端分离** | 前端独立构建、部署为 React SPA，后端提供 REST JSON API |
| **认证升级** | Session 认证替换为 Keycloak OIDC，前端使用 `keycloak-js` |
| **数据格式标准化** | 废弃自定义 XML 响应，全面使用 JSON API |
| **核心逻辑迁移** | 自适应轮询 → `usePolling` hook；时间同步 → `useServerClock` hook |
| **Bay Plan 数据驱动渲染** | 后端仅返回结构化 JSON，前端 React 组件自行渲染网格 |
| **类型安全** | TypeScript 全覆盖，表单验证使用 Zod schema |
| **多语言支持** | `react-i18next` 迁移 `messages_*.properties` → JSON |

### 2.2 业务规则与约束

| 规则 | 来源 | 约束条件 |
|------|------|---------|
| Bay Plan 渲染 CSS 类规则 | `tqcvmt.jsp` 内联 CSS | 8 种类型：`inactive`, `unable`, `empty`, `discharge`, `load`, `complexunit`, `twenty`, `refuel` |
| 自适应轮询三模式 | `vmt.js` L60-173 | Mode 1/2/3，连续超时 → 间隔递增（15s→20s→25s→30s） |
| 20ft 箱检测 | `CellDaoImpl.getCells()` | 仅在 DISCH 模式、单 Bay、偶数 Bay 时触发 |
| 奇偶校验 | 各 JSP 内联 JS | `rowStart` 和 `rowEnd` 必须同奇偶 |
| 权限矩阵 | `SecurityInterceptor` + `system.properties` | admin / user / 受限账户（`limitAccount`） |
| Tier 编号计算 | `CellDaoImpl.getTier()` | Hold: 00/02/04/06/08/10...; Deck: 78/80/82... |
| DG 标识 | `CellDaoImpl`（当前被注释禁用） | 危险品集装箱黄色/红色标记 |

### 2.3 待解决问题

| 编号 | 问题 | 影响 | 建议 |
|------|------|------|------|
| OQ1 | 旧系统键盘快捷键（Numpad +/- 切换焦点、* 登出）是否保留 | TerminalPage | Phase 5 后根据用户反馈决定 |
| OQ2 | `limitAccount` 受限账户逻辑迁至 Keycloak role 还是后端配置 | 权限控制 | 建议迁移为 Keycloak 自定义属性 |
| OQ3 | Cookie 持久化 QC/HC/C 号在 Keycloak 登录后是否还需要 | 登录流程 | Keycloak 登录后通过 API 获取，不再需要 |
| OQ4 | Bay Plan 是否需要支持缩放/响应式 | TerminalPage | 建议保持固定尺寸（工控屏分辨率固定） |
| OQ5 | `loadTimeCount`（LOAD 完成后继续显示 N 周期）在前端还是后端实现 | 轮询逻辑 | 建议前端实现 |

---

## 3. 影响范围

### 3.1 直接影响

| 模块 | 文件/目录 | 变更类型 | 说明 |
|------|----------|---------|------|
| 全部 JSP 页面（21 个） | `src/main/webapp/WEB-INF/jsp/*.jsp` | **删除** | Phase 6 清理旧 webapp 目录 |
| 前端 JS | `src/main/webapp/js/vmt.js` | **删除**（逻辑迁移至 React hooks） | 自适应轮询、时间同步、XML 解析 |
| CSS 文件 | `box.css`, `colorPickerStyle.css` | **删除**（迁移至 CSS Modules） | |
| jQuery/IE 兼容库 | `jquery-1.11.1.min.js`, `jquery.bgiframe-2.1.2.js`, `jquery.soColorPicker-1.0.js` | **删除** | IE5/6 兼容代码全部移除 |
| Spring MVC 配置 | `springMVC-servlet.xml`, `web.xml` | **删除** | Spring Boot 内嵌 Tomcat 替代 |
| i18n 资源 | `messages_en/zh_CN/zh_TW.properties` | **迁移** → `src/locales/*.json` | 格式转换 |

### 3.2 间接影响

| 维度 | 影响说明 |
|------|---------|
| 后端 Controller | `CellControl`, `UserControl` 需配合后端改造为 REST Controller（后端设计已覆盖） |
| 后端 DAO 层 | `CellDaoImpl`（1884 行）中大量业务逻辑（`buildBay`, `getCellInfo`, `getTier`）需拆分：数据查询留后端，HTML 生成逻辑迁至前端 |
| N4 集成 | `CellDaoImpl` 中 N4 SQL 查询迁至独立 `N4WorkQueueService`/`N4ContainerQueryService`/`N4VesselQueryService`/`N4FacilityQueryService` |
| 部署架构 | WAR 包 → Nginx（前端静态资源）+ Spring Boot JAR（后端 API），新增 Nginx 反向代理层 |
| 认证体系 | Session → Keycloak OIDC，新增 `keycloak.ts`, `AuthGuard`, JWT Token 拦截器 |

### 3.3 传递性依赖

| 依赖层 | 影响链 |
|--------|-------|
| Keycloak 服务器 | 需部署/配置 Keycloak realm、client、角色映射 |
| CI/CD Pipeline | 新增前端构建（`npm run build`）→ Docker 多阶段构建 → Nginx 镜像 |
| 运维 | Nginx 配置、SSL 证书、前端环境变量管理 |
| 用户培训 | 界面变化、登录流程变化（从 QC/HC/C 号输入 → Keycloak 统一登录） |

---

## 4. 受影响流程与路由

### 4.1 API 端点映射（旧 → 新）

| 旧 URL | 新 REST API | 方法 | 数据格式 |
|--------|------------|------|---------|
| `BusiQuery.html?qcNum=xxx` | `GET /api/terminal/query?qcNum=xxx` | GET | JSON |
| `all.html` | `GET /api/users?page=0&size=10` | GET | JSON |
| `save.html` (POST) | `POST /api/users` | POST | JSON |
| `update.html` (POST) | `PUT /api/users/{id}` | PUT | JSON |
| `del.html?id=x` | `DELETE /api/users/{id}` | DELETE | JSON |
| `log.html?id=x` | `GET /api/users/{id}/logs` | GET | JSON |
| `allVessel.html` | `GET /api/vessels` | GET | JSON |
| `saveVessel.html` | `POST /api/vessels` | POST | JSON |
| `updateVessel.html` | `PUT /api/vessels/{id}` | PUT | JSON |
| `delVessel.html?id=x` | `DELETE /api/vessels/{id}` | DELETE | JSON |
| `allColSet.html` | `GET /api/color-sets` | GET | JSON |
| `saveColSet.html` | `POST /api/color-sets` | POST | JSON |
| `updateColSet.html` | `PUT /api/color-sets/{id}` | PUT | JSON |
| `allVesselCol.html` | `GET /api/vessel-colors` | GET | JSON |
| `saveVesselCol.html` | `POST /api/vessel-colors` | POST | JSON |
| `delVesselCol.html?id=x` | `DELETE /api/vessel-colors/{id}` | DELETE | JSON |
| `allVesselRefuel.html` | `GET /api/vessel-refuels` | GET | JSON |
| `updateVesselRefuelStatus.html` | `POST /api/vessel-refuels` | POST | JSON |
| `delVesselRefuel.html?id=x` | `DELETE /api/vessel-refuels/{id}` | DELETE | JSON |
| `setbay.html` | `GET /api/bay-config` | GET | JSON |
| `updateBay.html` | `PUT /api/bay-config` | PUT | JSON |
| `importVessel.html` | `POST /api/import/vessel` | POST | multipart |
| `exportLogs.html` | `GET /api/export/logs?from=x&to=y` | GET | file download |

### 4.2 前端路由规划

| 路由 | 角色要求 | 对应旧页面 |
|------|---------|-----------|
| `/terminal` | qcvmt-admin / qcvmt-user | `tqcvmt.jsp` |
| `/admin` | qcvmt-admin | `admin.jsp` |
| `/admin/users/**` | qcvmt-admin | `userDetail.jsp`, `update.jsp`, `log.jsp` |
| `/admin/vessels/**` | qcvmt-admin | `vesselManage.jsp`, `vesselDetail.jsp`, `updateVessel.jsp` |
| `/admin/color-sets/**` | qcvmt-admin | `colorManage.jsp`, `colSetDetail.jsp`, `updateColSet.jsp` |
| `/admin/vessel-refuels/**` | qcvmt-admin / 受限账户 | `vesselRefuelManage.jsp`, `vesselRefuelDetail.jsp` |
| `/admin/vessel-colors/**` | qcvmt-admin / 受限账户 | `vesselColorManage.jsp`, `vesselColorDetail.jsp` |
| `/admin/bay-config` | qcvmt-admin | `setbaysize.jsp` |
| `/admin/import` | qcvmt-admin | `importPage.jsp` |
| `/admin/export` | qcvmt-admin | `exportPage.jsp` |
| `/login` | 公开 | `login.jsp`, `loginAdmin.jsp` |

### 4.3 10 条端到端业务链路

| 链路名称 | 影响等级 | 说明 |
|---------|---------|------|
| Vessel Terminal Operations Lifecycle | **高** | 核心 Bay Plan 渲染 + 轮询，涉及 12 个页面 |
| User Authentication and Session Management | **高** | Session → Keycloak OIDC，全部重写 |
| User Administration and Management | 中 | CRUD 页面，模式统一 |
| Vessel Configuration Management | 中 | CRUD 页面 |
| Color Set Management | 中 | CRUD 页面 + 颜色选择器替换 |
| Vessel Color and Bay/Row Configuration | 中 | CRUD 页面 + 奇偶校验逻辑迁移 |
| Vessel Refuel Configuration | 低 | CRUD 页面 |
| Container Cell and Bay Size Management | 中 | Bay 尺寸配置表单 |
| Operation Log Audit and Export | 低 | 日志查询 + Excel 导出 |
| Vessel Data Import and Export | 中 | 文件上传 + N4 验证 |

---

## 5. 风险评估

### 5.1 风险矩阵

| 编号 | 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|------|---------|
| R1 | Bay Plan 渲染逻辑复杂，后端生成 HTML 转前端数据驱动可能遗漏边界情况 | **高** | 中 | 对比旧系统截图逐一验证；保留旧系统并行运行一段时间 |
| R2 | 自适应轮询逻辑迁移后行为不一致 | 中 | 低 | 编写完整单元测试覆盖所有模式（Mode 1/2/3） |
| R3 | Keycloak 配置与后端不一致导致认证失败 | **高** | 低 | 前后端联调阶段重点验证；开发环境使用独立 realm |
| R4 | N4 Oracle 查询超时导致前端长时间等待 | 中 | 中 | Axios timeout 设置 + 轮询超时处理 + 信号指示红灯 |
| R5 | 旧系统用户习惯改变（键盘快捷键） | 低 | **高** | 新系统后期根据用户反馈追加 |
| R6 | i18n 翻译 key 迁移遗漏 | 低 | 低 | 自动化脚本对比 properties 和 json 文件的 key 完整性 |

### 5.2 高风险区域详细分析

#### R1: Bay Plan 渲染逻辑

**风险来源**：`CellDaoImpl.java`（1884 行）中 `buildBay()` 方法包含大量条件分支：
- 8 种 CSS 类判断（`inactive`, `unable`, `empty`, `discharge`, `load`, `complexunit`, `twenty`, `refuel`）
- DG 危险品标识（当前被注释但需评估是否启用）
- 20ft 箱检测（仅 DISCH + 单 Bay + 偶数 Bay）
- 连体箱（`complexunit`）跨 Bay 显示
- Tier 编号计算差异（Deck vs Hold）

**迁移策略**：后端将 `buildBay()` 逻辑拆分为结构化 JSON 数据返回，前端 `BayCell.tsx`（`React.memo`）根据 `SequenceVO` 属性自行决定样式。

#### R3: 认证体系迁移

**风险来源**：
- 旧系统使用 QC/HC/C 号 + 密码登录，新系统使用 Keycloak OIDC
- `limitAccount` 受限账户逻辑需从 `system.properties` 迁移至 Keycloak role 或自定义属性
- `SecurityInterceptor` → Spring Security JWT 验证 + 前端 `AuthGuard`

**迁移策略**：Phase 3 集中处理认证集成，前后端联调阶段重点验证 Token 刷新和权限矩阵。

---

## 6. 当前代码关键问题（待改造项）

| 编号 | 问题 | 严重度 | 当前表现 |
|------|------|--------|---------|
| P1 | 服务端渲染 HTML 表格 | **高** | `Busihandler.returnResponse()` + `buildBay()` 生成 HTML 字符串，前端 `innerHTML` 注入 |
| P2 | 自定义 XML 响应格式 | **高** | `text/xml` Content-Type，前端字符串截取解析（非 DOM parser） |
| P3 | CSS 大量重复 | 中 | `#d1` 样式在 21 个 JSP 中各写一遍 |
| P4 | IE5/IE6 兼容代码 | 低 | `expression()`, `bgiframe`, `window.event` |
| P5 | 无前端构建工具 | 中 | JS/CSS 直接引用，手动版本号 `?v=4` |
| P6 | Session 认证 | **高** | `SecurityInterceptor` + Session 存储 User，无法前后端分离 |
| P7 | 表单验证逻辑重复 | 中 | 每个 JSP 内联相似 JS 验证代码 |
| P8 | 密码明文存储 | **高** | `User` 实体 `PASSWORD` 字段明文 |
| P9 | 无 TypeScript | 中 | 运行时错误难排查 |
| P10 | 无自动化测试 | 中 | 回归风险高 |
| P11 | DG 标识 bug | 中 | `is_dg == "1"` 使用 `==` 而非 `.equals()`，且 `getHazardList()` 被注释 |

---

## 7. 结论与建议

1. **改造范围明确**：21 个 JSP 页面 → React 组件，23 个旧 API 端点 → REST JSON API，Session → Keycloak OIDC
2. **核心风险集中在 Bay Plan 渲染和认证迁移**，建议在 Phase 4 集中攻关
3. **后端改造（Spring Boot 3 + REST API）是前端改造的前置依赖**，需先完成后端 Phase 1-2
4. **建议渐进式迁移**：Phase 1（基础骨架）→ Phase 2（API 层）→ Phase 3（认证/路由/i18n）→ Phase 4（核心终端页）→ Phase 5（管理页面）→ Phase 6（清理旧代码）→ Phase 7（部署配置）
5. **旧系统建议保留并行运行**一段时间，确保功能对比验证完成后再完全下线
