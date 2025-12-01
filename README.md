# Quiz Grader - New UI

A modern React frontend for the Quiz Grader application with a Figma-designed metallic button style.

## Quick Start (Development/Testing)

### Option 1: Run Both Servers Together (Recommended)
```bash
npm run dev:all
```
This starts both the backend server (port 5000) and the frontend dev server (port 3000).

### Option 2: Run Separately
In one terminal:
```bash
npm run dev:server
```

In another terminal:
```bash
npm run dev:frontend
```

Then open http://localhost:3000 in your browser.

## Available Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start frontend dev server only (port 3000) |
| `npm run dev:server` | Start backend server only (port 5000) |
| `npm run dev:frontend` | Same as `npm run dev` |
| `npm run dev:all` | Start both frontend and backend together |
| `npm run build` | Build the frontend for production |
| `npm run package` | Build and package as Windows executable |
| `npm run package:dir` | Build and package (unpacked, for testing) |

## Building an Executable

### Prerequisites
- Node.js 18+ 
- Python 3.9+ (for the backend scripts)
- All Python dependencies installed (`pip install -r ../requirements.txt`)

### Build Steps

1. **Install dependencies** (if not already done):
   ```bash
   npm install
   ```

2. **Build the frontend**:
   ```bash
   npm run build
   ```

3. **Package as executable**:
   ```bash
   npm run package
   ```
   
   This creates the installer in the `dist/` folder.

### Quick Test Build
To test the build without creating an installer:
```bash
npm run package:dir
```
This creates an unpacked version in `dist/win-unpacked/` that you can run directly.

## Project Structure

```
NewStyle/
├── src/                    # React frontend source
│   ├── components/         # React components (Option1, Option2, Option3)
│   ├── services/           # API service for backend communication
│   └── styles/             # Global CSS styles
├── electron/               # Electron main process
│   ├── main.js             # Electron entry point
│   └── preload.js          # Preload script for IPC
├── server.js               # Standalone Express backend server
├── package.json            # Dependencies and scripts
├── vite.config.ts          # Vite configuration
└── dist/                   # Built files (after `npm run build`)
```

## How It Works

1. **Frontend** (React + Vite): Modern UI at `http://localhost:3000`
2. **Backend** (Express): API server at `http://localhost:5000`
3. **Python Scripts**: The backend calls Python scripts in the parent directory to process quizzes

## Troubleshooting

### "Cannot connect to backend"
Make sure the backend server is running:
```bash
npm run dev:server
```

### "Python not found"
Install Python 3.9+ and add it to your PATH.

### Port already in use
- Backend uses port 5000
- Frontend uses port 3000
Kill any processes using these ports or change the ports in the config.

## UI Options

The app includes three UI layout options:
- **Option1**: Sidebar navigation with compact main area
- **Option2**: Horizontal top bar with grid layout (default)
- **Option3**: Compact dashboard with 50/50 split

To switch, edit `src/App.tsx` and import a different option.
