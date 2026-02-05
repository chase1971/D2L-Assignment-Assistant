/**
 * Server-Sent Events (SSE) Logger Module
 * Handles real-time log streaming from Python scripts to frontend
 */

// Track all connected SSE clients
const sseClients = new Set();

/**
 * SSE endpoint handler - establishes streaming connection
 */
function handleSseConnection(req, res) {
  // Set SSE headers
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');
  res.setHeader('X-Accel-Buffering', 'no'); // Disable nginx buffering
  
  // Send initial connection message
  res.write('data: {"type":"connected","timestamp":' + Date.now() + '}\n\n');
  
  // Add client to set
  const clientId = Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  const client = { id: clientId, res };
  sseClients.add(client);
  
  console.log(`[SSE] Client connected: ${clientId} (${sseClients.size} total)`);
  
  // Remove client on disconnect
  req.on('close', () => {
    sseClients.delete(client);
    console.log(`[SSE] Client disconnected: ${clientId} (${sseClients.size} remaining)`);
  });
}

/**
 * Broadcast log message to all connected SSE clients
 */
function broadcastLog(logData) {
  if (sseClients.size === 0) {
    return; // No clients connected, skip broadcasting
  }
  
  const data = JSON.stringify(logData);
  const deadClients = [];
  
  sseClients.forEach(client => {
    try {
      client.res.write(`data: ${data}\n\n`);
    } catch (error) {
      // Client connection broken, mark for removal
      console.error(`[SSE] Failed to send to client ${client.id}:`, error.message);
      deadClients.push(client);
    }
  });
  
  // Clean up dead clients
  deadClients.forEach(client => sseClients.delete(client));
}

/**
 * Parse and broadcast a log line from Python stdout
 */
function parseAndBroadcastLogLine(line) {
  const trimmed = line.trim();
  if (!trimmed) return;
  
  // Parse log level and message
  let level = 'INFO';
  let message = trimmed;
  
  // New format: [LOG:LEVEL] message
  const logMatch = trimmed.match(/^\[LOG:(SUCCESS|ERROR|WARNING|INFO)\] (.+)$/);
  if (logMatch) {
    level = logMatch[1];
    message = logMatch[2];
  } 
  // Legacy format: [USER] message
  else if (trimmed.startsWith('[USER]')) {
    message = trimmed.substring(7);
  } 
  // Skip developer logs
  else if (trimmed.startsWith('[DEV]')) {
    return;
  }
  // Skip JSON responses (they're handled separately)
  else if (trimmed.startsWith('{') && (trimmed.includes('"success"') || trimmed.includes('"confidenceScores"'))) {
    return;
  }
  
  // Broadcast to SSE clients
  broadcastLog({
    type: 'log',
    level: level,
    message: message,
    timestamp: Date.now()
  });
}

/**
 * Broadcast process start event
 */
function broadcastProcessStart(endpoint, data = {}) {
  broadcastLog({
    type: 'process-started',
    endpoint: endpoint,
    timestamp: Date.now(),
    ...data
  });
}

/**
 * Broadcast process completion event
 */
function broadcastProcessComplete(endpoint, success, data = {}) {
  broadcastLog({
    type: 'process-complete',
    endpoint: endpoint,
    success: success,
    timestamp: Date.now(),
    ...data
  });
}

/**
 * Get count of connected SSE clients
 */
function getClientCount() {
  return sseClients.size;
}

module.exports = {
  handleSseConnection,
  broadcastLog,
  parseAndBroadcastLogLine,
  broadcastProcessStart,
  broadcastProcessComplete,
  getClientCount
};
