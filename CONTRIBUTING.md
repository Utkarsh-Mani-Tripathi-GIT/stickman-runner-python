# 🤝 Contributing to Stickman Runner

First off, **thank you** for considering contributing! Every bit of help makes this game better.

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Getting Started](#getting-started)
- [Pull Request Process](#pull-request-process)
- [Style Guide](#style-guide)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)

---

## 📜 Code of Conduct

This project follows a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold a welcoming and respectful community.

---

## 🛠 How Can I Contribute?

### 🐛 Bug Fixes
Found something broken? Open an issue or submit a fix directly.

### ✨ New Features
Ideas for the game? Here are some areas that'd be great to expand:
- New enemy types (helicopters, drones, etc.)
- Power-ups (shields, slow-motion, double jump)
- New obstacle variants
- Additional sound effects
- Settings menu (volume, key remapping)
- Persistent high score saving to file
- Multiplayer or online leaderboard

### 📖 Documentation
Improvements to docs, README, or in-code comments are always welcome.

### 🎨 Visual Enhancements
Better animations, new particle effects, or UI polish.

---

## 🚀 Getting Started

1. **Fork** the repository
2. **Clone** your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/stickman-runner.git
   cd stickman-runner
   ```
3. **Create a branch** for your feature/fix:
   ```bash
   git checkout -b feature/my-awesome-feature
   ```
4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
5. **Make your changes** and test them by running the game:
   ```bash
   python stickman_runner.py
   ```
6. **Commit** your changes:
   ```bash
   git add .
   git commit -m "feat: add my awesome feature"
   ```
7. **Push** and open a **Pull Request**

---

## ✅ Pull Request Process

1. Ensure your code runs without errors
2. Test the game thoroughly — play at least a few rounds to verify no regressions
3. Update the `CHANGELOG.md` if you're adding a notable change
4. Write a clear PR description explaining **what** you changed and **why**
5. Reference any related issues (e.g., `Closes #42`)

---

## 🎨 Style Guide

### Python

- Follow **PEP 8** where practical
- Use descriptive variable names
- Keep functions focused and well-commented
- All procedural sprite generation should use `pygame.draw` primitives (no external image files)
- Sound effects should use the built-in `_syn()` synthesizer

### Commits

Use [Conventional Commits](https://www.conventionalcommits.org/) where possible:

| Prefix | Usage |
|---|---|
| `feat:` | New feature |
| `fix:` | Bug fix |
| `docs:` | Documentation only |
| `style:` | Formatting, no logic change |
| `refactor:` | Code restructure, no feature change |
| `perf:` | Performance improvement |
| `test:` | Adding tests |

---

## 🐛 Reporting Bugs

When reporting a bug, please include:

- **OS and version** (e.g., Windows 11, macOS 14, Ubuntu 22.04)
- **Python version** (`python --version`)
- **Pygame version** (`pip show pygame`)
- **Steps to reproduce** the issue
- **Expected behavior** vs. **actual behavior**
- **Screenshots or error logs** if applicable

---

## 💡 Suggesting Features

Open an issue tagged `enhancement` with:

- A **clear description** of the feature
- **Why** it would improve the game
- Any **mockups or references** you have in mind

---

## 📄 License

By contributing, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).

---

<p align="center">
  Thank you for making <b>Stickman Runner</b> better! 🎮
</p>
