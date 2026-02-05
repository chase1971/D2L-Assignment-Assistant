/**
 * CurrentAssignmentDisplay - Shows the current assignment being worked on
 * Reusable component displayed in Extract Grades, Split PDF, and Clear Data cards
 */

import React from 'react';

interface CurrentAssignmentDisplayProps {
  isDark: boolean;
  lastProcessedAssignment: { name: string; className: string; zipPath: string } | null;
  selectedClass: string;
}

export default function CurrentAssignmentDisplay({
  isDark,
  lastProcessedAssignment,
  selectedClass
}: CurrentAssignmentDisplayProps) {
  return (
    <div className={`p-1.5 rounded border ${
      isDark ? 'bg-[#1a2942]/50 border-[#2a3952]' : 'bg-[#d0d0d4] border-gray-400'
    }`}>
      <div className={`text-xs uppercase tracking-wider mb-0.5 ${isDark ? 'text-gray-500' : 'text-gray-600'}`}>
        Current Assignment:
      </div>
      {lastProcessedAssignment && lastProcessedAssignment.className === selectedClass ? (
        <div className={`text-xs font-medium truncate ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>
          📄 {lastProcessedAssignment.name}
        </div>
      ) : (
        <div className={`text-xs italic ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>
          None
        </div>
      )}
    </div>
  );
}
