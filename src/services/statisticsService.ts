/**
 * Statistics Service
 * API calls for student statistics tracking
 */

import { apiCall, ApiResult, LogCallback } from './quizGraderService';

export interface StudentStatistics {
  name: string;
  failed_submissions: number;
  late_submissions: number;
  assignments: {
    [assignmentName: string]: {
      submitted: boolean;
      date: string;
    };
  };
  notes: string;
}

export interface StatisticsData {
  students: {
    [studentName: string]: {
      failed_submissions: number;
      late_submissions: number;
      assignments: {
        [assignmentName: string]: {
          submitted: boolean;
          date: string;
        };
      };
      notes: string;
    };
  };
  last_updated: string | null;
}

/**
 * Load statistics for a class
 */
export const loadStatistics = (
  className: string,
  addLog?: LogCallback
): Promise<ApiResult & { statistics?: StatisticsData; students?: StudentStatistics[] }> =>
  apiCall({
    endpoint: '/statistics/load',
    body: { className },
    errorMessage: 'Failed to load statistics',
    addLog
  });

/**
 * Save statistics for a class
 */
export const saveStatistics = (
  className: string,
  statistics: StatisticsData,
  addLog?: LogCallback
): Promise<ApiResult> =>
  apiCall({
    endpoint: '/statistics/save',
    body: { className, statistics },
    errorMessage: 'Failed to save statistics',
    addLog
  });

/**
 * Update notes for a specific student
 */
export const updateStudentNotes = (
  className: string,
  studentName: string,
  notes: string,
  addLog?: LogCallback
): Promise<ApiResult> =>
  apiCall({
    endpoint: '/statistics/update-notes',
    body: { className, studentName, notes },
    errorMessage: 'Failed to update student notes',
    addLog
  });

/**
 * Update failed submission count for a specific student
 */
export const updateFailedSubmissionCount = (
  className: string,
  studentName: string,
  count: number,
  addLog?: LogCallback
): Promise<ApiResult> =>
  apiCall({
    endpoint: '/statistics/update-count',
    body: { className, studentName, count },
    errorMessage: 'Failed to update failed submission count',
    addLog
  });

/**
 * Update late submission count for a specific student (auto-saved)
 */
export const updateLateSubmissionCount = (
  className: string,
  studentName: string,
  count: number,
  addLog?: LogCallback
): Promise<ApiResult> =>
  apiCall({
    endpoint: '/statistics/update-late-count',
    body: { className, studentName, count },
    errorMessage: 'Failed to update late submission count',
    addLog
  });
