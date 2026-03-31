# QueueLessClinics

QueueLessClinics is a clinic queue management platform scaffolded with an Angular frontend, a Django backend, and a Docker-based local development environment.

The project is set up to support a modern full-stack workflow with separate frontend and backend services, PostgreSQL for persistence, Redis for caching, and pgAdmin for database administration during development.

## Tech Stack

- Angular 15 frontend
- Django backend
- Django REST Framework
- PostgreSQL 15
- Redis 7
- Docker Compose
- Nginx for production frontend serving

## Project Structure

- `angular-app/` Angular application
- `django-backend/` Django project and app source
- `database/` SQL schema and seed files
- `docker-compose.yml` Multi-service local development setup

## Development Environment

The repository includes Docker configuration for:

- Angular development server on port `4200`
- Django development server on port `8000`
- PostgreSQL on port `5432`
- Redis on port `6379`
- pgAdmin on port `5050`

## Getting Started

To start the full local environment:

```bash
docker compose up --build
```
