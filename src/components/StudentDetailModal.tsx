/**
 * StudentDetailModal Component
 * Shows detailed assignment history for a specific student
 */

import React from 'react';

interface StudentDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  studentName: string;
  assignments: {
    [assignmentName: string]: {
      submitted: boolean;
      date: string;
    };
  };
  notes: string;
  onNotesChange: (notes: string) => void;
  isDark: boolean;
  metalButtonClass: (isDark: boolean) => string;
  metalButtonStyle: (isDark: boolean) => React.CSSProperties | undefined;
}

export default function StudentDetailModal({
  isOpen,
  onClose,
  studentName,
  assignments,
  notes,
  onNotesChange,
  isDark,
  metalButtonClass,
  metalButtonStyle,
}: StudentDetailModalProps) {
  const [editedNotes, setEditedNotes] = React.useState(notes);

  React.useEffect(() => {
    setEditedNotes(notes);
  }, [notes]);

  if (!isOpen) return null;

  const handleSave = () => {
    onNotesChange(editedNotes);
    onClose();
  };

  // Sort assignments by date (most recent first)
  const sortedAssignments = Object.entries(assignments).sort((a, b) => {
    const dateA = new Date(a[1].date);
    const dateB = new Date(b[1].date);
    return dateB.getTime() - dateA.getTime();
  });

  const submittedCount = sortedAssignments.filter(([, data]) => data.submitted).length;
  const notSubmittedCount = sortedAssignments.filter(([, data]) => !data.submitted).length;

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
      }}
      onClick={onClose}
    >
      <div
        style={{
          backgroundColor: isDark ? '#2d2d2d' : 'white',
          borderRadius: '8px',
          padding: '24px',
          maxWidth: '600px',
          width: '90%',
          maxHeight: '80vh',
          overflow: 'auto',
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div style={{ marginBottom: '20px' }}>
          <h2
            style={{
              margin: '0 0 8px 0',
              fontSize: '24px',
              color: isDark ? '#e0e0e0' : '#333',
            }}
          >
            {studentName}
          </h2>
          <div
            style={{
              fontSize: '14px',
              color: isDark ? '#b0b0b0' : '#666',
            }}
          >
            <span style={{ marginRight: '16px' }}>
              ✅ Submitted: <strong>{submittedCount}</strong>
            </span>
            <span>
              ❌ Not Submitted: <strong>{notSubmittedCount}</strong>
            </span>
          </div>
        </div>

        {/* Assignment History */}
        <div style={{ marginBottom: '20px' }}>
          <h3
            style={{
              margin: '0 0 12px 0',
              fontSize: '16px',
              color: isDark ? '#e0e0e0' : '#333',
              borderBottom: `1px solid ${isDark ? '#444' : '#ddd'}`,
              paddingBottom: '8px',
            }}
          >
            Assignment History
          </h3>
          {sortedAssignments.length === 0 ? (
            <p
              style={{
                color: isDark ? '#999' : '#666',
                fontStyle: 'italic',
                margin: '12px 0',
              }}
            >
              No assignment history recorded yet.
            </p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {sortedAssignments.map(([assignmentName, data]) => (
                <div
                  key={assignmentName}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    padding: '8px 12px',
                    backgroundColor: isDark ? '#3a3a3a' : '#f5f5f5',
                    borderRadius: '4px',
                    borderLeft: `4px solid ${data.submitted ? '#4CAF50' : '#f44336'}`,
                  }}
                >
                  <span style={{ fontSize: '18px', marginRight: '12px' }}>
                    {data.submitted ? '✅' : '❌'}
                  </span>
                  <div style={{ flex: 1 }}>
                    <div
                      style={{
                        fontWeight: '500',
                        color: isDark ? '#e0e0e0' : '#333',
                        marginBottom: '2px',
                      }}
                    >
                      {assignmentName}
                    </div>
                    <div
                      style={{
                        fontSize: '12px',
                        color: isDark ? '#999' : '#666',
                      }}
                    >
                      {new Date(data.date).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'short',
                        day: 'numeric',
                      })}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Notes Section */}
        <div style={{ marginBottom: '20px' }}>
          <h3
            style={{
              margin: '0 0 8px 0',
              fontSize: '16px',
              color: isDark ? '#e0e0e0' : '#333',
              borderBottom: `1px solid ${isDark ? '#444' : '#ddd'}`,
              paddingBottom: '8px',
            }}
          >
            Notes
          </h3>
          <textarea
            value={editedNotes}
            onChange={(e) => setEditedNotes(e.target.value)}
            placeholder="Add notes about this student..."
            style={{
              width: '100%',
              minHeight: '100px',
              padding: '8px',
              borderRadius: '4px',
              border: `1px solid ${isDark ? '#555' : '#ddd'}`,
              backgroundColor: isDark ? '#3a3a3a' : 'white',
              color: isDark ? '#e0e0e0' : '#333',
              fontFamily: 'inherit',
              fontSize: '14px',
              resize: 'vertical',
            }}
          />
        </div>

        {/* Buttons */}
        <div
          style={{
            display: 'flex',
            justifyContent: 'flex-end',
            gap: '8px',
          }}
        >
          <button
            onClick={onClose}
            className={metalButtonClass(isDark)}
            style={{
              ...metalButtonStyle(isDark),
              padding: '8px 16px',
              fontSize: '14px',
            }}
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className={metalButtonClass(isDark)}
            style={{
              ...metalButtonStyle(isDark),
              padding: '8px 16px',
              fontSize: '14px',
              background: isDark
                ? 'linear-gradient(145deg, #4a4a4a, #3a3a3a)'
                : 'linear-gradient(145deg, #e8e8e8, #d0d0d0)',
            }}
          >
            Save Notes
          </button>
        </div>
      </div>
    </div>
  );
}
