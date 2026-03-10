# D2L Assignment Assistant — Documentation Index

Use this as the single place to find all project documentation.

---

## Start here (project root)

| Document | Purpose |
|----------|--------|
| [**START_HERE.md**](../START_HERE.md) | First-time setup, overview, dependencies, doc order. Read this before changing the codebase. |
| [**README.md**](../README.md) | Quick start, install, build, key features. |
| [**.cursorrules**](../.cursorrules) | AI coding rules, making the app distributable, and AI tips for students. |

---

## Configuration and distributable setup

| Document | Purpose |
|----------|--------|
| [**docs/CONFIGURATION.md**](CONFIGURATION.md) | How config works, what’s hardcoded, and how to make the app work for any professor (paths, config.json, .env, first-run). **Use this instead of the old REMOVE_DRIVE_DETECTION.md.** |

---

## Architecture and development

| Document | Purpose |
|----------|--------|
| [**docs/all-docs/PROJECT_SYNOPSIS.md**](all-docs/PROJECT_SYNOPSIS.md) | Full architecture, data flow, workflows, components, building, troubleshooting. |
| [**docs/ELECTRON_BUILD_AND_PATCH_GUIDE.md**](ELECTRON_BUILD_AND_PATCH_GUIDE.md) | Electron build, installer, packaging, Python bundling, (optional) auto-updates. |
| [**docs/all-docs/PATCH_SYSTEM_README.md**](all-docs/PATCH_SYSTEM_README.md) | Patch system: create, distribute, and apply patches without reinstalling. |
| [**docs/all-docs/REALTIME_LOGGING_IMPLEMENTATION.md**](all-docs/REALTIME_LOGGING_IMPLEMENTATION.md) | How real-time log streaming (SSE) works. |

---

## Workflow and patterns

| Document | Purpose |
|----------|--------|
| [**END_OF_SESSION_CHECKLIST.md**](../END_OF_SESSION_CHECKLIST.md) | What to do at the end of each dev session (SESSIONS.md, file headers, synopsis). |
| [**SESSIONS.md**](../SESSIONS.md) | Development history and session notes. |
| [**docs/all-docs/README.md**](all-docs/README.md) | Index of **Cursor pattern files** (refactoring, code-style, d2l-automation, selenium). Use when implementing or refactoring. |

---

## Other

| Document | Purpose |
|----------|--------|
| [**docs/all-docs/Attributions.md**](all-docs/Attributions.md) | Credits and attributions. |
| [**docs/archived/**](archived/) | Older or superseded docs (reference only). |

---

**Suggested order for a new developer:** START_HERE → CONFIGURATION (if making it distributable) → PROJECT_SYNOPSIS → .cursorrules. Use this README whenever you’re not sure which doc to open.
