/**
 * Standard API response helper
 * Used by all route files for consistent response format
 */

function apiResponse(res, { success, logs = [], error = null, ...extra }) {
  res.json({ success, logs, error: success ? null : error, ...extra });
}

module.exports = { apiResponse };
