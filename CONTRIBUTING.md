# Contributing Guide

Thank you for contributing to the **Japan's Earthquake Catalog** project.
This document explains how to set up the development environment and the workflow for contributing code.

---

## Development Setup

### Prerequisites

Install the following tools before working on the project.

#### Node.js (required for Pyright)

Pyright is written in TypeScript and requires Node.js.

Download: [NodeJS](https://nodejs.org/en/download/current)

Verify installation:

```bash
node --version
npm --version
```

---

#### uv (Python dependency manager)

This project uses **uv** to manage Python dependencies and run development tools.

Linux / macOS:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

If curl is not installed:

```bash
wget -qO- https://astral.sh/uv/install.sh | sh
```

Windows (PowerShell):

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Alternative installation:

```bash
pip install uv
```

Verify installation:

```bash
uv --version
```

---

## Initial Setup

Clone the repository and install the development environment:

```bash
git clone https://github.com/QB12-Group1/japans-earthquake-catalog.git
cd japans-earthquake-catalog

uv sync --group dev
uv run pre-commit install
```

---

## Development Workflow

All development happens on **feature branches created from `dev`**.

---

### 1. Start From the Latest `dev`

Before starting work, make sure your local `dev` branch is up to date.

```bash
git checkout dev
git pull origin dev
```

---

### 2. Create Your Branch

Create a branch for your change.

```bash
git checkout -b <your-branch-name>
```

---

### 3. Implement Your Changes

Work on your feature, bug fix or etc....

---

### 4. Commit Your Changes

Stage and commit your work.

```bash
git add .
git commit -m "describe your change"
```

---

### 5. Push Your Branch

```bash
git push -u origin <your-branch-name>
```

---

## Pull Requests

When your change is complete:

Open a **Pull Request into `dev`**.

`<your-branch-name> → dev`

Your code will be reviewed before merging.

Feature branches are typically deleted after the PR is merged.

---

## Release Flow

The repository follows this branch structure:

- `main` → stable production-ready code
- `dev` → active development branch

Workflow:

1. Contributors open PRs into **`dev`**
2. Features are reviewed and merged into **`dev`**
3. When `dev` becomes stable, it is merged into **`main`**

---

## Code Quality

This project uses **pre-commit hooks** to enforce code quality.

Tools used:

- Ruff (linting and formatting)
- Pyright (static type checking)
- Pre-commit hooks (file checks and whitespace fixes)

These checks run automatically before each commit.

To run them manually:

```bash
uv run pre-commit run
```

Fix any issues before pushing your changes.

---
