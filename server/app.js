/**
 * Express application setup
 * Creates app, applies middleware, mounts all route modules
 */

const express = require('express');
const cors = require('cors');
const os = require('os');
const multer = require('multer');

const { SCRIPTS_PATH } = require('./config');

// Route modules
const systemRoutes = require('./routes/system');
const quizRoutes = require('./routes/quiz');
const classesRoutes = require('./routes/classes');
const patchesRoutes = require('./routes/patches');
const filesRoutes = require('./routes/files');

const app = express();

// Configure multer for file uploads
const upload = multer({
  dest: os.tmpdir(), // Store in system temp directory
  limits: {
    fileSize: 1000 * 1024 * 1024 // 1GB max file size (for very large combined PDFs)
  },
  fileFilter: (req, file, cb) => {
    // Only accept PDF files
    if (file.mimetype === 'application/pdf' || file.originalname.toLowerCase().endsWith('.pdf')) {
      cb(null, true);
    } else {
      cb(new Error('Only PDF files are allowed'));
    }
  }
});

// Middleware
app.use(cors());
app.use(express.json({ limit: '500mb' })); // Increase JSON body size limit
app.use(express.urlencoded({ extended: true, limit: '500mb' })); // Increase URL-encoded body size limit

// Multer error handling middleware for split-pdf-upload
const handleUpload = (req, res, next) => {
  upload.single('pdf')(req, res, (err) => {
    if (err) {
      if (err.code === 'LIMIT_FILE_SIZE') {
        return res.json({
          success: false,
          logs: [],
          error: `File too large. Maximum size is 1GB. Your file appears to exceed this limit.`
        });
      }
      return res.json({
        success: false,
        logs: [],
        error: `File upload error: ${err.message}`
      });
    }
    next();
  });
};

// Apply multer middleware to specific routes before mounting
app.post('/api/quiz/split-pdf-upload', handleUpload);
app.post('/api/patches/import', upload.single('patchFile'));

// Mount routes
app.use('/api', systemRoutes);
app.use('/api/quiz', quizRoutes);
app.use('/api/classes', classesRoutes);
app.use('/api/patches', patchesRoutes);
app.use('/api', filesRoutes);

module.exports = { app, SCRIPTS_PATH };
