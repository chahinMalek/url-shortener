# 🔗 URL Shortener with ML-Powered Safety Classification

A modern, fast, and secure URL shortening system built with FastAPI and enhanced with a 2-tier Machine Learning classification system to detect and block malicious links.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![CI](https://github.com/chahinMalek/url-shortener/actions/workflows/ci.yml/badge.svg)](https://github.com/chahinMalek/url-shortener/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Tests](https://img.shields.io/badge/tests-120%20passed-success)](https://github.com/chahinMalek/url-shortener/actions)
[![Coverage](https://img.shields.io/badge/coverage-99%25-green)](https://github.com/chahinMalek/url-shortener/actions)
[![Code Style](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

## 🚀 Vision: Safety First
The core philosophy of this project is to provide more than just a redirection service. We aim to protect users from phishing and malware by integrating intelligent classification models at two levels:
1.  **⚡ Tier 1 (Online)**: A lightning-fast XGBoost classifier (via ONNX) that performs real-time checks during shortening requests, blocking known threats with <50ms latency.
2.  **🔍 Tier 2 (Offline)**: A deep-learning based re-scan of newly added URLs to detect sophisticated threats that might have bypassed the initial check.

---

## 🎯 Features

- **URL Shortening**: Generate short codes with collision detection
- **User Authentication**: JWT-based auth with registration and login
- **ML Safety Classification**: Two-tier approach (fast + deep inspection)
- **Rate Limiting**: Redis-backed request throttling
- **Background Processing**: Celery workers for async classification
- **Auto-Remediation**: Malicious URLs automatically disabled
- **Docker Ready**: Full Docker Compose setup for all services

---

## 🛠️ Tech Stack

| Category | Technology |
|----------|------------|
| **Framework** | FastAPI |
| **Database** | SQLAlchemy 2.0 (Async) + PostgreSQL |
| **Cache & Rate Limiting** | Redis |
| **Background Tasks** | Celery + Redis (broker) |
| **Task Monitoring** | Flower |
| **ML Runtime** | ONNX Runtime |
| **Dependency Management** | `uv` |
| **Linting & Formatting** | `ruff` |
| **Testing** | `pytest` + `pytest-asyncio` |
| **CI/CD** | GitHub Actions |

---

## 🏁 Getting Started

### Prerequisites
- [uv](https://github.com/astral-sh/uv) installed.
- Redis server running (for rate limiting).

### Installation
1.  **Clone the Repo**:
    ```bash
    git clone https://github.com/your-username/url-shortener.git
    cd url-shortener
    ```
2.  **Install Dependencies**:
    ```bash
    uv sync
    ```
3.  **Environment Setup**:
    ```bash
    cp .env.example .env
    # Edit .env with your configuration
    ```
4.  **Run Development Server**:
    ```bash
    uv run fastapi dev app/api.py
    ```

### Docker (Recommended)
Run all services (API, PostgreSQL, Redis, Celery worker, Celery beat, Flower) with:
```bash
docker compose up
```

Services available:
- **API**: http://localhost:8000
- **Flower** (task monitoring): http://localhost:5555

---

## 📖 Documentation

- **[Architecture](./docs/ARCHITECTURE.md)** - System design, component layout, and data flow
- **[Roadmap](./docs/ROADMAP.md)** - Development phases and upcoming features
- **[API Docs](http://localhost:8000/docs)** - Interactive Swagger UI (when running)

---

## 🤝 Contributing
We welcome contributions! Please see our [Contributing Guidelines](./CONTRIBUTING.md) to get started and check the [Roadmap](./docs/ROADMAP.md) for open tasks.

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
