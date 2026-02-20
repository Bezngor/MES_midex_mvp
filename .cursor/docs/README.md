# MES_midex Documentation

## Quick Navigation

### 🚀 Getting Started
- [Setup Guide](./01_getting-started/setup-guide.md) - Environment setup

### 🏗️ Architecture
- [System Overview](./02_architecture/system-overview.md) - High-level design
- [Detailed Architecture](./02_architecture/detailed-architecture.md) - Full architecture docs
- [API Specification](./02_architecture/api-specification.md) - Endpoints reference
- [Database Schema](./02_architecture/database-schema.md) - Database design
- [Domain Model](./02_architecture/domain/model.md) - Business domain
- [Repository Structure](./02_architecture/repository-structure.md) - Project layout
- [Business Process Reference](./02_architecture/business-process-reference.md) - Workflows
- [DSIZ Customization](./02_architecture/dsiz/) - DSIZ module architecture (#1-7)

### 💻 Development
- [Coding Standards](./03_development/coding-standards.md) - Python & TypeScript standards
- [Testing Overview](./03_development/testing/overview.md) - Testing strategy
- [Testing Report](./03_development/testing/report.md) - Test results
- [Testing Summary](./03_development/testing/summary.md) - Summary
- [Manual Test Plan](./03_development/testing/manual-test-plan.md) - E2E testing
- [Manual E2E Report](./03_development/testing/manual-e2e-report.md) - E2E results
- [Test Run Guide](./03_development/testing/run-guide.md) - How to run tests
- [Customization Guide](./03_development/customization/guide.md) - Customization
- [Custom Tabs Development](./03_development/customization/custom-tabs.md) - Tabs guide

### 🔧 Operations
- [Deployment Guide](./04_operations/deployment-guide.md) - Docker, VPS
- [Deployment Manifest](./04_operations/deployment-manifest.md) - Production manifest
- [Docker Production](./04_operations/docker-production.md) - Docker setup
- [Data Load CSV](./04_operations/guides/data-load-csv.md) - CSV import
- [n8n Workflow Guide](./04_operations/guides/n8n-workflow.md) - n8n automation
- [Power BI Integration](./04_operations/guides/power-bi-integration.md) - Analytics

### 📋 Workflows
- [Feature Development](./05_workflows/feature-development.md) - Q→Cursor process
- [Git Workflow](./05_workflows/git-workflow.md) - Git processes
- [MRP Guide](./05_workflows/mrp-guide.md) - MRP workflow
- [Dispatching Guide](./05_workflows/dispatching-guide.md) - Dispatching
- [Production Connectivity](./05_workflows/production-connectivity-guide.md) - Integration
- [Strategic Planning Algorithm](./05_workflows/planning/strategic-algorithm.md) - Planning
- [Tactical Plan Phase 4](./05_workflows/planning/tactical-phase4.md) - Phase 4 planning
- [DSIZ Guides](./05_workflows/dsiz/) - DSIZ operations
- [AI Agent Instruction](./05_workflows/ai-agent/instruction-prompt.md) - AI workflow

### 📊 Diagrams
- [Orders Diagram (PDF)](./02_architecture/diagrams/orders.pdf)
- [Production Tasks (PDF)](./02_architecture/diagrams/production-tasks.pdf)

## Project Status

- **FastAPI:** >=0.104.0
- **DSIZ Module:** Feature-complete
- **Infrastructure:** Production-ready Docker setup

## Data Paths (for 1С Integration)

- **Import data:** `backend/data/import/`
- **Test fixtures:** `backend/data/fixtures/`

## Quick Links

- [GitHub Repository](https://github.com/Bezngor/MES_midex)
- [API Documentation](http://localhost:8000/docs) (when running)

---

*Last Updated: 2026-02-20*
