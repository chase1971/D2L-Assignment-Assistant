import React from 'react';
import { FolderOpen } from 'lucide-react';
import ZipSelectionModal from './ZipSelectionModal';
import AssignmentSelectionModal from './AssignmentSelectionModal';
import ConfirmationModal from './ConfirmationModal';
import ClearOptionsModal from './ClearOptionsModal';
import ClassSetupModal from './ClassSetupModal';
import EmailStudentsModal from './EmailStudentsModal';
import PatchManager from './PatchManager';
import ActionCard from './ActionCard';
import LogTerminal from './LogTerminal';
import NavigationBar from './NavigationBar';
import MetalButton from './MetalButton';
import CurrentAssignmentDisplay from './CurrentAssignmentDisplay';
import { useThemeStyles } from './hooks/useThemeStyles';
import { useOption2State } from './hooks/useOption2State';
import { useOption2Actions } from './hooks/useOption2Actions';

// Option 2: Horizontal Top Bar with Grid Layout Below - Figma Metallic Style
export default function Option2() {
  const drive = 'C'; // Always use C drive
  
  // Get all state from custom hook
  const state = useOption2State();
  
  // Get all actions from custom hook
  const actions = useOption2Actions(state, drive);
  
  // Get theme styles from hook
  const { metalButtonClass, metalButtonStyle } = useThemeStyles();

  return (
    <div className={`h-screen flex flex-col transition-colors ${state.isDark ? 'bg-[#0a0e1a]' : 'bg-[#d0d0d2]'}`}>
      {/* Top Navigation Bar */}
      <NavigationBar
        isDark={state.isDark}
        setIsDark={state.setIsDark}
        selectedClass={state.selectedClass}
        handleClassChange={actions.handleClassChange}
        classOptions={state.classOptions}
        handleOpenDownloads={actions.handleOpenDownloads}
        onClassSetupClick={() => state.setShowClassSetup(true)}
        onPatchManagerClick={() => state.setShowPatchManager(true)}
        serverStatus={state.serverStatus}
        metalButtonClass={metalButtonClass}
        metalButtonStyle={metalButtonStyle}
      />

      {/* ZIP File Selection Modal */}
      <ZipSelectionModal
        isOpen={state.showZipSelection}
        onClose={actions.handleZipModalClose}
        zipFiles={state.zipFiles}
        onSelect={actions.handleZipModalSelect}
        isDark={state.isDark}
        metalButtonClass={metalButtonClass}
        metalButtonStyle={metalButtonStyle}
      />
      
      {/* Assignment Selection Modal for Clear Data */}
      <AssignmentSelectionModal
        isOpen={state.showAssignmentSelection}
        onClose={actions.handleAssignmentModalClose}
        folders={state.processingFolders}
        selectedAssignments={state.selectedAssignments}
        onToggleAssignment={actions.handleToggleAssignment}
        onSelectAll={actions.handleSelectAll}
        onDeselectAll={actions.handleDeselectAll}
        onConfirm={actions.handleAssignmentSelection}
        isDark={state.isDark}
        metalButtonClass={metalButtonClass}
        metalButtonStyle={metalButtonStyle}
      />
      
      {/* Confirmation Modal */}
      {state.confirmationConfig && (
        <ConfirmationModal
          isOpen={state.showConfirmation}
          onClose={() => {
            state.setShowConfirmation(false);
            state.setConfirmationConfig(null);
          }}
          onConfirm={state.confirmationConfig.onConfirm}
          title={state.confirmationConfig.title}
          message={state.confirmationConfig.message}
          confirmText="CLEAR"
          cancelText="CANCEL"
          isDark={state.isDark}
          metalButtonClass={metalButtonClass}
          metalButtonStyle={metalButtonStyle}
        />
      )}
      
      {/* Clear Options Modal */}
      {state.clearOptionsConfig && (
        <ClearOptionsModal
          isOpen={state.showClearOptions}
          onClose={() => {
            state.setShowClearOptions(false);
            state.setClearOptionsConfig(null);
          }}
          onConfirm={state.clearOptionsConfig.onConfirm}
          title={state.clearOptionsConfig.title}
          message={state.clearOptionsConfig.message}
          isDark={state.isDark}
          metalButtonClass={metalButtonClass}
          metalButtonStyle={metalButtonStyle}
          hasCurrentAssignment={state.clearOptionsConfig.hasCurrentAssignment}
          onBack={state.clearOptionsConfig.onBack}
        />
      )}

      {/* Class Setup Modal */}
      <ClassSetupModal
        isOpen={state.showClassSetup}
        onClose={() => state.setShowClassSetup(false)}
        classes={state.classes}
        onClassesUpdated={state.reloadClasses}
        isDark={state.isDark}
        metalButtonClass={metalButtonClass}
        metalButtonStyle={metalButtonStyle}
      />

      {/* Email Students Modal */}
      <EmailStudentsModal
        isOpen={state.showEmailModal}
        onClose={() => state.setShowEmailModal(false)}
        students={state.emailStudents}
        mode={state.emailModalMode}
        onEmail={(selectedStudents) => {
          state.addLog(`📧 Email functionality will be implemented later. Selected ${selectedStudents.length} students.`);
          state.setShowEmailModal(false);
        }}
        isDark={state.isDark}
        metalButtonClass={metalButtonClass}
        metalButtonStyle={metalButtonStyle}
      />

      {/* Patch Manager Modal */}
      {state.showPatchManager && (
        <PatchManager
          isDark={state.isDark}
          onClose={() => state.setShowPatchManager(false)}
          addLog={state.addLog}
        />
      )}

      {/* Main Content Grid */}
      <div className="flex-1 overflow-auto p-3">
        <div className="grid grid-cols-3 gap-3 h-full max-h-full">
          {/* Left Column - Actions */}
          <div className="space-y-2.5">
            {/* Process Quizzes */}
            <ActionCard title="PROCESS QUIZZES" isDark={state.isDark}>
              <div className="space-y-2">
                <MetalButton
                  onClick={actions.handleProcessQuizzes}
                  disabled={!state.selectedClass || state.processing || state.processingCompletion}
                  isDark={state.isDark}
                  loading={state.processing}
                  loadingText="PROCESSING..."
                  className="w-full"
                >
                  PROCESS QUIZZES
                </MetalButton>
                
                <MetalButton
                  onClick={actions.handleProcessCompletion}
                  disabled={!state.selectedClass || state.processing || state.processingCompletion}
                  isDark={state.isDark}
                  loading={state.processingCompletion}
                  loadingText="PROCESSING..."
                  className="w-full"
                >
                  PROCESS COMPLETION
                </MetalButton>
                
                <label className="flex items-center gap-1.5 mt-1.5 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={state.dontOverride}
                    onChange={(e) => state.setDontOverride(e.target.checked)}
                    className="rounded"
                    style={{ width: '14px', height: '14px' }}
                  />
                  <span className={`text-xs ${state.isDark ? 'text-gray-400' : 'text-gray-700'}`}>
                    Don't override grades
                  </span>
                </label>
              </div>
            </ActionCard>

            {/* Extract Grades */}
            <ActionCard title="EXTRACT GRADES" isDark={state.isDark}>
              <div className={`mb-2 rounded border flex items-center justify-between gap-2 ${
                state.isDark ? 'bg-[#1a2942]/50 border-[#2a3952]' : 'bg-[#d0d0d4] border-gray-400'
              }`} style={{ padding: '6px' }}>
                <div className="flex-1">
                  <CurrentAssignmentDisplay
                    isDark={state.isDark}
                    lastProcessedAssignment={state.lastProcessedAssignment}
                    selectedClass={state.selectedClass}
                  />
                </div>
                <MetalButton
                  onClick={actions.handleSelectPdfFileForExtraction}
                  disabled={!state.selectedClass || state.extracting}
                  isDark={state.isDark}
                  scaleType="icon"
                  title="Select a PDF file to extract grades from"
                  style={{ fontSize: '10px', padding: '4px 8px' }}
                >
                  📄 Select PDF
                </MetalButton>
              </div>
              
              <MetalButton
                onClick={actions.handleExtractGrades}
                disabled={!state.selectedClass || state.extracting}
                isDark={state.isDark}
                loading={state.extracting}
                loadingText="EXTRACTING..."
                className="w-full"
              >
                EXTRACT GRADES
              </MetalButton>
            </ActionCard>

            {/* Split PDF */}
            <ActionCard title="SPLIT PDF" isDark={state.isDark}>
              <div className={`mb-2 rounded border flex items-center justify-between gap-2 ${
                state.isDark ? 'bg-[#1a2942]/50 border-[#2a3952]' : 'bg-[#d0d0d4] border-gray-400'
              }`} style={{ padding: '6px' }}>
                <div className="flex-1">
                  <CurrentAssignmentDisplay
                    isDark={state.isDark}
                    lastProcessedAssignment={state.lastProcessedAssignment}
                    selectedClass={state.selectedClass}
                  />
                </div>
                <MetalButton
                  onClick={actions.handleSelectPdfFile}
                  disabled={!state.selectedClass || state.splitting}
                  isDark={state.isDark}
                  scaleType="icon"
                  title="Select any PDF file to split and rezip"
                  style={{ fontSize: '10px', padding: '4px 8px' }}
                >
                  📄 Upload PDF
                </MetalButton>
              </div>
              
              <div className="space-y-2">
                <MetalButton
                  onClick={() => {
                    const pdfPath = state.lastProcessedAssignment?.zipPath || null;
                    actions.handleSplitPdf(state.lastProcessedAssignment?.name || null, pdfPath);
                  }}
                  disabled={!state.selectedClass || state.splitting || !state.lastProcessedAssignment || state.lastProcessedAssignment.className !== state.selectedClass}
                  isDark={state.isDark}
                  loading={state.splitting}
                  loadingText="PROCESSING..."
                  title={!state.lastProcessedAssignment || state.lastProcessedAssignment.className !== state.selectedClass ? 'Process quizzes first or select a PDF above' : ''}
                  className="w-full"
                >
                  SPLIT PDF AND REZIP
                </MetalButton>
                
                <button
                  onClick={actions.handleOpenFolder}
                  disabled={!state.selectedClass}
                  className={`w-full rounded-lg border shadow-lg flex items-center justify-center gap-2 font-medium ${metalButtonClass(state.isDark)} disabled:cursor-not-allowed`}
                  style={{ 
                    ...metalButtonStyle(state.isDark), 
                    padding: '16px 16px', 
                    fontSize: '14px', 
                    transition: 'all 0.15s ease',
                    ...(!state.selectedClass ? {
                      opacity: 0.5,
                      filter: 'saturate(0.2) brightness(0.85)',
                      pointerEvents: 'none'
                    } : {})
                  }}
                  title={state.lastProcessedAssignment && state.lastProcessedAssignment.className === state.selectedClass 
                    ? `Open grade processing folder for ${state.lastProcessedAssignment.name}`
                    : state.selectedClass 
                    ? `Open class roster folder for ${state.selectedClass}`
                    : 'Select a class first'}
                >
                  <FolderOpen size={18} />
                  {state.lastProcessedAssignment && state.lastProcessedAssignment.className === state.selectedClass 
                    ? `OPEN: ${state.lastProcessedAssignment.name.replace(/\s+combined\s+pdf\s*$/i, '').toUpperCase()}`
                    : state.selectedClass 
                    ? `OPEN: ${state.selectedClass.toUpperCase()}`
                    : 'OPEN FOLDER'}
                </button>
              </div>
            </ActionCard>

            {/* Clear Data */}
            <ActionCard title="CLEAR DATA" isDark={state.isDark} titleColor={state.isDark ? 'text-red-400' : 'text-red-700'}>
              <div className="flex items-center gap-2">
                <MetalButton
                  onClick={actions.handleClearAllData}
                  disabled={!state.selectedClass || state.clearing}
                  isDark={state.isDark}
                  variant="danger"
                  style={{ fontSize: '14px', padding: '8px 20px' }}
                >
                  {state.clearing ? 'CLEARING...' : 'CLEAR'}
                </MetalButton>
                
                <CurrentAssignmentDisplay
                  isDark={state.isDark}
                  lastProcessedAssignment={state.lastProcessedAssignment}
                  selectedClass={state.selectedClass}
                />
              </div>
            </ActionCard>

            {/* Email Students */}
            <ActionCard title="EMAIL STUDENTS" isDark={state.isDark}>
              <div className="space-y-2">
                <MetalButton
                  onClick={actions.handleEmailAll}
                  disabled={!state.selectedClass}
                  isDark={state.isDark}
                >
                  EMAIL ALL
                </MetalButton>
                
                <MetalButton
                  onClick={actions.handleEmailWithoutAssignment}
                  disabled={!state.selectedClass}
                  isDark={state.isDark}
                >
                  EMAIL STUDENTS WITHOUT ASSIGNMENT
                </MetalButton>
              </div>
            </ActionCard>
          </div>

          {/* Right Column Spanning 2/3 - Log Terminal */}
          <LogTerminal
            logs={state.logs}
            isDark={state.isDark}
            addLog={state.addLog}
            clearLogs={() => state.setLogs([])}
            confidenceScores={state.confidenceScores}
            drive={drive}
            selectedClass={state.selectedClass}
          />
        </div>
      </div>
    </div>
  );
}
