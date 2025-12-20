# D2L Assignment Assistant

**Version 0.0.1 (Beta)** - A desktop application for streamlining D2L/Brightspace assignment grading.

## Overview

D2L Assignment Assistant automates the tedious parts of grading assignments from D2L/Brightspace. It extracts student submissions from ZIP files, combines PDFs for efficient grading, uses OCR to extract written grades, and prepares files for re-upload.

## Quick Start

### For End Users

1. Run the installer: `D2L Assignment Assistant Setup 0.0.1.exe`
2. Launch the application
3. Configure your class using "CLASS SETUP"
4. Start processing assignments!

### For Developers

**Build from source:**
```bash
.\BUILD.bat
```

This script will:
- Clean old builds
- Check for/download bundled Python
- Build the frontend (Vite/React)
- Package the Electron app
- Launch the installer

**Development mode:**
```bash
npm run dev:all
```

See [PROJECT_SYNOPSIS.md](PROJECT_SYNOPSIS.md) for detailed development documentation.

## Key Features

- **Process Quizzes**: Extract, combine, and watermark student submissions
- **Extract Grades**: OCR-powered grade extraction from annotated PDFs
- **Process Completions**: Auto-assign completion grades (10 points)
- **Split PDF & Rezip**: Break combined PDF back into individual files for D2L upload
- **Class Management**: Organize multiple classes with custom configurations
- **Clear Data**: Flexible cleanup with selective preservation options

## System Requirements

- **OS**: Windows 10/11
- **Python**: 3.11+ (bundled with installer)
- **Node.js**: 18+ (for development only)
- **Storage**: 500MB+ free space

## Project Structure

```
D2L-Assignment-Assistant/
├── src/                    # React frontend (TypeScript)
├── electron/               # Electron main process
├── scripts/                # Python CLI scripts
├── python-modules/         # Reusable Python modules
├── docs/                   # Documentation
│   ├── plans/              # Planning documents
│   └── archived/           # Outdated documentation
├── dev-tools/              # Testing and development utilities
├── server.js               # Node.js backend (Express)
├── BUILD.bat               # Build script
├── package.json            # Dependencies and scripts
├── PROJECT_SYNOPSIS.md     # Detailed architecture documentation
└── CHANGELOG.md            # Version history
```

## Documentation

- **[PROJECT_SYNOPSIS.md](PROJECT_SYNOPSIS.md)**: Complete architecture, workflows, and development guide
- **[CHANGELOG.md](CHANGELOG.md)**: Version history and release notes
- **docs/archived/**: Older documentation (kept for reference)

## Support & Issues

This is beta software. If you encounter issues:
1. Check the logs in the application
2. Review [PROJECT_SYNOPSIS.md](PROJECT_SYNOPSIS.md) for technical details
3. Ensure your class folder structure matches the expected format

## License

Internal use only.
