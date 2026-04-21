# MCP-AI-Agent-test

Reusable MCP scaffold for KVBB-like agent projects.

## Overview

This project provides a reusable MCP-based integration layer for agent applications.  
It currently includes four MCP server domains:

- business_data
- notification
- status
- human_review

The `business_data` server is already connected to a real local PostgreSQL database.  
The other three servers currently use mock clients and can later be replaced with real APIs.

---

## Project Structure

```text
MCP-AI-Agent-test/
├─ agent.py
├─ mcp.json
├─ requirements.txt
├─ .env
├─ shared/
│  ├─ __init__.py
│  ├─ config.py
│  ├─ errors.py
│  └─ logging.py
└─ servers/
   ├─ __init__.py
   ├─ business_data/
   │  ├─ __init__.py
   │  ├─ repository.py
   │  ├─ schemas.py
   │  ├─ server.py
   │  └─ tools.py
   ├─ notification/
   │  ├─ __init__.py
   │  ├─ client.py
   │  ├─ schemas.py
   │  ├─ server.py
   │  └─ tools.py
   ├─ status/
   │  ├─ __init__.py
   │  ├─ client.py
   │  ├─ schemas.py
   │  ├─ server.py
   │  └─ tools.py
   └─ human_review/
      ├─ __init__.py
      ├─ client.py
      ├─ schemas.py
      ├─ server.py
      └─ tools.py




Setup
1. Create and activate virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

If PowerShell blocks activation:

Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.venv\Scripts\Activate.ps1

2. Install dependencies
python -m pip install -r requirements.txt




Environment Variables

Example .env for local PostgreSQL:

DB_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/kvbb?sslmode=disable
DB_SCHEMA=public

MAIL_API_BASE=https://mail.example.com/api
MAIL_API_KEY=demo-mail-key

STATUS_API_BASE=https://status.example.com/api
STATUS_API_TOKEN=demo-status-token

REVIEW_API_BASE=https://review.example.com/api
REVIEW_API_TOKEN=demo-review-token

## Environment Switching

Use `.env` as the active runtime configuration.

Switch to local:
```powershell
Copy-Item .env.local .env -Force

Switch to Azure:
Copy-Item .env.azure .env -Force

Verify active configuration:

python -c "from shared.config import get_business_data_config; print(get_business_data_config())"





Local PostgreSQL Test Data

The local PostgreSQL database used for testing is:

host: localhost
port: 5432
database: kvbb
schema: public
table: cases

Example test row:

case_id: KVBB-12345
customer_id: C-10001
status: pending_review




MCP Configuration

mcp.json defines the available MCP servers:

business-data
notification
status
human-review

agent.py currently validates and prints the configured MCP servers.

Run:

python agent.py
Current Verification Commands
business_data
python -c "from servers.business_data.tools import get_case_status; print(get_case_status({'case_id':'KVBB-12345'}))"
python -c "from servers.business_data.tools import search_cases; print(search_cases({'filters': {'customer_id': 'C-10001'}, 'limit': 20}))"
notification
python -c "from servers.notification.tools import preview_notification; print(preview_notification({'template_id':'case_update','variables':{'case_id':'KVBB-12345','status':'approved'}}))"
python -c "from servers.notification.tools import send_notification; print(send_notification({'recipient':'user@example.com','channel':'email','template_id':'case_update','variables':{'case_id':'KVBB-12345','status':'approved'}}))"
status
python -c "from servers.status.tools import get_workflow_status; print(get_workflow_status({'workflow_id':'WF-1001'}))"
python -c "from servers.status.tools import get_processing_summary; print(get_processing_summary({'case_id':'KVBB-12345'}))"
human_review
python -c "from servers.human_review.tools import create_review_task; print(create_review_task({'case_id':'KVBB-12345','review_type':'eligibility_check','payload':{'reason':'confidence_below_threshold','score':0.61}}))"
python -c "from servers.human_review.tools import submit_review_decision; print(submit_review_decision({'task_id':'review-555','decision':'approved','comment':'Looks good'}))"





Current Status

Completed:

MCP scaffold created
Local project structure established
business_data connected to real local PostgreSQL
notification, status, and human_review mocks verified
Git repository initialized
Initial backup created
Initial Git commit completed





Next Steps

Planned next improvements:

connect status to a real API
connect notification to a real mail or messaging API
connect human_review to a real review workflow system
add Azure PostgreSQL environment configuration
integrate MCP servers with a real agent runtime