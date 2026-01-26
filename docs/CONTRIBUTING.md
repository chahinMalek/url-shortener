# Contributing to URL Shortener

First off, thank you for considering contributing to the URL Shortener project! It's people like you that make it a better tool for everyone.

## Table of Contents
1.  [How Can I Contribute?](#how-can-i-contribute)
2.  [Development Setup](#development-setup)
3.  [Style Guidelines](#style-guidelines)
4.  [Pull Request Process](#pull-request-process)
5.  [ML Contributions](#ml-contributions)

---

## How Can I Contribute?
*   **Reporting Bugs**: Use GitHub Issues to report bugs.
*   **Suggesting Enhancements**: We are always looking for ways to make the tool faster and safer.
*   **Code Contributions**: Pick up an issue or work on something from our [Roadmap](./docs/ROADMAP.md).

## Development Setup
This project uses `uv` for dependency management.

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/your-username/url-shortener.git
    cd url-shortener
    ```
2.  **Install dependencies**:
    ```bash
    uv sync
    ```
3.  **Run the application**:
    ```bash
    uv run fastapi dev app/api.py
    ```
4.  **Run tests**:
    ```bash
    uv run pytest
    ```
5.  **Running pytest with coverage report**:
    ```bash
    uv run pytest --cov=core --cov=infra --cov-report=term-missing tests/
    ```

## Style Guidelines
*   **Python**: We use `ruff` for linting and formatting. Ensure your code passes `ruff check .`.
*   **Type Hits**: Use type hints everywhere to maintain code quality and enable better IDE support.
*   **Documentation**: Update the `docs/` directory if you add or change features.

## Pull Request Process
1.  Create a branch from `main`.
2.  Ensure all tests pass and the code is formatted.
3.  Update the `README.md` or `docs/` if necessary.
4.  Submit a PR with a clear description of the changes.

## ML Contributions
Since we are integrating a 2-tier ML classification system:
*   **Tier 1 (Fast)**: Must be optimized for low latency (< 50ms).
*   **Tier 2 (Heavy)**: Can be more compute-intensive but should be designed for batch processing.
*   When adding new models, provide benchmarks and details on the training dataset used.
