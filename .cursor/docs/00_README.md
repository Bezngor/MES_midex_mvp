# MES_midex - Manufacturing Execution System

## 🎯 Project Overview

**MES_midex** — система управления производственными операциями (Manufacturing Execution System).

**Current Status:** Production-ready with DSIZ customization module

**Repository:** `Bezngor/MES_midex`

---

## 🏗️ Architecture

- **Backend:** FastAPI >=0.104.0, Python 3.11+, PostgreSQL 15
- **Frontend:** React 18, TypeScript, Vite, Material-UI
- **Infrastructure:** Docker, Docker Compose, VPS deployment

---

## 📚 Documentation Structure

| Section | Description |
|---------|-------------|
| [01_getting-started](./01_getting-started/) | Environment setup, first contribution |
| [02_architecture](./02_architecture/) | System design, API specs, database |
| [03_development](./03_development/) | Coding standards, testing, debugging |
| [04_operations](./04_operations/) | Deployment, monitoring, security |
| [05_workflows](./05_workflows/) | Feature development, bug fixing, releases |

---

## 🚀 Quick Start

1. **Clone repository**
2. **Setup environment** → See [01_getting-started/setup-guide.md](./01_getting-started/setup-guide.md)
3. **Read architecture** → See [02_architecture/system-overview.md](./02_architecture/system-overview.md)
4. **Start development** → See [03_development/coding-standards.md](./03_development/coding-standards.md)

---

## 🔄 Development Workflow

**Current Phase:** Phase 1 - Q Analysis → Cursor Prompts

1. Q analyzes code via GitHub API (read-only)
2. Q generates Cursor-ready prompts
3. Developer implements in Cursor IDE
4. Push to GitHub → Q performs automated PR review

---

## ⚠️ Important Notes

- **Knowledge Base:** See `memory/projects/MES_midex_parameters.md`
- **Workflow Rules:** See `memory/projects/MES_midex_workflow_rules.md`
- **Decisions Log:** Track all architectural decisions

---

*Last Updated: 2026-02-20*
