# AHDUNYI Terminal PRO

Desktop audit terminal for live-stream content review. PyQt6 shell hosting a compiled Vue 3 frontend; Python FastAPI backend persists shift metrics to MySQL.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Desktop shell | Python 3.12 · PyQt6 · QWebEngineView · QWebChannel |
| Frontend | Vue 3 · TypeScript · Vite · Pinia · Arco Design |
| Backend | FastAPI · SQLAlchemy 2 · Alembic · PyMySQL |
| Database | MySQL 8 (charset utf8mb4) |
| Auth | JWT (python-jose) · bcrypt |
| CI/CD | GitHub Actions → Aliyun ECS via SSH |
| Packaging | PyInstaller (one-folder EXE) |

---

## Directory Structure

```
AHDUNYI_Terminal_PRO/
├── client/
│   ├── desktop/                  # PyQt6 application
│   │   ├── app/
│   │   │   ├── bridge/           # QWebChannel ↔ Vue bridge
│   │   │   ├── core/             # Room monitor, memory probe, behavior analyzer
│   │   │   └── ui/               # MainWindow, LoginWindow
│   │   ├── config/               # AppSettings dataclass + JSON loader
│   │   ├── utils/
│   │   └── main.py               # Entry point
│   ├── web/                      # Vue 3 frontend
│   │   └── src/
│   │       ├── api/              # rbacApi, axios HTTP layer
│   │       ├── bridge/           # qt_channel.ts (QWebChannel adapter)
│   │       ├── layouts/          # MainLayout
│   │       ├── router/           # Vue Router (hash history)
│   │       ├── stores/           # Pinia: permission, workflow, loading
│   │       └── views/            # RealTimePatrolPage, DashboardPage, ...
│   └── build/                    # PyInstaller spec + one-click build script
├── server/                       # FastAPI application
│   ├── api/                      # Routers: auth, tasks, team, users, logs, violation
│   ├── constants/                # Role definitions, permission matrix
│   ├── core/                     # SQLAlchemy engine + session factory
│   ├── db/                       # ORM models, init_db seed script
│   ├── schemas/                  # Pydantic request/response models
│   ├── services/                 # dispatch.py (least-assigned-first algorithm)
│   ├── alembic/                  # Migration history
│   ├── main.py                   # FastAPI app factory
│   ├── Dockerfile
│   └── requirements.txt
├── shared/                       # Constants and schemas shared across layers
│   ├── constants/api_paths.py
│   ├── patterns/room_id.py
│   └── schemas/
├── config.json                   # Runtime config: server URL, window size, debug flags
├── db_schema.md                  # Database schema reference
└── .github/workflows/
    ├── server-deploy.yml         # Lint → git pull → pip install → systemctl restart
    └── client-build.yml
```

---

## API Overview

### Authentication
| Method | Path | Description |
|---|---|---|
| POST | `/api/auth/login` | Username/password → 24h JWT |
| GET | `/api/auth/permissions` | Re-hydrate permission store |
| POST | `/api/auth/change-password` | Change own password |

### Tasks (`shift_tasks` table)
| Method | Path | Description |
|---|---|---|
| GET | `/api/task/my/live-patrol` | Get or auto-create today's live patrol task (idempotent, no dispatch required) |
| GET | `/api/task/my` | Today + historical tasks + weekly stats |
| PATCH | `/api/task/{id}/progress` | Persist `reviewed_count`, `violation_count`, `work_duration`, `is_completed` |
| POST | `/api/task/{id}/complete` | Mark task completed (`is_completed = 1`) |
| POST | `/api/dispatch/auto` | Least-assigned-first batch dispatch (requires `action:dispatch_task`) |

### Team & Audit
| Method | Path | Description |
|---|---|---|
| GET | `/api/team/insight` | Aggregated stats by date range, user, channel |
| GET | `/api/team/user/{id}/stats` | Per-user detailed breakdown |
| POST | `/api/log/action` | Append fine-grained action log entry |
| GET | `/api/log/list` | Paginated action log query (requires `view:shadow_audit`) |

---

## Data Persistence Model

Every live-patrol session is backed by a row in `shift_tasks`.

```
Auditor logs in
    └─→ GET /api/task/my/live-patrol          # row created if absent (idempotent)
            └─→ workflow started (frontend timer)
                    ├─→ PATCH …/progress every 10 s  # incremental sync
                    ├─→ PATCH …/progress on suspend   # forced flush
                    ├─→ PATCH …/progress on route leave (router.beforeEach)
                    └─→ PATCH …/progress (is_completed=true) on stop
```

Timezone: all `shift_date` values are written and queried in **CST (UTC+8)**.

---

## Role / Permission Matrix

| Role | Key permissions |
|---|---|
| `manager` | All permissions + `view:shadow_audit`, `action:dispatch_task` |
| `team_leader` | `action:dispatch_task`, `view:shadow_audit` |
| `qa_specialist` | `view:violations`, `view:sop` |
| `auditor` | `view:realtime`, `view:sop` |

Permissions are defined server-side in `server/constants/permissions.py`. The frontend never checks role strings directly.

---

## Quick Start

### Backend

```bash
cd server
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env              # set DATABASE_URL, JWT_SECRET_KEY

# Apply migrations
alembic upgrade head

# Seed initial users (first run)
python -m server.db.init_db

# Start server
uvicorn server.main:app --host 0.0.0.0 --port 8000 --reload
```

API docs: `http://localhost:8000/docs`

### Frontend (development)

```bash
cd client/web
npm install
npm run dev
```

### Desktop build

```bash
# Requires Python 3.12 + Node.js 18+ in PATH
python client/build/build.py
# Output: dist/AHDUNYI_Terminal_PRO/AHDUNYI_Terminal_PRO.exe
```

Place `config.json` next to the `.exe` to override server URL and window dimensions.

---

## Configuration (`config.json`)

```jsonc
{
  "server":       { "url": "http://HOST:8000" },
  "gui":          { "window_width": 1440, "window_height": 900 },
  "room_monitor": { "target_process": "small_dimple.exe", "memory_probe_enabled": true },
  "debug":        { "enable_console": false }   // true opens a DevTools window
}
```

---

## CI/CD

- **`server-deploy.yml`** — triggers on push to `main` when `server/**` changes: flake8 lint → SSH into Aliyun ECS → `git pull` → `pip install` → `systemctl restart ahdunyi-api`
- **`client-build.yml`** — triggers on push to `main` when `client/**` changes: builds Vue frontend
