/**
 * Standalone Backend Server for D2L Assignment Assistant
 * Run with: node server.js
 *
 * This server can run independently without Electron for development/testing.
 * For production, use the Electron packaged version.
 */

const { app, SCRIPTS_PATH } = require('./server/app');

const DEFAULT_PORT = 5000;
let PORT = DEFAULT_PORT;

function startServer(port) {
  const server = app.listen(port, () => {
    PORT = port;
    console.log('');
    console.log('='.repeat(50));
    console.log('  D2L Assignment Assistant Backend Server');
    console.log('='.repeat(50));
    console.log(`  Server running at: http://localhost:${PORT}`);
    console.log(`  API test endpoint: http://localhost:${PORT}/api/test`);
    console.log(`  Scripts path: ${SCRIPTS_PATH}`);
    console.log('='.repeat(50));
    console.log('');
    const timestamp = new Date().toISOString();
    console.log(`${timestamp} [INFO] Server started successfully`);
  });

  server.on('error', (err) => {
    if (err.code === 'EADDRINUSE') {
      console.log(`Port ${port} is in use, trying ${port + 1}...`);
      startServer(port + 1);
    } else {
      console.error('Server error:', err);
      process.exit(1);
    }
  });
}

// Start with default port, will auto-increment if busy
startServer(DEFAULT_PORT);
