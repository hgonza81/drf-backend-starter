# Django REST Framework Project

Django project with Django REST Framework, configured with Docker, pre-commit hooks, and complete CI/CD.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Installation](#quick-installation)
- [Environment Configuration](#environment-configuration)
- [Development](#development)
- [Testing](#testing)
- [Code Quality](#code-quality)
- [CI/CD Pipeline](#cicd-pipeline)

---

## 🚀 Prerequisites

- **Docker** and **Docker Compose**
- **Python 3.12+** (for local development)
- **Git**
- **Make** (optional but recommended)

---

## ⚡ Quick Installation

### Just to run the project

If you only want to run the project without contributing code:

```bash
# 1. Clone the repository
git clone <repository-url>
cd <project-name>

# 2. Start the development environment
make dev
```

The server will be available at `http://localhost:8000`

### To contribute to the project

If you're going to develop and make commits:

```bash
# 1. Clone the repository
git clone <repository-url>
cd <project-name>make pip-install-dev

# 2. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# 3. Install dev dependencies and setup pre-commit hooks
make setup

# 4. Start the development environment
make dev
```

---

## ⚙️ Environment Configuration

The project uses **three separate environments**: development, testing, and production. Each environment has its own configuration divided into three layers:

### 1. Environment Variables (`envs/`)

```
envs/
├── .env.base      # Variables shared by all environments
├── .env.dev       # Development-specific variables
├── .env.test      # Testing-specific variables
└── .env.prod      # Production-specific variables
```

### 2. Django Settings (`app/core/settings/`)

```
app/core/settings/
├── base.py        # Base Django configuration
├── dev.py         # Development configuration (DEBUG=True)
├── test.py        # Testing configuration
└── prod.py        # Production configuration (DEBUG=False)
```

### 3. Docker Compose (`infra/docker/`)

```
infra/docker/
├── Dockerfile
├── docker-compose.base    # Base Docker configuration
├── docker-compose.dev     # Development services
├── docker-compose.test    # Testing services
└── docker-compose.prod    # Production services
```

The system automatically loads the correct configuration based on the environment using the pattern:

```bash
docker compose -f docker-compose.base -f docker-compose.{env}
```

---

## 💻 Development

### Start the development server

```bash
make dev
```

This will start:

- Django server at `http://localhost:8000`
- Database (if configured)
- Mounted volumes for hot-reload

### Useful development commands

```bash
# Stop the server
make dev-down

# Rebuild containers
make dev-rebuild

# Create migrations
make makemigrations

# Apply migrations
make migrate

# Create superuser
make createsuperuser

# Seed database with test data
make dev-seed
```

### View logs

```bash
docker compose -f infra/docker/docker-compose.base -f infra/docker/docker-compose.dev logs -f
```

---

## 🧪 Testing

### Run tests in Docker

```bash
make test
```

This command:

1. Builds the test container
2. Runs pytest with coverage
3. Generates coverage reports

### Clean test containers

```bash
make test-down
```

---

## ✅ Code Quality

### Pre-commit Hooks

The project uses **pre-commit hooks** to validate code before each commit and push.

#### Pre-commit Hooks (run before commit)

- **Ruff Linter & Formatter**: Automatically fixes style errors
- **Detect Secrets**: Detects credentials and secrets in code
- **YAML/TOML Validation**: Validates configuration files
- **Check Large Files**: Prevents commits of large files
- **Check Merge Conflicts**: Detects conflict markers

#### Pre-push Hooks (run before push)

- **Mypy Type Checking**: Verifies static types
- **Bandit Security Scan**: Scans for security vulnerabilities
- **Pip-audit**: Checks for vulnerabilities in dependencies

### Run validations manually

```bash
# Run all hooks
pre-commit run --all-files

# Run specific validation
make lint              # Linter with auto-fix
make lint-check        # Linter without auto-fix
make type-check        # Type checking
make detect-secrets    # Detect secrets
make security-check    # Security scan

# Run all validations (summary)
make quality-checks
```

### View all available commands

```bash
make help
```

---

## 🔄 CI/CD Pipeline

The project has **three GitHub Actions workflows** that run automatically:

### 1. **Code Quality** (`.github/workflows/ci-code-quality.yml`)

Runs on every push and pull request.

**Validations:**

- ✅ Ruff linting
- ✅ Mypy type checking
- ✅ Pre-commit hooks checks
- ✅ Detect secrets
- ✅ Bandit security scan

### 2. **Tests** (`.github/workflows/ci-tests.yml`)

Runs on every push and pull request.

**Actions:**

- 🧪 Runs tests in Docker
- 📊 Generates coverage report
- ✅ Validates that all tests pass

### 3. **SonarCloud** (`.github/workflows/ci-sonarcloud.yml`)

Runs after tests.

**Analysis:**

- 📈 Code quality analysis
- 🐛 Code smell detection
- 🔒 Vulnerability analysis
- 📊 Coverage metrics

### Complete flow

```
1. Developer makes commit
   ↓
2. Pre-commit hooks validate code locally
   ↓
3. Developer pushes
   ↓
4. Pre-push hooks run heavy validations
   ↓
5. GitHub Actions runs:
   - Code Quality workflow
   - Tests workflow
   - SonarCloud workflow (if tests pass)
   ↓
6. If everything passes ✅ → code ready to merge
```