import { useState, useEffect } from 'react';
import { getPatchStatus, selectAndImportPatch, clearPatches, reloadWindow, type PatchStatus } from '../services/quizGraderService';

interface PatchManagerProps {
  isDark: boolean;
  onClose: () => void;
  addLog: (message: string) => void;
}

export default function PatchManager({ isDark, onClose, addLog }: PatchManagerProps) {
  const [patchStatus, setPatchStatus] = useState<PatchStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [importing, setImporting] = useState(false);
  const [clearing, setClearing] = useState(false);

  useEffect(() => {
    loadPatchStatus();
  }, []);

  const loadPatchStatus = async () => {
    setLoading(true);
    try {
      const status = await getPatchStatus();
      setPatchStatus(status);
    } catch (error) {
      console.error('Failed to load patch status:', error);
      addLog('❌ Failed to load patch status');
    } finally {
      setLoading(false);
    }
  };

  const handleImportPatch = async () => {
    setImporting(true);
    try {
      const result = await selectAndImportPatch(addLog);
      if (result.success) {
        addLog(`✅ ${result.message}`);
        await loadPatchStatus();
        
        // Show restart prompt
        if (window.confirm('Patch imported successfully! Restart the app to apply changes?')) {
          reloadWindow();
        }
      } else {
        addLog(`❌ ${result.error || 'Failed to import patch'}`);
      }
    } catch (error) {
      console.error('Import failed:', error);
      addLog('❌ Failed to import patch');
    } finally {
      setImporting(false);
    }
  };

  const handleClearPatches = async () => {
    if (!window.confirm('Are you sure you want to remove all patches and restore bundled versions?')) {
      return;
    }

    setClearing(true);
    try {
      const result = await clearPatches(addLog);
      if (result.success) {
        addLog(`✅ ${result.message}`);
        await loadPatchStatus();
        
        // Show restart prompt
        if (window.confirm('Patches cleared! Restart the app to use bundled versions?')) {
          reloadWindow();
        }
      } else {
        addLog(`❌ ${result.error || 'Failed to clear patches'}`);
      }
    } catch (error) {
      console.error('Clear failed:', error);
      addLog('❌ Failed to clear patches');
    } finally {
      setClearing(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div 
        className={`w-full max-w-2xl max-h-[80vh] overflow-auto rounded-lg shadow-2xl border-2 ${
          isDark 
            ? 'bg-[#0f1419] border-[#2a3952]' 
            : 'bg-white border-[#c0c6d0]'
        }`}
      >
        {/* Header */}
        <div className={`sticky top-0 px-6 py-4 border-b ${
          isDark ? 'bg-[#1a2942] border-[#2a3952]' : 'bg-[#f0f2f5] border-[#c0c6d0]'
        }`}>
          <div className="flex items-center justify-between">
            <h2 className={`text-xl font-bold ${isDark ? 'text-white' : 'text-[#2c3e50]'}`}>
              🔧 Patch Manager
            </h2>
            <button
              onClick={onClose}
              className={`px-3 py-1 rounded transition-colors ${
                isDark
                  ? 'bg-[#2a3952] hover:bg-[#3a4962] text-gray-300'
                  : 'bg-[#e0e4e8] hover:bg-[#d0d4d8] text-[#2c3e50]'
              }`}
            >
              Close
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Info Section */}
          <div className={`p-4 rounded-lg border ${
            isDark ? 'bg-[#1a2942] border-[#2a3952]' : 'bg-[#f8f9fa] border-[#e0e4e8]'
          }`}>
            <h3 className={`text-lg font-semibold mb-2 ${isDark ? 'text-white' : 'text-[#2c3e50]'}`}>
              What are patches?
            </h3>
            <p className={`text-sm ${isDark ? 'text-gray-300' : 'text-gray-600'}`}>
              Patches allow you to update the app without reinstalling. When you receive a patch file (.zip) 
              from your administrator, import it here to apply bug fixes and improvements.
            </p>
          </div>

          {/* Status */}
          {loading ? (
            <div className="text-center py-8">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-500 border-t-transparent"></div>
              <p className={`mt-2 ${isDark ? 'text-gray-300' : 'text-gray-600'}`}>
                Loading patch status...
              </p>
            </div>
          ) : patchStatus ? (
            <>
              {/* Current Status */}
              <div className={`p-4 rounded-lg border ${
                isDark ? 'bg-[#1a2942] border-[#2a3952]' : 'bg-[#f8f9fa] border-[#e0e4e8]'
              }`}>
                <div className="flex items-center justify-between mb-3">
                  <h3 className={`text-lg font-semibold ${isDark ? 'text-white' : 'text-[#2c3e50]'}`}>
                    Current Status
                  </h3>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                    patchStatus.hasPatch
                      ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                      : 'bg-gray-500/20 text-gray-400 border border-gray-500/30'
                  }`}>
                    {patchStatus.hasPatch ? '✓ Patched' : '○ No Patches'}
                  </span>
                </div>

                {patchStatus.hasPatch && (
                  <>
                    <div className={`space-y-2 ${isDark ? 'text-gray-300' : 'text-gray-600'}`}>
                      <div className="flex justify-between text-sm">
                        <span>Files patched:</span>
                        <span className="font-semibold">{patchStatus.patchedFilesCount}</span>
                      </div>
                      
                      {patchStatus.patchInfo?.version && (
                        <div className="flex justify-between text-sm">
                          <span>Patch version:</span>
                          <span className="font-semibold">{patchStatus.patchInfo.version}</span>
                        </div>
                      )}
                      
                      {patchStatus.patchInfo?.description && (
                        <div className="text-sm">
                          <span>Description:</span>
                          <p className="mt-1 font-semibold">{patchStatus.patchInfo.description}</p>
                        </div>
                      )}
                      
                      {patchStatus.patchInfo?.lastImported && (
                        <div className="flex justify-between text-sm">
                          <span>Last imported:</span>
                          <span className="font-semibold">
                            {new Date(patchStatus.patchInfo.lastImported).toLocaleString()}
                          </span>
                        </div>
                      )}
                    </div>

                    {/* Patched Files List */}
                    {patchStatus.patchedFiles.length > 0 && (
                      <details className="mt-4">
                        <summary className={`cursor-pointer text-sm font-medium ${
                          isDark ? 'text-blue-400' : 'text-blue-600'
                        }`}>
                          View patched files ({patchStatus.patchedFiles.length})
                        </summary>
                        <div className={`mt-2 p-3 rounded text-xs font-mono max-h-48 overflow-auto ${
                          isDark ? 'bg-[#0f1419] text-gray-400' : 'bg-gray-100 text-gray-700'
                        }`}>
                          {patchStatus.patchedFiles.map((file, idx) => (
                            <div key={idx}>{file}</div>
                          ))}
                        </div>
                      </details>
                    )}
                  </>
                )}
              </div>

              {/* Actions */}
              <div className="space-y-3">
                <button
                  onClick={handleImportPatch}
                  disabled={importing}
                  className={`w-full px-4 py-3 rounded-lg font-medium transition-colors ${
                    importing
                      ? 'bg-gray-500 cursor-not-allowed'
                      : isDark
                      ? 'bg-blue-600 hover:bg-blue-700 text-white'
                      : 'bg-blue-500 hover:bg-blue-600 text-white'
                  }`}
                >
                  {importing ? 'Importing...' : '📥 Import Patch File'}
                </button>

                {patchStatus.hasPatch && (
                  <button
                    onClick={handleClearPatches}
                    disabled={clearing}
                    className={`w-full px-4 py-3 rounded-lg font-medium transition-colors ${
                      clearing
                        ? 'bg-gray-500 cursor-not-allowed'
                        : isDark
                        ? 'bg-red-600 hover:bg-red-700 text-white'
                        : 'bg-red-500 hover:bg-red-600 text-white'
                    }`}
                  >
                    {clearing ? 'Clearing...' : '🗑️ Clear All Patches'}
                  </button>
                )}
              </div>

              {/* Patch Directory Info */}
              <div className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>
                <p>Patch directory: {patchStatus.patchDirectory}</p>
              </div>
            </>
          ) : (
            <div className={`text-center py-8 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
              Failed to load patch status
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
