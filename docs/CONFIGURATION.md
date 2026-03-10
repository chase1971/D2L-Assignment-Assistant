# Configuration Guide — D2L Assignment Assistant

This guide explains how the app is configured and how to **make it work for any professor** (remove developer-specific paths and behavior).

---

## Current behavior (what’s hardcoded)

- **Path resolution** lives in **`python-modules/config_reader.py`**.
- Config is read from:
  - `%APPDATA%\D2L Assignment Extractor\config.json` (packaged app), or
  - Project root `config.json` (development).
- **`get_rosters_path()`** uses `config['rostersPath']` if it exists and the folder exists. If not, it falls back to **hardcoded** logic:
  - Username: `os.getenv('USERNAME', 'chase')` (default `'chase'`).
  - Drives: tries `G:` then `C:` with paths like `G:\My Drive\Rosters etc` and `C:\Users\<username>\My Drive\Rosters etc`.
- So on a machine without those paths or with a different username, the app can point at the wrong place or fail.

**To make the app distributable:** remove these fallbacks and rely on **config (or first-run setup)** only. If `rostersPath` is missing or invalid, show a clear error and tell the user how to set it (e.g. CLASS SETUP or config file).

---

## What to change (making it professor-friendly)

### 1. `config_reader.py` — single source of truth for paths

- **Rosters path:** Use only `config['rostersPath']`. If missing or path doesn’t exist:
  - **Option A (recommended):** Return a clear error message telling the user to set the rosters folder (e.g. via CLASS SETUP or by editing config), and document where config is stored.
  - **Option B:** Use an environment variable (e.g. `ROSTERS_BASE_PATH`) as override, still no hardcoded `C:`/`G:` or `chase`.
- **Remove:** The fallback that uses `username = os.getenv('USERNAME', 'chase')` and the loop over `G:`/`C:` and fixed path patterns. No hardcoded usernames or drive letters.
- **Downloads path:** Keep using `config['downloadsPath']` with a sensible default (e.g. user’s `~/Downloads`) if you want; avoid machine-specific paths.
- **Config file name/location:** The app may still refer to “D2L Assignment Extractor” in paths; align with the real app name (e.g. “D2L Assignment Assistant”) if needed so config is found in the right place.

### 2. Where config comes from

- **Packaged app:** Config is typically under `%APPDATA%\D2L Assignment Assistant\` (or the name your Electron app uses). The frontend/CLASS SETUP should write `config.json` there (rostersPath, downloadsPath, etc.).
- **Development:** A `config.json` in the project root can be used; document this in README or START_HERE.
- **Optional:** Support `.env` for overrides (e.g. `ROSTERS_BASE_PATH`) and document in this file.

### 3. First-run / new users

- On first run, if `rostersPath` is missing or invalid, show a clear message: e.g. “Set your rosters folder in CLASS SETUP” or “Edit config at …”.
- Document in **START_HERE.md** (or README): “New users: run the app, use CLASS SETUP to choose your rosters folder (and optionally downloads folder).”

### 4. API keys (secrets)

- **Google Cloud Vision:** Use `.env` in the project root with `GOOGLE_VISION_API_KEY=...`. Never commit `.env`. Provide `.env.example` with placeholder keys. Load in code (e.g. backend or Python) and pass to OCR. See START_HERE for setup steps.

---

## Config file format

**`config.json`** (created by app or manually):

```json
{
  "rostersPath": "C:\\Users\\YourName\\Documents\\Rosters",
  "downloadsPath": "C:\\Users\\YourName\\Downloads",
  "developerMode": false,
  "firstRun": true
}
```

- **rostersPath** — Base folder that contains one folder per class (each with `Import File.csv`, etc.). **Required** for grading; no hardcoded fallback.
- **downloadsPath** — Where to look for downloaded D2L ZIPs (e.g. Downloads). Default is fine if not set.
- **developerMode** / **firstRun** — Optional; use for UI or onboarding.

**`classes.json`** — Managed via CLASS SETUP in the app. Each class has an id, label, and **rosterFolderPath** (usually `rostersPath + "/" + classFolderName`). Don’t hardcode paths here; build them from `get_rosters_path()` and the chosen class name.

---

## Expected folder structure

```
<rostersPath>/
├── <ClassFolderName>/
│   ├── Import File.csv
│   └── grade processing <Class> <Assignment>/
│       ├── PDFs/
│       ├── unzipped folders/
│       └── archived/
└── (other class folders...)
```

Document this in START_HERE or README so professors know how to organize their folders.

---

## Checklist for “distributable” config

- [ ] `config_reader.get_rosters_path()` uses only config (and optional env); no `'chase'`, no `C:`/`G:` fallbacks.
- [ ] Clear error if rostersPath is missing or invalid, with instructions (CLASS SETUP or config path).
- [ ] Config file location documented (AppData vs project root).
- [ ] `.env` and `.env.example` documented for API keys; no keys in repo.
- [ ] START_HERE / README updated for new users (first run, CLASS SETUP, folder structure).
- [ ] Any remaining `drive` parameter in CLIs/APIs removed or ignored so all path resolution goes through config_reader.

---

## Troubleshooting

- **“Rosters path not set” / “Path does not exist”** — User must set rosters folder (CLASS SETUP or edit config). Point them to this doc and START_HERE.
- **“Config not found”** — Packaged app: check `%APPDATA%\D2L Assignment Assistant\` (or actual app name). Dev: check project root. Ensure the app creates or reads config from the same path.
- **Wrong folder opened** — Confirm `rostersPath` in config and that class folders live directly under it; no typos in class names or paths.

---

## Legacy note (REMOVE_DRIVE_DETECTION)

The old guide “REMOVE_DRIVE_DETECTION.md” referred to `common.py` and `grading_processor.py`. In the current codebase, path logic is in **`config_reader.py`** and scripts use `get_rosters_path()` / `get_downloads_path()` from there. Follow this CONFIGURATION guide instead; update config_reader and callers (no separate `common.py` needed unless you introduce one).
