/**
 * Development startup script
 * Ensures backend, frontend, and Electron start in the correct order
 */

const { spawn } = require('child_process');
const http = require('http');

function waitForServer(url, timeout = 30000) {
  return new Promise((resolve, reject) => {
    const startTime = Date.now();
    
    function check() {
      const req = http.get(url, (res) => {
        resolve();
      });
      
      req.on('error', () => {
        if (Date.now() - startTime > timeout) {
          reject(new Error(`Timeout waiting for ${url}`));
        } else {
          setTimeout(check, 500);
        }
      });
    }
    
    check();
  });
}

async function start() {
  console.log('🚀 Starting Quiz Grader (NewStyle)...\n');
  
  // Start backend server
  console.log('📡 Starting backend server...');
  const backend = spawn('node', ['server.js'], {
    cwd: __dirname,
    stdio: 'inherit',
    shell: true
  });
  
  // Start frontend dev server
  console.log('⚛️  Starting frontend dev server...');
  const frontend = spawn('npm', ['run', 'dev'], {
    cwd: __dirname,
    stdio: 'inherit',
    shell: true
  });
  
  // Wait for both servers to be ready
  console.log('⏳ Waiting for servers to be ready...');
  try {
    await Promise.all([
      waitForServer('http://localhost:5000/api/test'),
      waitForServer('http://localhost:3000')
    ]);
    
    console.log('✅ Servers ready!');
    console.log('🪟 Launching Electron...\n');
    
    // Start Electron
    const electron = spawn('npx', ['electron', '.'], {
      cwd: __dirname,
      stdio: 'inherit',
      shell: true
    });
    
    // Cleanup on exit
    process.on('SIGINT', () => {
      console.log('\n🛑 Shutting down...');
      backend.kill();
      frontend.kill();
      electron.kill();
      process.exit();
    });
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    backend.kill();
    frontend.kill();
    process.exit(1);
  }
}

start();

