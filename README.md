# AHDUNYI Terminal PRO v9.0.0

> 字节跳动风控审核中台 — 商业化全栈项目

## 技术栈

| 层级 | 技术 |
|---|---|
| 后端 | FastAPI + SQLAlchemy 2.0 + MySQL (pymysql) |
| 鉴权 | JWT (python-jose) + bcrypt (passlib) |
| 前端 | Vue 3 + TypeScript + Arco Design Vue |
| 状态管理 | Pinia |
| 打包 | Vite 5 (产物可封装为 .exe) |
| 桌面端 | PyQt6 + QWebEngineView |
| 权限 | RBAC 2.0 — 基于权限点，非角色硬编码 |

## 项目结构

```
AHDUNYI_Terminal_PRO/
├── server/                  # FastAPI 后端
│   ├── api/                 # 路由层
│   │   ├── auth.py          # 登录 / 改密
│   │   ├── permissions.py   # 权限点 / 角色列表
│   │   ├── users.py         # 用户管理
│   │   ├── tasks.py         # 任务派发 / 进度
│   │   ├── team.py          # 团队洞察
│   │   └── logs.py          # 影子审计日志
│   ├── constants/
│   │   ├── roles.py         # UserRole 枚举
│   │   └── permissions.py   # 权限矩阵（新增角色只改此处）
│   ├── core/
│   │   └── database.py      # MySQL 连接池
│   ├── db/
│   │   ├── models.py        # ORM: users / shift_tasks / action_logs
│   │   └── init_db.py       # 建表 + 种子数据
│   ├── schemas/
│   │   └── __init__.py      # 全套 Pydantic 模型
│   ├── services/
│   │   └── dispatch.py      # 最少分配优先算法
│   ├── main.py              # 应用入口 + 全局异常处理
│   ├── requirements.txt
│   ├── .env.example         # 配置模板（复制为 .env 填写密码）
│   └── Dockerfile
├── client/
│   ├── web/                 # Vue 3 前端
│   │   ├── src/
│   │   │   ├── api/         # rbac.ts (业务接口)
│   │   │   ├── stores/      # permission.ts (Pinia 权限 Store)
│   │   │   ├── router/      # 权限点驱动路由守卫
│   │   │   ├── layouts/     # MainLayout.vue
│   │   │   ├── views/
│   │   │   │   ├── LoginPage.vue
│   │   │   │   ├── DashboardPage.vue
│   │   │   │   ├── RealTimePatrolPage.vue
│   │   │   │   ├── ViolationReviewPage.vue
│   │   │   │   ├── SettingsPage.vue
│   │   │   │   ├── SOPPage.vue / SOPRulesPage.vue
│   │   │   │   ├── dashboard/
│   │   │   │   │   ├── AuditorView.vue
│   │   │   │   │   ├── ShiftLeaderView.vue
│   │   │   │   │   └── SupervisorView.vue
│   │   │   │   └── supervisor/
│   │   │   │       └── ShadowAuditDashboard.vue
│   │   │   └── utils/auth.ts
│   │   ├── vite.config.ts
│   │   └── package.json
│   ├── desktop/             # PyQt6 桌面壳
│   └── build/               # PyInstaller 打包配置
├── shared/                  # 前后端共享常量
└── .github/workflows/       # CI/CD
```

## 快速启动

### 1. 配置环境变量

```bash
cp server/.env.example server/.env
# 编辑 server/.env，填写 MySQL 密码和 JWT 密钥
```

### 2. 后端

```bash
pip install -r server/requirements.txt

# 首次：建表 + 种子数据
python server/db/init_db.py

# 启动
uvicorn server.main:app --host 0.0.0.0 --port 8000 --reload
```

API 文档：http://localhost:8000/docs

### 3. 前端

```bash
cd client/web
npm install
npm run dev      # 开发
npm run build    # 生产打包 → dist/
```

## 数据库

需在 MySQL 中提前创建数据库：

```sql
CREATE DATABASE ahdunyi_pro_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

表结构由 `python server/db/init_db.py` 自动创建，共 3 张表：

| 表名 | 用途 |
|---|---|
| `users` | 用户账户（角色、密码哈希、状态） |
| `shift_tasks` | 班次任务派发与进度记录 |
| `action_logs` | 影子审计操作行为日志 |

## 默认账号

| 用户名 | 密码 | 角色 |
|---|---|---|
| `superyu` | `melody2026` | 风控经理（全权限） |
| `leader_am` | `ahdunyi2026` | 早班组长 |
| `auditor_001` ~ `005` | `ahdunyi2026` | 审核员 |

## RBAC 权限矩阵

权限矩阵位于 `server/constants/permissions.py`。

**新增角色只需修改此一处文件，前端零改动。**

```python
# 示例：新增「合规专员」角色
ROLE_PERMISSION_MATRIX["compliance_officer"] = [
    Permission.VIEW_DASHBOARD,
    Permission.VIEW_VIOLATIONS,
]
```

## CI/CD

`.github/workflows/` 包含：
- `client-build.yml` — PR 触发前端 build 验证
- `server-deploy.yml` — push to main 自动部署后端
