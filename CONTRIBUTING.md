# Contributing to DesignKit

First of all, thank you for considering contributing to **DesignKit**! ❤️

Our goal is to build a modern, educational, and production-ready collection of software architecture and design patterns for Python, powered by Rust where appropriate.

Please read this document before opening a Pull Request.

---

# Philosophy

DesignKit prioritizes:

- 📚 Education and readability over micro-optimizations.
- 🐍 Pythonic APIs.
- 🦀 Rust implementations for performance-critical components.
- 🧩 Reusable software architecture.
- 📝 Complete documentation.
- 🧪 Reliable testing.
- 🔒 Stable public APIs.

Every contribution should improve the library without making it harder to understand.

---

# Before Contributing

Make sure you:

- Read the project README.
- Read the LICENSE.
- Search existing Issues and Pull Requests.
- Verify your idea has not already been implemented.

---

# Development Setup

Clone the repository

```bash
git clone https://github.com/Sheniey/designkit.git
cd designkit
```

Create a virtual environment

```bash
python -m venv .venv
```

Activate it

Windows

```bash
.venv\Scripts\activate
```

Linux/macOS

```bash
source .venv/bin/activate
```

Install development dependencies

```bash
pip install -e ".[dev]"
```

Build the Rust extension

```bash
maturin develop
```

Run tests

```bash
pytest
```

---

# Python Version

DesignKit currently targets:

- Python **3.14+**

Pull Requests using older Python syntax will not be accepted.

---

# Project Structure

A typical pattern should contain:

```
designkit/
    behavioral/
        my_pattern/
            __init__.py
            core.py
            ...
tests/
    behavioral/
        test_my_pattern.py
samples/
    behavioral/
        my_pattern.py
```

Documentation should be reflected in:

- README.md
- TODO.md
- Pattern documentation (if applicable)

---

# Adding a New Design Pattern

Every new pattern must include:

## 1. Implementation

Implement the pattern following the project's coding style.

Prefer:

- Type hints
- Clear naming
- Small classes
- Small functions
- Documentation strings

---

## 2. Tests

Every feature should be tested.

Tests should cover:

- Normal usage
- Invalid inputs
- Edge cases
- Public API

Use `pytest`.

---

## 3. Sample

Provide at least one working example under:

```
samples/
```

Examples should be educational and executable.

---

## 4. Documentation

Document:

- What problem the pattern solves
- Why it exists
- When it should be used
- Advantages
- Disadvantages
- Example usage

---

# Code Style

Preferred conventions:

- PEP 8
- Type annotations everywhere
- Explicit imports
- Meaningful names
- No dead code
- No commented-out code

Avoid unnecessary complexity.

Readable code is preferred over clever code.

---

# Rust Code

Rust is used for performance-sensitive implementations.

Rust code should:

- Follow idiomatic Rust
- Be memory safe
- Expose clean Python APIs through PyO3
- Avoid unsafe blocks unless absolutely necessary

---

# API Design

Public APIs should be:

- Easy to discover
- Easy to read
- Easy to type
- Stable

Breaking API changes are discouraged.

---

# Pull Requests

Every Pull Request must use the provided PR template.

The checklist must be completed honestly.

A PR should focus on **one design pattern** whenever possible.

Large unrelated changes may be rejected.

---

# Pull Request Requirements

A Pull Request should:

- Build successfully
- Pass all tests
- Include documentation
- Include examples
- Include type hints
- Avoid breaking changes
- Follow the project philosophy

---

# Commit Messages

Recommended format:

```bash
feat(pattern): implement state pattern

fix(observer): fix subscription bug

docs: improve README

test(factory): add edge cases

refactor(builder): simplify API
```

---

# Reporting Bugs

Please include:

- Python version
- Operating system
- Minimal reproducible example
- Expected behavior
- Actual behavior

---

# Feature Requests

Explain:

- The problem
- Why it matters
- Possible implementation
- Alternatives considered

---

# Code of Conduct

Please be respectful.

Constructive discussions are encouraged.

Harassment, discrimination, or toxic behavior will not be tolerated.

---

# License

By submitting code, you agree that your contribution will be licensed under the project's MIT License.

---

Thank you for helping make **DesignKit** better.