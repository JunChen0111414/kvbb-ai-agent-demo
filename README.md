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