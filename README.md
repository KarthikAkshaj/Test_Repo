# TaskFlow

A lightweight task and project management platform. This repository contains the core REST API, a TypeScript browser SDK, a Go notification delivery service, and a Java analytics aggregation service.

## Architecture

| Component | Language / Runtime | Purpose |
|---|---|---|
| `backend/` | Python 3.11 · Flask | Core REST API (users, projects, tasks) |
| `frontend/` | TypeScript · Node 20 | Browser client SDK and form utilities |
| `services/notifications/` | Go 1.22 | Real-time in-app notification delivery |
| `services/analytics/` | Java 17 · Spring Boot | Reporting and analytics aggregation |

## Quick Start

```bash
# Full stack (requires Docker)
docker-compose -f infra/docker-compose.yml up

# Backend only
cd backend
pip install -r requirements.txt
flask run

# Frontend SDK
cd frontend
npm install
npm test

# Notifications service
cd services/notifications
go run .

# Analytics service
cd services/analytics
mvn spring-boot:run
```

## Docs

- [API Reference](docs/API_SPEC.md)
- [Coding Guidelines](docs/CODING_GUIDELINES.md)
- [Contributing](CONTRIBUTING.md)
