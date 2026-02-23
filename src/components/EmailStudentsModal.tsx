import React, { useState, useMemo } from 'react';
import { Mail, CheckSquare, Square } from 'lucide-react';
import BaseModal from './BaseModal';
import MetalButton from './MetalButton';
import { DARK_THEME } from './constants/ui-constants';

interface Student {
  name: string;
  hasAssignment: boolean;
  email?: string;
  isUnreadable?: boolean;
}

interface EmailStudentsModalProps {
  isOpen: boolean;
  onClose: () => void;
  students: Student[];
  mode: 'all' | 'without-assignment';
  onEmail: (selectedStudents: string[]) => void;
  isDark: boolean;
  metalButtonClass?: (isDark: boolean) => string;
  metalButtonStyle?: (isDark: boolean) => React.CSSProperties | undefined;
}

export default function EmailStudentsModal({
  isOpen,
  onClose,
  students,
  mode,
  onEmail,
  isDark,
}: EmailStudentsModalProps) {
  // Helper function to capitalize names properly
  const capitalizeName = (name: string): string => {
    return name
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(' ');
  };

  // Reorder students to flow down columns instead of across rows
  const reorderForColumns = (items: Student[], numColumns: number): Student[] => {
    if (items.length === 0 || numColumns <= 1) return items;

    const numRows = Math.ceil(items.length / numColumns);
    const reordered: Student[] = [];

    for (let row = 0; row < numRows; row++) {
      for (let col = 0; col < numColumns; col++) {
        const index = row + col * numRows;
        if (index < items.length) {
          reordered.push(items[index]);
        }
      }
    }

    return reordered;
  };

  // Initialize selected students based on mode
  const initialSelected = useMemo(() => {
    if (mode === 'all') {
      return new Set(students.map(s => s.name));
    } else {
      return new Set(students.filter(s => !s.hasAssignment).map(s => s.name));
    }
  }, [students, mode]);

  const [selectedStudents, setSelectedStudents] = useState<Set<string>>(initialSelected);

  // Update selected when mode or students change
  React.useEffect(() => {
    if (mode === 'all') {
      setSelectedStudents(new Set(students.map(s => s.name)));
    } else {
      setSelectedStudents(new Set(students.filter(s => !s.hasAssignment).map(s => s.name)));
    }
  }, [mode, students]);

  // Calculate breakdown of selected students for tooltip
  const selectedStudentObjects = students.filter(s => selectedStudents.has(s.name));
  const unreadableCount = selectedStudentObjects.filter(s => s.isUnreadable).length;
  const noSubmissionCount = selectedStudentObjects.filter(s => !s.hasAssignment && !s.isUnreadable).length;
  const hasAssignmentCount = selectedStudentObjects.filter(s => s.hasAssignment).length;
  const noneSelected = selectedStudents.size === 0;

  const tooltipText = React.useMemo(() => {
    if (noneSelected) {
      return 'Select students to email';
    }
    return `Selected: ${selectedStudents.size} students\n` +
           `  • ${hasAssignmentCount} with assignments\n` +
           `  • ${noSubmissionCount} no submission\n` +
           `  • ${unreadableCount} unreadable`;
  }, [selectedStudents.size, hasAssignmentCount, noSubmissionCount, unreadableCount, noneSelected]);

  const allSelected = students.length > 0 && students.every(student => selectedStudents.has(student.name));

  const handleToggleStudent = (studentName: string) => {
    setSelectedStudents(prev => {
      const next = new Set(prev);
      if (next.has(studentName)) {
        next.delete(studentName);
      } else {
        next.add(studentName);
      }
      return next;
    });
  };

  const handleSelectAll = () => {
    if (allSelected) {
      setSelectedStudents(new Set());
    } else {
      setSelectedStudents(new Set(students.map(s => s.name)));
    }
  };

  const handleEmail = async () => {
    const selectedNames = Array.from(selectedStudents);

    // Get emails for selected students
    const selectedStudentObjects = students.filter(s => selectedStudents.has(s.name));
    const emails = selectedStudentObjects
      .map(s => s.email)
      .filter(email => email && email.trim() !== '')
      .join('; ');

    // Copy emails to clipboard
    if (emails) {
      try {
        await navigator.clipboard.writeText(emails);
        console.log('Emails copied to clipboard:', emails);
      } catch (error) {
        console.error('Failed to copy emails to clipboard:', error);
        const textarea = document.createElement('textarea');
        textarea.value = emails;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        try {
          document.execCommand('copy');
          console.log('Emails copied to clipboard (fallback method)');
        } catch (err) {
          console.error('Fallback clipboard copy failed:', err);
        }
        document.body.removeChild(textarea);
      }
    }

    // Launch Firefox with Outlook URL
    try {
      const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';
      const response = await fetch(`${API_BASE_URL}/launch-firefox-outlook`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error('Failed to launch Firefox:', errorData.error || 'Unknown error');
      }
    } catch (error) {
      console.error('Error launching Firefox:', error);
    }

    onEmail(selectedNames);
  };

  const modalTitle = mode === 'all'
    ? `EMAIL ALL STUDENTS (${students.length} students)`
    : `EMAIL STUDENTS WITHOUT ASSIGNMENT (${students.length} students)`;

  return (
    <BaseModal
      isOpen={isOpen}
      onClose={onClose}
      isDark={isDark}
      title={modalTitle}
      icon={Mail}
      iconColor={isDark ? '#22d3ee' : '#1a2942'}
      width="900px"
      maxHeight="80vh"
      footer={
        <div style={{ display: 'flex', gap: '10px' }}>
          <MetalButton onClick={onClose} isDark={isDark} className="flex-1">
            CANCEL
          </MetalButton>
          <MetalButton
            onClick={handleEmail}
            isDark={isDark}
            disabled={noneSelected}
            className="flex-1"
            title={tooltipText}
          >
            EMAIL ({selectedStudents.size})
          </MetalButton>
        </div>
      }
    >
      <div style={{ margin: '-20px', marginBottom: '-20px' }}>
        {/* Select All / Deselect All Bar */}
        <div
          style={{
            padding: '10px 20px',
            backgroundColor: isDark ? DARK_THEME.bgSecondary : '#b8b8bc',
            borderBottom: isDark ? `1px solid ${DARK_THEME.bgQuaternary}` : '1px solid #999',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '12px',
          }}
        >
          <span style={{
            fontSize: '12px',
            color: isDark ? '#888' : '#666'
          }}>
            {selectedStudents.size} selected
          </span>
          <MetalButton
            onClick={handleSelectAll}
            isDark={isDark}
            style={{ fontSize: '12px', padding: '6px 12px' }}
          >
            {allSelected ? 'Deselect All' : 'Select All'}
          </MetalButton>
        </div>

        {/* Scrollable Student List */}
        <div
          style={{
            overflowY: 'auto',
            backgroundColor: isDark ? DARK_THEME.bgSecondary : '#b8b8bc',
            maxHeight: 'calc(80vh - 220px)',
            padding: '8px',
          }}
        >
          {students.length === 0 ? (
            <div style={{
              padding: '40px 20px',
              textAlign: 'center',
              color: isDark ? '#888' : '#666',
            }}>
              <p style={{ fontSize: '14px', marginBottom: '8px' }}>No students found</p>
              <p style={{ fontSize: '12px', fontStyle: 'italic' }}>
                Make sure the import file exists and contains student data.
              </p>
            </div>
          ) : (
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(3, 1fr)',
              gap: '4px',
            }}>
              {reorderForColumns(students, 3).map((student, index) => {
                const isSelected = selectedStudents.has(student.name);
                return (
                  <button
                    key={index}
                    onClick={() => handleToggleStudent(student.name)}
                    style={{
                      width: '100%',
                      padding: '10px 12px',
                      textAlign: 'left',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                      backgroundColor: isSelected
                        ? (isDark ? 'rgba(0, 200, 255, 0.2)' : 'rgba(100, 150, 255, 0.2)')
                        : 'transparent',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      transition: 'all 0.15s ease',
                    }}
                    onMouseEnter={(e) => {
                      if (!isSelected) {
                        e.currentTarget.style.backgroundColor = isDark ? 'rgba(0, 200, 255, 0.15)' : 'rgba(100, 150, 255, 0.1)';
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (!isSelected) {
                        e.currentTarget.style.backgroundColor = 'transparent';
                      }
                    }}
                  >
                    {/* Checkbox Icon */}
                    <div style={{ flexShrink: 0 }}>
                      {isSelected ? (
                        <CheckSquare
                          size={18}
                          style={{ color: isDark ? '#00c8ff' : '#1a2942' }}
                        />
                      ) : (
                        <Square
                          size={18}
                          style={{ color: isDark ? '#666' : '#999' }}
                        />
                      )}
                    </div>

                    {/* Student Info */}
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{
                        fontSize: '13px',
                        fontWeight: '500',
                        color: isDark ? '#e0e0e0' : '#333',
                        whiteSpace: 'nowrap',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                      }}>
                        {capitalizeName(student.name)}
                      </div>
                      {!student.hasAssignment && (
                        <div style={{
                          fontSize: '10px',
                          color: student.isUnreadable
                            ? (isDark ? '#ffaa00' : '#cc8800')
                            : (isDark ? '#ff6b6b' : '#cc0000'),
                          fontStyle: 'italic',
                          marginTop: '2px',
                        }}
                        title={student.isUnreadable
                          ? 'Unreadable submission (treated as no submission)'
                          : 'No submission'
                        }
                        >
                          {student.isUnreadable ? 'unreadable' : 'no assignment'}
                        </div>
                      )}
                    </div>
                  </button>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </BaseModal>
  );
}
