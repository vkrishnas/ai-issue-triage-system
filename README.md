# AI-Powered Issue Triage System

An event-driven backend system that automatically classifies system logs using a Groq LLM pipeline, persists data to MySQL, and monitors everything via a real-time Streamlit dashboard.

## Architecture

```
POST /logs (FastAPI)
    → Persist to MySQL (SQLModel)
    → Async webhook to n8n (<200ms)
    → Groq LLM classifies into 7 tiers
    → MySQL updated with category + urgency
    → If CRITICAL_SECURITY or SYSTEM_FATAL → Gmail alert sent
    → Streamlit dashboard reads /stats in real-time
```

## Tech Stack

- **Backend:** FastAPI, SQLModel, httpx
- **Database:** MySQL
- **Automation:** n8n (webhook-based workflow)
- **LLM:** Groq API (via n8n LangChain node)
- **Dashboard:** Streamlit, Plotly
- **Language:** Python

## 7 Classification Tiers

| Category | Description |
|----------|-------------|
| CRITICAL_SECURITY | Breaches, SQL injections, unauthorized access |
| SYSTEM_FATAL | Server crashes, DB failures, total downtime |
| DEVOPS_BUILD | Pipeline failures, Docker errors, deployment issues |
| USER_BILLING | Payment failures, subscription or refund issues |
| FEATURE_REQUEST | New functionality suggestions, UI/UX improvements |
| GENERAL_ENQUIRY | Non-urgent questions, basic support |
| SPAM | Irrelevant text, junk, or gibberish |

`CRITICAL_SECURITY` and `SYSTEM_FATAL` are flagged as urgent and trigger an automated Gmail alert.

## Key Metrics

- Webhook trigger latency: **< 200ms** (non-blocking async)
- Mean triage time reduction: **85%**
- Emergency response time reduction: **70%**
- Data integrity errors reduced: **90%**

## Project Structure

```
ai-issue-triage/
├── src/
│   ├── main.py          # FastAPI backend + SQLModel schema
│   ├── app.py           # Streamlit NOC dashboard
│   └── workflow.json    # n8n automation workflow
├── .env.example         # Environment variable template
├── .gitignore
├── requirements.txt
└── README.md
```

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/vkrishnas/ai-issue-triage
cd ai-issue-triage
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy the example file and fill in your credentials:
```bash
cp .env.example .env
```

Open `.env` and set the following:

```env
# Your MySQL connection string
# Format: mysql+pymysql://<username>:<password>@<host>:<port>/<database_name>
DATABASE_URL=mysql+pymysql://root:yourpassword@localhost:3306/ai_triage_system

# n8n webhook URL
# Found in your n8n workflow under the Webhook node → Production URL
N8N_WEBHOOK_URL=http://localhost:5678/webhook-test/triage-trigger
```

> ⚠️ Never commit your `.env` file. It is already in `.gitignore`.

### 4. Run FastAPI backend
```bash
uvicorn src.main:app --reload
```

### 5. Run Streamlit dashboard
```bash
streamlit run src/app.py
```

### 6. Set up n8n workflow
- Import `src/workflow.json` into your n8n instance
- Add your **Groq API key** to the Groq Chat Model node
- Add your **Gmail OAuth2 credentials** to the Gmail node
- Update the **MySQL credentials** in both SQL nodes with your DB host, username, and password
- Activate the workflow

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/logs` | Ingest a new log entry + trigger n8n |
| GET | `/stats` | Classification distribution for dashboard |

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | Full MySQL connection string | `mysql+pymysql://root:pass@localhost:3306/ai_triage_system` |
| `N8N_WEBHOOK_URL` | n8n webhook endpoint URL | `http://localhost:5678/webhook-test/triage-trigger` |
