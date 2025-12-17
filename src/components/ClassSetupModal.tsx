import React, { useState } from 'react';
import { X, Edit2, Trash2, AlertTriangle, FolderOpen } from 'lucide-react';
import ClassSetupWizard from './ClassSetupWizard';
import { ClassData, deleteClass, deleteAllClasses, editClass, selectFolder } from '../services/quizGraderService';

interface ClassSetupModalProps {
  isOpen: boolean;
  onClose: () => void;
  classes: ClassData[];
  onClassesUpdated: () => void;
  isDark: boolean;
  metalButtonClass: (isDark: boolean) => string;
  metalButtonStyle: (isDark: boolean) => React.CSSProperties | undefined;
}

type View = 'management' | 'wizard' | 'confirm-delete' | 'confirm-new-semester';

export default function ClassSetupModal({
  isOpen,
  onClose,
  classes,
  onClassesUpdated,
  isDark,
  metalButtonClass,
  metalButtonStyle,
}: ClassSetupModalProps) {
  const [view, setView] = useState<View>('management');
  const [editingClassId, setEditingClassId] = useState<string | null>(null);
  const [editForm, setEditForm] = useState({ value: '', label: '', rosterFolderPath: '' });
  const [classToDelete, setClassToDelete] = useState<ClassData | null>(null);
  const [error, setError] = useState<string>('');
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleClose = () => {
    setView('management');
    setEditingClassId(null);
    setClassToDelete(null);
    setError('');
    onClose();
  };

  const handleEdit = (cls: ClassData) => {
    setEditingClassId(cls.id);
    setEditForm({
      value: cls.value,
      label: cls.label,
      rosterFolderPath: cls.rosterFolderPath,
    });
  };

  const handleCancelEdit = () => {
    setEditingClassId(null);
    setEditForm({ value: '', label: '', rosterFolderPath: '' });
  };

  const handleBrowseFolderEdit = async () => {
    try {
      const result = await selectFolder();
      
      if (result.success && result.folderPath) {
        setEditForm({
          ...editForm,
          rosterFolderPath: result.folderPath,
        });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to select folder');
    }
  };

  const handleSaveEdit = async (classId: string) => {
    setLoading(true);
    setError('');
    
    try {
      const result = await editClass(classId, editForm);
      
      if (result.success) {
        setEditingClassId(null);
        setEditForm({ value: '', label: '', rosterFolderPath: '' });
        onClassesUpdated();
      } else {
        setError(result.error || 'Failed to edit class');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to edit class');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteClick = (cls: ClassData) => {
    setClassToDelete(cls);
    setView('confirm-delete');
  };

  const handleConfirmDelete = async () => {
    if (!classToDelete) return;
    
    setLoading(true);
    setError('');
    
    try {
      const result = await deleteClass(classToDelete.id);
      
      if (result.success) {
        setClassToDelete(null);
        setView('management');
        onClassesUpdated();
      } else {
        setError(result.error || 'Failed to delete class');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete class');
    } finally {
      setLoading(false);
    }
  };

  const handleNewSemesterClick = () => {
    // If there are no non-protected classes, skip confirmation and go straight to wizard
    if (nonProtectedClasses.length === 0) {
      setView('wizard');
    } else {
      setView('confirm-new-semester');
    }
  };

  const handleConfirmNewSemester = async () => {
    setLoading(true);
    setError('');
    
    try {
      const result = await deleteAllClasses();
      
      if (result.success) {
        setView('wizard');
        onClassesUpdated();
      } else {
        setError(result.error || 'Failed to delete classes');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete classes');
    } finally {
      setLoading(false);
    }
  };

  const handleWizardComplete = async () => {
    try {
      await onClassesUpdated(); // Refresh dropdown
      handleClose(); // Close modal
    } catch (err) {
      console.error('Error refreshing classes:', err);
      handleClose(); // Still close on error
    }
  };

  const nonProtectedClasses = classes.filter(cls => !cls.isProtected);

  return (
    <div 
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        width: '100vw',
        height: '100vh',
        backgroundColor: 'rgba(0, 0, 0, 0.7)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 999999,
      }}
      onClick={(e) => {
        if (e.target === e.currentTarget) {
          handleClose();
        }
      }}
    >
      <div 
        style={{
          width: view === 'management' ? '800px' : view === 'wizard' ? '600px' : '500px',
          maxWidth: '95vw',
          maxHeight: '85vh',
          backgroundColor: isDark ? '#1a2942' : '#d0d0d4',
          borderRadius: '12px',
          border: isDark ? '2px solid #3a4962' : '2px solid #888',
          boxShadow: '0 25px 60px rgba(0, 0, 0, 0.5)',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div 
          style={{
            padding: '16px 20px',
            backgroundColor: isDark ? '#0f1729' : '#c0c0c4',
            borderBottom: isDark ? '2px solid #3a4962' : '2px solid #999',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexShrink: 0,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <h2 
              style={{
                fontSize: '20px',
                fontWeight: 'bold',
                color: isDark ? '#22d3ee' : '#1a2942',
                margin: 0,
              }}
            >
              {view === 'wizard' ? 'New Semester Setup' : view === 'confirm-delete' ? 'Delete Class' : view === 'confirm-new-semester' ? 'Start New Semester' : 'Class Setup'}
            </h2>
          </div>
          <button
            onClick={handleClose}
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              padding: '4px',
              display: 'flex',
              alignItems: 'center',
              color: isDark ? '#9ca3af' : '#4b5563',
            }}
          >
            <X size={24} />
          </button>
        </div>

        {/* Content */}
        <div 
          style={{
            padding: '20px',
            overflowY: 'auto',
            flex: 1,
            color: isDark ? '#d1d5db' : '#1f2937',
          }}
        >
          {error && (
            <div 
              style={{
                marginBottom: '16px',
                padding: '12px',
                backgroundColor: 'rgba(239, 68, 68, 0.1)',
                border: '1px solid #ef4444',
                borderRadius: '8px',
                color: '#ef4444',
                fontSize: '14px',
              }}
            >
              {error}
            </div>
          )}

          {/* Management View */}
          {view === 'management' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
              {/* Current Classes List */}
              <div>
                <h3 
                  style={{
                    fontSize: '18px',
                    fontWeight: '600',
                    marginBottom: '16px',
                    color: isDark ? '#d1d5db' : '#1f2937',
                  }}
                >
                  Current Classes
                </h3>
                
                {classes.length === 0 ? (
                  <p 
                    style={{
                      textAlign: 'center',
                      padding: '32px 0',
                      color: isDark ? '#6b7280' : '#4b5563',
                    }}
                  >
                    No classes configured. Click "Start New Semester" to add classes.
                  </p>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    {classes.map((cls) => (
                      <div
                        key={cls.id}
                        style={{
                          padding: '16px',
                          borderRadius: '8px',
                          border: isDark ? '1px solid #2a3952' : '1px solid #d1d5db',
                          backgroundColor: isDark ? '#0f1729' : '#f9fafb',
                        }}
                      >
                        {editingClassId === cls.id ? (
                          // Edit Mode
                          <div className="space-y-3">
                            <div>
                              <label className={`block text-xs font-medium mb-1 ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                                Roster Folder Path
                              </label>
                              <div className="flex gap-2">
                                <input
                                  type="text"
                                  value={editForm.rosterFolderPath}
                                  onChange={(e) => setEditForm({ ...editForm, rosterFolderPath: e.target.value })}
                                  className={`flex-1 px-3 py-2 rounded border text-sm ${
                                    isDark
                                      ? 'bg-[#0f1729] border-[#2a3952] text-gray-300'
                                      : 'bg-white border-gray-400 text-gray-800'
                                  }`}
                                />
                                <button
                                  onClick={handleBrowseFolderEdit}
                                  className={`px-3 py-2 rounded border text-sm ${metalButtonClass(isDark)}`}
                                  style={metalButtonStyle(isDark)}
                                >
                                  <FolderOpen size={14} />
                                </button>
                              </div>
                            </div>
                            <div className="grid grid-cols-2 gap-3">
                              <div>
                                <label className={`block text-xs font-medium mb-1 ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                                  Class Name (Display)
                                </label>
                                <input
                                  type="text"
                                  value={editForm.label}
                                  onChange={(e) => setEditForm({ ...editForm, label: e.target.value })}
                                  className={`w-full px-3 py-2 rounded border text-sm ${
                                    isDark
                                      ? 'bg-[#0f1729] border-[#2a3952] text-gray-300'
                                      : 'bg-white border-gray-400 text-gray-800'
                                  }`}
                                />
                              </div>
                              <div>
                                <label className={`block text-xs font-medium mb-1 ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                                  Class Value (Internal)
                                </label>
                                <input
                                  type="text"
                                  value={editForm.value}
                                  onChange={(e) => setEditForm({ ...editForm, value: e.target.value })}
                                  className={`w-full px-3 py-2 rounded border text-sm ${
                                    isDark
                                      ? 'bg-[#0f1729] border-[#2a3952] text-gray-300'
                                      : 'bg-white border-gray-400 text-gray-800'
                                  }`}
                                />
                              </div>
                            </div>
                            <div className="flex gap-2 justify-end">
                              <button
                                onClick={handleCancelEdit}
                                className={`px-4 py-2 rounded border text-sm ${metalButtonClass(isDark)}`}
                                style={metalButtonStyle(isDark)}
                                disabled={loading}
                              >
                                Cancel
                              </button>
                              <button
                                onClick={() => handleSaveEdit(cls.id)}
                                className={`px-4 py-2 rounded border text-sm ${metalButtonClass(isDark)}`}
                                style={metalButtonStyle(isDark)}
                                disabled={loading}
                              >
                                {loading ? 'Saving...' : 'Save'}
                              </button>
                            </div>
                          </div>
                        ) : (
                          // Display Mode
                          <div className="flex items-center justify-between">
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-1">
                                <h4 className={`font-semibold ${isDark ? 'text-gray-200' : 'text-gray-800'}`}>
                                  {cls.label}
                                </h4>
                                {cls.isProtected && (
                                  <span className="px-2 py-0.5 text-xs rounded bg-yellow-500 bg-opacity-20 text-yellow-500 border border-yellow-500">
                                    Protected
                                  </span>
                                )}
                              </div>
                              <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                                {cls.value}
                              </p>
                              {cls.rosterFolderPath && (
                                <p className={`text-xs mt-1 ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>
                                  📁 {cls.rosterFolderPath}
                                </p>
                              )}
                            </div>
                            <div className="flex gap-2">
                              <button
                                onClick={() => handleEdit(cls)}
                                className={`p-2 rounded border ${metalButtonClass(isDark)}`}
                                style={metalButtonStyle(isDark)}
                                title="Edit"
                              >
                                <Edit2 size={16} />
                              </button>
                              {!cls.isProtected && (
                                <button
                                  onClick={() => handleDeleteClick(cls)}
                                  className={`p-2 rounded border ${metalButtonClass(isDark)}`}
                                  style={metalButtonStyle(isDark)}
                                  title="Delete"
                                >
                                  <Trash2 size={16} />
                                </button>
                              )}
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Actions */}
              <div className="flex gap-3 justify-between pt-4 border-t border-gray-300">
                <button
                  onClick={handleNewSemesterClick}
                  className={`px-6 py-3 rounded-lg border ${metalButtonClass(isDark)} font-medium`}
                  style={metalButtonStyle(isDark)}
                  disabled={loading}
                >
                  Start New Semester
                </button>
                <button
                  onClick={handleClose}
                  className={`px-6 py-3 rounded-lg border ${metalButtonClass(isDark)} font-medium`}
                  style={metalButtonStyle(isDark)}
                >
                  Close
                </button>
              </div>
            </div>
          )}

          {/* Wizard View */}
          {view === 'wizard' && (
            <ClassSetupWizard
              isDark={isDark}
              onComplete={handleWizardComplete}
              onCancel={() => setView('management')}
              metalButtonClass={metalButtonClass}
              metalButtonStyle={metalButtonStyle}
              initialClasses={classes}
            />
          )}

          {/* Confirm Delete */}
          {view === 'confirm-delete' && classToDelete && (
            <div className="space-y-6">
              <div className="flex items-start gap-4">
                <AlertTriangle size={48} className="text-yellow-500 flex-shrink-0" />
                <div>
                  <h3 className={`text-lg font-semibold mb-2 ${isDark ? 'text-gray-200' : 'text-gray-800'}`}>
                    Delete Class?
                  </h3>
                  <p className={`mb-4 ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                    Are you sure you want to delete <strong>{classToDelete.label}</strong>?
                  </p>
                  <p className={`text-sm ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>
                    This action cannot be undone.
                  </p>
                </div>
              </div>
              
              <div className="flex gap-3 justify-end">
                <button
                  onClick={() => setView('management')}
                  className={`px-6 py-2 rounded-lg border ${metalButtonClass(isDark)}`}
                  style={metalButtonStyle(isDark)}
                  disabled={loading}
                >
                  Cancel
                </button>
                <button
                  onClick={handleConfirmDelete}
                  className={`px-6 py-2 rounded-lg border shadow-lg font-bold text-white`}
                  style={{
                    backgroundColor: isDark ? '#dc2626' : '#ef4444',
                    borderColor: isDark ? '#b91c1c' : '#dc2626',
                  }}
                  disabled={loading}
                >
                  {loading ? 'Deleting...' : 'Delete Class'}
                </button>
              </div>
            </div>
          )}

          {/* Confirm New Semester */}
          {view === 'confirm-new-semester' && (
            <div className="space-y-6">
              <div className="flex items-start gap-4">
                <AlertTriangle size={48} className="text-yellow-500 flex-shrink-0" />
                <div>
                  <h3 className={`text-lg font-semibold mb-2 ${isDark ? 'text-gray-200' : 'text-gray-800'}`}>
                    Start New Semester?
                  </h3>
                  <p className={`mb-4 ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                    This will delete all non-protected classes ({nonProtectedClasses.length} {nonProtectedClasses.length === 1 ? 'class' : 'classes'}).
                  </p>
                  <p className={`text-sm ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>
                    Protected classes will be preserved. You'll then set up your new classes.
                  </p>
                </div>
              </div>
              
              <div className="flex gap-3 justify-end">
                <button
                  onClick={() => setView('management')}
                  className={`px-6 py-2 rounded-lg border ${metalButtonClass(isDark)}`}
                  style={metalButtonStyle(isDark)}
                  disabled={loading}
                >
                  Cancel
                </button>
                <button
                  onClick={handleConfirmNewSemester}
                  className={`px-6 py-2 rounded-lg border shadow-lg font-bold text-white`}
                  style={{
                    backgroundColor: isDark ? '#dc2626' : '#ef4444',
                    borderColor: isDark ? '#b91c1c' : '#dc2626',
                  }}
                  disabled={loading}
                >
                  {loading ? 'Processing...' : 'Continue'}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

