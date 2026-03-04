/**
 * StudentStatisticsModal Component
 * Main modal for viewing and managing student submission statistics
 */

import React, { useState, useEffect } from 'react';
import StudentDetailModal from './StudentDetailModal';
import { StudentStatistics } from '../services/statisticsService';

interface StudentStatisticsModalProps {
  isOpen: boolean;
  onClose: () => void;
  students: StudentStatistics[];
  onUpdateNotes: (studentName: string, notes: string) => void;
  onUpdateCount: (studentName: string, count: number) => void;
  onUpdateLateCount: (studentName: string, count: number) => void;
  onRefresh: () => void;
  isDark: boolean;
  metalButtonClass: (isDark: boolean) => string;
  metalButtonStyle: (isDark: boolean) => React.CSSProperties | undefined;
}

export default function StudentStatisticsModal({
  isOpen,
  onClose,
  students,
  onUpdateNotes,
  onUpdateCount,
  onUpdateLateCount,
  onRefresh,
  isDark,
  metalButtonClass,
  metalButtonStyle,
}: StudentStatisticsModalProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedStudent, setSelectedStudent] = useState<StudentStatistics | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [editingCount, setEditingCount] = useState<string | null>(null);
  const [tempCount, setTempCount] = useState<string>('');

  if (!isOpen) return null;

  // Filter students based on search term
  const filteredStudents = students.filter((student) =>
    student.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Calculate totals
  const totalFailures = students.reduce((sum, s) => sum + s.failed_submissions, 0);
  const studentsWithFailures = students.filter((s) => s.failed_submissions > 0).length;

  const handleStudentClick = (student: StudentStatistics) => {
    setSelectedStudent(student);
    setShowDetailModal(true);
  };

  const handleNotesChange = (notes: string) => {
    if (selectedStudent) {
      onUpdateNotes(selectedStudent.name, notes);
      // Update local state
      setSelectedStudent({ ...selectedStudent, notes });
    }
  };

  const handleStartEditCount = (student: StudentStatistics, e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingCount(student.name);
    setTempCount(student.failed_submissions.toString());
  };

  const handleSaveCount = (studentName: string) => {
    const newCount = parseInt(tempCount, 10);
    if (!isNaN(newCount) && newCount >= 0) {
      onUpdateCount(studentName, newCount);
    }
    setEditingCount(null);
  };

  const handleCancelEdit = () => {
    setEditingCount(null);
    setTempCount('');
  };

  const handleKeyDown = (e: React.KeyboardEvent, studentName: string) => {
    if (e.key === 'Enter') {
      handleSaveCount(studentName);
    } else if (e.key === 'Escape') {
      handleCancelEdit();
    }
  };

  return (
    <>
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
            padding: '12px 16px',
            maxWidth: '900px',
            width: '90%',
            maxHeight: '90vh',
            display: 'flex',
            flexDirection: 'column',
            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
          }}
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div style={{ marginBottom: '10px' }}>
            <h2
              style={{
                margin: '0 0 4px 0',
                fontSize: '18px',
                color: isDark ? '#e0e0e0' : '#333',
              }}
            >
              📊 Student Statistics
            </h2>
            <div
              style={{
                fontSize: '12px',
                color: isDark ? '#b0b0b0' : '#666',
                marginBottom: '8px',
              }}
            >
              <span style={{ marginRight: '12px' }}>
                Total: <strong>{students.length}</strong>
              </span>
              <span style={{ marginRight: '12px' }}>
                With Failures: <strong>{studentsWithFailures}</strong>
              </span>
              <span>
                Total Failures: <strong>{totalFailures}</strong>
              </span>
            </div>

            {/* Search Bar */}
            <input
              type="text"
              placeholder="Search students..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{
                width: '100%',
                padding: '6px 10px',
                borderRadius: '4px',
                border: `1px solid ${isDark ? '#555' : '#ddd'}`,
                backgroundColor: isDark ? '#3a3a3a' : 'white',
                color: isDark ? '#e0e0e0' : '#333',
                fontSize: '13px',
              }}
            />
          </div>

          {/* Student List - two columns */}
          <div
            style={{
              flex: 1,
              minHeight: 0,
              overflow: 'auto',
              marginBottom: '10px',
            }}
          >
            {filteredStudents.length === 0 ? (
              <div
                style={{
                  textAlign: 'center',
                  padding: '24px 16px',
                  color: isDark ? '#999' : '#666',
                  fontSize: '13px',
                }}
              >
                {students.length === 0 ? (
                  <>
                    <p style={{ margin: '0 0 4px 0' }}>📋 No statistics yet</p>
                    <p style={{ margin: 0, fontSize: '12px' }}>
                      Recorded when you process quizzes and completions.
                    </p>
                  </>
                ) : (
                  <p style={{ margin: 0 }}>No students match your search.</p>
                )}
              </div>
            ) : (
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: '1fr 1fr',
                  gap: '6px 12px',
                }}
              >
                {filteredStudents.map((student) => {
                  const assignmentCount = Object.keys(student.assignments).length;
                  const isEditing = editingCount === student.name;

                  return (
                    <div
                      key={student.name}
                      onClick={() => !isEditing && handleStudentClick(student)}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        padding: '6px 10px',
                        backgroundColor: isDark ? '#3a3a3a' : '#f5f5f5',
                        borderRadius: '4px',
                        cursor: isEditing ? 'default' : 'pointer',
                        transition: 'all 0.2s',
                        border: `1px solid ${
                          student.failed_submissions > 0
                            ? isDark
                              ? '#d32f2f'
                              : '#f44336'
                            : 'transparent'
                        }`,
                      }}
                      onMouseEnter={(e) => {
                        if (!isEditing) {
                          e.currentTarget.style.backgroundColor = isDark ? '#454545' : '#e8e8e8';
                        }
                      }}
                      onMouseLeave={(e) => {
                        if (!isEditing) {
                          e.currentTarget.style.backgroundColor = isDark ? '#3a3a3a' : '#f5f5f5';
                        }
                      }}
                    >
                      {/* Student Name */}
                      <div style={{ flex: 1, minWidth: 0, marginRight: '8px' }}>
                        <div
                          style={{
                            fontWeight: '500',
                            fontSize: '13px',
                            color: isDark ? '#e0e0e0' : '#333',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap',
                          }}
                        >
                          {student.name}
                        </div>
                        {student.notes && (
                          <div
                            style={{
                              fontSize: '11px',
                              color: isDark ? '#999' : '#666',
                              fontStyle: 'italic',
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              whiteSpace: 'nowrap',
                            }}
                          >
                            {student.notes.length > 35
                              ? student.notes.substring(0, 35) + '...'
                              : student.notes}
                          </div>
                        )}
                      </div>

                      {/* Assignment Count */}
                      <div
                        style={{
                          marginRight: '6px',
                          fontSize: '11px',
                          color: isDark ? '#b0b0b0' : '#666',
                          flexShrink: 0,
                        }}
                      >
                        {assignmentCount} asg
                      </div>

                      {/* Failed Submissions Count */}
                      <div
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '4px',
                          flexShrink: 0,
                        }}
                      >
                        {isEditing ? (
                          <>
                            <input
                              type="number"
                              min="0"
                              value={tempCount}
                              onChange={(e) => setTempCount(e.target.value)}
                              onKeyDown={(e) => handleKeyDown(e, student.name)}
                              onClick={(e) => e.stopPropagation()}
                              autoFocus
                              style={{
                                width: '44px',
                                padding: '2px 4px',
                                borderRadius: '4px',
                                border: `1px solid ${isDark ? '#555' : '#ddd'}`,
                                backgroundColor: isDark ? '#2d2d2d' : 'white',
                                color: isDark ? '#e0e0e0' : '#333',
                                fontSize: '12px',
                              }}
                            />
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleSaveCount(student.name);
                              }}
                              style={{
                                padding: '2px 6px',
                                fontSize: '11px',
                                backgroundColor: '#4CAF50',
                                color: 'white',
                                border: 'none',
                                borderRadius: '4px',
                                cursor: 'pointer',
                              }}
                            >
                              ✓
                            </button>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleCancelEdit();
                              }}
                              style={{
                                padding: '2px 6px',
                                fontSize: '11px',
                                backgroundColor: '#f44336',
                                color: 'white',
                                border: 'none',
                                borderRadius: '4px',
                                cursor: 'pointer',
                              }}
                            >
                              ✕
                            </button>
                          </>
                        ) : (
                          <>
                            <span
                              style={{
                                fontSize: '16px',
                                fontWeight: 'bold',
                                color:
                                  student.failed_submissions > 0
                                    ? isDark
                                      ? '#ef5350'
                                      : '#f44336'
                                    : isDark
                                    ? '#66bb6a'
                                    : '#4CAF50',
                                minWidth: '24px',
                                textAlign: 'center',
                              }}
                            >
                              {student.failed_submissions}
                            </span>
                            <button
                              onClick={(e) => handleStartEditCount(student, e)}
                              style={{
                                padding: '2px 6px',
                                fontSize: '11px',
                                backgroundColor: isDark ? '#4a4a4a' : '#e0e0e0',
                                color: isDark ? '#e0e0e0' : '#333',
                                border: 'none',
                                borderRadius: '4px',
                                cursor: 'pointer',
                              }}
                              title="Edit count"
                            >
                              ✏️
                            </button>
                          </>
                        )}
                      </div>

                      {/* Late submissions: count + minus/plus (auto-save) */}
                      <div
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '2px',
                          flexShrink: 0,
                        }}
                        onClick={(e) => e.stopPropagation()}
                      >
                        <span
                          style={{
                            fontSize: '10px',
                            color: isDark ? '#b0b0b0' : '#666',
                            marginRight: '2px',
                          }}
                          title="Late submissions"
                        >
                          Late
                        </span>
                        <button
                          type="button"
                          onClick={() => {
                            const current = student.late_submissions ?? 0;
                            if (current > 0) {
                              onUpdateLateCount(student.name, current - 1);
                            }
                          }}
                          style={{
                            width: '22px',
                            height: '22px',
                            padding: 0,
                            fontSize: '14px',
                            lineHeight: 1,
                            fontWeight: 'bold',
                            backgroundColor: isDark ? '#4a4a4a' : '#e0e0e0',
                            color: isDark ? '#e0e0e0' : '#333',
                            border: `1px solid ${isDark ? '#555' : '#ccc'}`,
                            borderRadius: '4px',
                            cursor: 'pointer',
                          }}
                          title="Decrease late count"
                        >
                          −
                        </button>
                        <span
                          style={{
                            fontSize: '14px',
                            fontWeight: '600',
                            color: isDark ? '#ffb74d' : '#e65100',
                            minWidth: '20px',
                            textAlign: 'center',
                          }}
                        >
                          {student.late_submissions ?? 0}
                        </span>
                        <button
                          type="button"
                          onClick={() => {
                            const current = student.late_submissions ?? 0;
                            onUpdateLateCount(student.name, current + 1);
                          }}
                          style={{
                            width: '22px',
                            height: '22px',
                            padding: 0,
                            fontSize: '14px',
                            lineHeight: 1,
                            fontWeight: 'bold',
                            backgroundColor: isDark ? '#4a4a4a' : '#e0e0e0',
                            color: isDark ? '#e0e0e0' : '#333',
                            border: `1px solid ${isDark ? '#555' : '#ccc'}`,
                            borderRadius: '4px',
                            cursor: 'pointer',
                          }}
                          title="Increase late count"
                        >
                          +
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Footer Buttons */}
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              gap: '8px',
              paddingTop: '8px',
              borderTop: `1px solid ${isDark ? '#444' : '#ddd'}`,
            }}
          >
            <button
              onClick={onRefresh}
              className={metalButtonClass(isDark)}
              style={{
                ...metalButtonStyle(isDark),
                padding: '6px 12px',
                fontSize: '13px',
              }}
            >
              🔄 Refresh
            </button>
            <button
              onClick={onClose}
              className={metalButtonClass(isDark)}
              style={{
                ...metalButtonStyle(isDark),
                padding: '6px 12px',
                fontSize: '13px',
              }}
            >
              Close
            </button>
          </div>
        </div>
      </div>

      {/* Student Detail Modal */}
      {selectedStudent && (
        <StudentDetailModal
          isOpen={showDetailModal}
          onClose={() => setShowDetailModal(false)}
          studentName={selectedStudent.name}
          assignments={selectedStudent.assignments}
          notes={selectedStudent.notes}
          onNotesChange={handleNotesChange}
          isDark={isDark}
          metalButtonClass={metalButtonClass}
          metalButtonStyle={metalButtonStyle}
        />
      )}
    </>
  );
}
