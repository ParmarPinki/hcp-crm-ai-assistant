# AI-First CRM HCP Module (React + Redux + FastAPI + LangGraph + Groq + MySQL)

This project implements the **Log Interaction Screen** from the assessment using the required stack:

- Frontend: **React + JavaScript + Vite + Redux Toolkit**
- Backend: **FastAPI + LangGraph**
- LLM: **Groq** (`llama-3.1-8b-instant`) with a mock fallback for local testing
- Database: **MySQL**
- Font: **Google Inter**

The left-side form is intentionally **read-only**. The right-side AI assistant fills and edits the form through LangGraph tool routing.

## LangGraph tools included

1. `log_interaction`
2. `edit_interaction`
3. `resolve_hcp`
4. `search_materials`
5. `suggest_follow_up`

## Project structure

```text
hcp-crm-mysql-fullstack/
├── docker-compose.yml
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── .env.example
│   ├── index.html
│   └── src/
│       ├── app/
│       ├── components/
│       ├── features/
│       ├── services/
│       └── styles/
├── backend/
│   ├── requirements.txt
│   ├── .env.example
│   ├── run.py
│   └── app/
│       ├── agents/
│       ├── api/
│       ├── core/
│       ├── db/
│       ├── schemas/
│       └── services/
└── README.md
```

## 1) Start MySQL

You need Docker Desktop or Docker Engine installed.

```bash
cd hcp-crm-mysql-fullstack
docker compose up -d mysql
```

MySQL runs on:

- Host: `localhost`
- Port: `3306`
- Database: `hcp_crm`
- User: `root`
- Password: `root`

## 2) Run the backend

```bash
cd backend
python -m venv venv
```

### macOS / Linux

```bash
source venv/bin/activate
```

### Windows PowerShell

```powershell
venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create `.env` from the example:

### macOS / Linux

```bash
cp .env.example .env
```

### Windows PowerShell

```powershell
Copy-Item .env.example .env
```

Update `.env` if needed. Default MySQL connection string is already set:

```env
DATABASE_URL=mysql+pymysql://root:root@localhost:3306/hcp_crm
```

Run backend:

```bash
python run.py
```

Backend URL:

- `http://localhost:8000`
- Health check: `http://localhost:8000/health`

## 3) Run the frontend

Open another terminal:

```bash
cd frontend
npm install
```

Create frontend env file:

### macOS / Linux

```bash
cp .env.example .env
```

### Windows PowerShell

```powershell
Copy-Item .env.example .env
```

Run Vite:

```bash
npm run dev
```

Frontend URL:

- `http://localhost:5173`

## 4) Groq setup

For the real assignment demo, add your Groq key in `backend/.env`:

```env
GROQ_API_KEY=your_real_groq_api_key
MODEL_NAME=llama-3.1-8b-instant
ALLOW_MOCK_LLM=true
```

If you do not add a Groq key, the app still runs in **mock AI mode** so you can test the UI and LangGraph flow locally.

## 5) High-Level Architecture

```text
+----------------------- FRONTEND -----------------------+
| React + JavaScript + Vite                              |
| Redux Toolkit                                          |
|                                                        |
|  +-------------------+    +-------------------------+  |
|  | Interaction Form  |    | AI Assistant Chat Panel |  |
|  | (read-only draft) |    | user enters natural     |  |
|  | left panel        |    | language messages       |  |
|  +-------------------+    +-------------------------+  |
|              \                 /                       |
|               \               /                        |
|                \             /                         |
|                 +-----------+                          |
|                 | Redux     |                          |
|                 | Store     |                          |
|                 | - form    |                          |
|                 | - chat    |                          |
|                 | - status  |                          |
|                 +-----------+                          |
+------------------------|------------------------------+
                         |
                         | HTTP / JSON
                         v
+------------------------ BACKEND -----------------------+
| FastAPI API                                             |
|                                                        |
|  POST /api/ai/chat                                     |
|  POST /api/interactions                                |
|                                                        |
|                +--------------------------+            |
|                | LangGraph Agent          |            |
|                | shared state + routing   |            |
|                +--------------------------+            |
|                   |        |        |                  |
|                   v        v        v                  |
|          +--------------+  +------------------+       |
|          | Log/Edit via |  | Rule-based tools |       |
|          | Groq LLM     |  | resolve/search   |       |
|          +--------------+  +------------------+       |
|                   \         /                          |
|                    \       /                           |
|                     v     v                            |
|                +------------------+                    |
|                | Suggestions tool |                    |
|                +------------------+                    |
+------------------------|------------------------------+
                         |
                         | SQLAlchemy / ORM
                         v
+------------------------ DATABASE ----------------------+
| MySQL                                                   |
| - interactions                                          |
| - audit / saved interaction data                        |
+--------------------------------------------------------+
```

## 6) LangGraph Workflow

```text
                      +------------------+
                      |   route_intent   |
                      +------------------+
                         /      |      \
                        /       |       \
                       v        v        v
          +----------------+  +----------------+  +----------------------+
          |log_interaction |  |edit_interaction|  | suggest_follow_up    |
          |    _tool       |  |    _tool       |  |       _tool          |
          +----------------+  +----------------+  +----------------------+
                    \               /
                     \             /
                      v           v
                 +----------------------+
                 |   resolve_hcp_tool   |
                 +----------------------+
                            |
                            v
                 +----------------------+
                 | search_materials_tool|
                 +----------------------+
                            |
                            v
                 +----------------------+
                 | suggest_follow_up    |
                 |       _tool          |
                 +----------------------+
                            |
                            v
                 +----------------------+
                 |  finalize_response   |
                 +----------------------+
                            |
                            v
                           END
```


## Example prompts to test

- `Today I met Dr. Smith and discussed Product X efficacy. Sentiment was positive and I shared brochures.`
- `Correction: the doctor was Dr. John and the sentiment was negative.`
- `Suggest next best actions for this HCP.`
- `I also distributed samples and want a follow up next week.`

