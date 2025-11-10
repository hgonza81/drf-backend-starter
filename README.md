# Django REST Framework Project

A Django REST Framework application with Docker support and multi-environment configuration.

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Docker & Docker Compose (for containerized development)
- Make (optional, for using Makefile commands)

### Local Development Setup

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd <project-name>
   ```
1. **Create virtual environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
1. **Install dependencies**

   ```bash
   pip install -r requirements/dev.txt
   ```
1. **Run migrations**

   ```bash
   make migrate
   ```
1. **Create superuser**

   ```bash
   make superuser
   ```
1. **Run containerized development server**

   ```bash
   make dev
   ```

## 🧪 Running Tests

```bash
# Run tests in Docker
make test

# Clean up test containers
make test-down
```

## 📝 Configuration

### Environment Variables

Environment variables are stored in `envs/` directory:

- `envs/.env.base` - Common environment
- `envs/.env.dev` - Development environment
- `envs/.env.test` - Testing environment
- `envs/.env.prod` - Production environment

### Settings Structure

Settings are split into multiple files for better organization:

- `app/core/settings/base.py` - Common settings
- `app/core/settings/dev.py` - Development settings
- `app/core/settings/test.py` - Testing settings
- `app/core/settings/prod.py` - Production settings

### Requirements Structure

Dependencies are organized by environment:

- `requirements/base.txt` - Core dependencies
- `requirements/dev.txt` - Development dependencies
- `requirements/test.txt` - Testing dependencies
- `requirements/prod.txt` - Production dependencies