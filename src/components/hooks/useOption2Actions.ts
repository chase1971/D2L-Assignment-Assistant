/**
 * useOption2Actions - Action handlers hook for Option2 component
 * All business logic and event handlers
 */

import {
  processQuizzes,
  processSelectedQuiz,
  processCompletion,
  processSelectedCompletion,
  extractGrades,
  splitPdf,
  splitPdfUpload,
  openFolder,
  openDownloads,
  clearAllData,
  listProcessingFolders,
  getPdfsFolderPath,
  validateFolder,
  loadStudentsForEmail as loadStudentsForEmailService
} from '../../services/quizGraderService';
import { ClearOption } from '../ClearOptionsModal';
import { Option2State } from './useOption2State';
import {
  displayError,
  formatAssignmentDisplayName,
  formatAssignmentFolderName
} from '../utils/assignmentUtils';

export interface Option2Actions {
  handleClassChange: (e: any) => Promise<void>;
  handleOpenDownloads: () => Promise<void>;
  handleProcessQuizzes: () => Promise<void>;
  handleZipSelection: (zipPath: string) => Promise<void>;
  handleZipModalClose: () => void;
  handleZipModalSelect: (zipPath: string) => void;
  handleCompletionZipSelection: (zipPath: string) => Promise<void>;
  handleProcessCompletion: () => Promise<void>;
  handleExtractGrades: () => Promise<void>;
  handleSelectPdfFileForExtraction: () => Promise<void>;
  handleSelectPdfFile: () => Promise<void>;
  handleSplitPdfUpload: (file: File) => Promise<void>;
  handleSplitPdf: (assignmentName?: string | null, pdfPath?: string | null) => Promise<void>;
  handleOpenFolder: () => Promise<void>;
  handleOpenClassRosterFolder: () => Promise<void>;
  handleClearAllData: () => Promise<void>;
  handleAssignmentSelection: () => void;
  handleAssignmentModalClose: () => void;
  handleToggleAssignment: (assignmentName: string) => void;
  handleSelectAll: (folderNames?: string[]) => void;
  handleDeselectAll: () => void;
  handleEmailAll: () => Promise<void>;
  handleEmailWithoutAssignment: () => Promise<void>;
  loadStudentsForEmail: () => Promise<Array<{name: string; hasAssignment: boolean; email?: string; isUnreadable?: boolean}>>;
}

export function useOption2Actions(state: Option2State, drive: string = 'C'): Option2Actions {
  const {
    selectedClass,
    addLog,
    setProcessing,
    setProcessingCompletion,
    setExtracting,
    setSplitting,
    setClearing,
    setZipFiles,
    setZipSelectionMode,
    setShowZipSelection,
    setLastProcessedAssignment,
    setConfidenceScores,
    setPdfsFolderPath,
    setClassRosterPath,
    setUploadedPdfFile,
    setUploadedPdfFileForExtraction,
    setSelectedPdfPathForExtraction,
    setProcessingFolders,
    setSelectedAssignments,
    setWasSelectAllUsed,
    setShowAssignmentSelection,
    setShowClearOptions,
    setClearOptionsConfig,
    setShowEmailModal,
    setEmailModalMode,
    setEmailStudents,
    requireClass,
    processing,
    processingCompletion,
    extracting,
    splitting,
    clearing,
    classes,
    zipSelectionMode,
    lastProcessedAssignment,
    uploadedPdfFile,
    pdfsFolderPath,
    processingFolders,
    selectedAssignments,
    wasSelectAllUsed,
    dontOverride
  } = state;

  // Load students from import file
  const loadStudentsForEmail = async (): Promise<Array<{name: string; hasAssignment: boolean; email?: string; isUnreadable?: boolean}>> => {
    if (!selectedClass || !drive) {
      return [];
    }
    
    const assignmentName = lastProcessedAssignment && lastProcessedAssignment.className === selectedClass
      ? lastProcessedAssignment.name
      : null;
    
    try {
      const result = await loadStudentsForEmailService(drive, selectedClass, assignmentName, addLog);
      if (result.success && result.students) {
        return result.students;
      } else {
        addLog(`❌ Error loading students: ${result.error || 'Unknown error'}`);
        return [];
      }
    } catch (error) {
      addLog(`❌ Error loading students: ${error instanceof Error ? error.message : 'Unknown error'}`);
      return [];
    }
  };

  // Handle class selection
  const handleClassChange = async (e: any) => {
    const newClass = e.target.value;
    state.setSelectedClass(newClass);
    setPdfsFolderPath(null);
    setUploadedPdfFile(null);
    setUploadedPdfFileForExtraction(null);
    setSelectedPdfPathForExtraction(null);
    setLastProcessedAssignment(null);
    
    if (newClass) {
      const classData = classes.find(cls => cls.value === newClass);
      let rosterPath = classData?.rosterFolderPath;
      
      if (rosterPath) {
        setClassRosterPath(rosterPath);
        addLog(`✅ Class loaded: ${newClass}`);
        addLog(`📂 Location: ${rosterPath}`);
        
        const validation = await validateFolder(rosterPath);
        if (!validation.success) {
          addLog(`❌ Class folder not found: ${newClass}`);
          if (validation.error) {
            addLog(`   Error: ${validation.error}`);
          }
        } else if (!validation.hasCSV) {
          addLog(`❌ No import file found in this folder [E1051]`);
        }
        
        const pathResult = await getPdfsFolderPath(drive, newClass);
        setPdfsFolderPath(pathResult);
      } else {
        const pathResult = await getPdfsFolderPath(drive, newClass);
        setPdfsFolderPath(pathResult);
        
        if (pathResult?.classFolder) {
          setClassRosterPath(pathResult.classFolder);
          rosterPath = pathResult.classFolder;
        } else if (pathResult?.targetPath) {
          const pdfsPath = pathResult.targetPath;
          const classRosterFolder = pdfsPath.split(/[/\\]PDFs/)[0]?.split(/[/\\]grade processing/)[0]?.trim() || null;
          if (classRosterFolder) {
            setClassRosterPath(classRosterFolder);
            rosterPath = classRosterFolder;
          }
        }
        
        if (pathResult) {
          addLog(`✅ Class loaded: ${newClass}`);
          const locationPath = pathResult.classFolder || pathResult.targetPath?.split(/[/\\]PDFs/)[0]?.split(/[/\\]grade processing/)[0]?.trim() || pathResult.targetPath;
          addLog(`📂 Location: ${locationPath}`);
          
          if (rosterPath) {
            const validation = await validateFolder(rosterPath);
            if (!validation.hasCSV) {
              addLog(`❌ No import file found in this folder [E1051]`);
            }
          }
        } else {
          addLog(`✅ Class loaded: ${newClass}`);
          addLog(`⚠️ Could not determine class folder location`);
        }
      }
    } else {
      setClassRosterPath(null);
    }
  };

  // Open Downloads folder
  const handleOpenDownloads = async () => {
    try {
      const result = await openDownloads(addLog);
      if (result.success) {
        addLog('✅ Downloads folder opened successfully!');
      } else {
        addLog(`❌ ${result.error}`);
      }
    } catch (error) {
      addLog(`❌ ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  // Process quizzes
  const handleProcessQuizzes = async () => {
    if (!requireClass()) return;

    setProcessing(true);
    addLog('🔍 Searching for assignment ZIP in Downloads...');
    
    try {
      const result = await processQuizzes(drive, selectedClass, addLog);
      
      if (result.success) {
        // Success message already logged
      } else if (result.error === 'Multiple ZIP files found') {
        setZipFiles(result.zip_files || []);
        setZipSelectionMode('quiz');
        setShowZipSelection(true);
        return;
      } else {
        displayError(result.error, addLog);
      }
    } catch (error) {
      displayError(error instanceof Error ? error.message : 'Unknown error', addLog);
    } finally {
      setProcessing(false);
    }
  };

  // Handle ZIP file selection for quizzes
  const handleZipSelection = async (zipPath: string) => {
    setShowZipSelection(false);
    setProcessing(true);
    const zipFilename = zipPath.split('\\').pop() || '';
    addLog(`📦 Processing: ${zipFilename}`);
    
    try {
      const result = await processSelectedQuiz(drive, selectedClass, zipPath, addLog);
      
      if (result.success) {
        let rawName = result.combined_pdf_path 
          ? result.combined_pdf_path.split('\\').pop()?.replace('.pdf', '') || result.assignment_name
          : result.assignment_name || zipFilename.replace(/\s*Download.*\.zip$/i, '').trim();
        
        const displayName = formatAssignmentDisplayName(rawName, selectedClass);
        
        setLastProcessedAssignment({
          name: displayName,
          className: selectedClass,
          zipPath: zipPath
        });
      } else {
        displayError(result.error, addLog);
      }
    } catch (error) {
      displayError(error instanceof Error ? error.message : 'Unknown error', addLog);
    } finally {
      setProcessing(false);
    }
  };

  // Handle ZIP modal close
  const handleZipModalClose = () => {
    setShowZipSelection(false);
    setProcessing(false);
    setProcessingCompletion(false);
  };

  // Handle ZIP modal selection
  const handleZipModalSelect = (zipPath: string) => {
    if (zipSelectionMode === 'quiz') {
      handleZipSelection(zipPath);
    } else {
      handleCompletionZipSelection(zipPath);
    }
  };

  // Handle ZIP file selection for completions
  const handleCompletionZipSelection = async (zipPath: string) => {
    setShowZipSelection(false);
    setProcessingCompletion(true);
    const zipFilename = zipPath.split('\\').pop() || '';
    addLog(`📦 Processing: ${zipFilename}`);
    
    try {
      const result = await processSelectedCompletion(drive, selectedClass, zipPath, dontOverride, addLog);
      
      if (result.success) {
        addLog('✅ Completion processing completed!');
        addLog('✅ Auto-assigned 10 points to all submissions');
        
        if (result.assignment_name) {
          const rawAssignmentName = result.assignment_name.trim();
          setLastProcessedAssignment({
            name: rawAssignmentName,
            className: selectedClass,
            zipPath: zipPath
          });
        }
      } else {
        displayError(result.error, addLog);
      }
    } catch (error) {
      displayError(error instanceof Error ? error.message : 'Unknown error', addLog);
    } finally {
      setProcessingCompletion(false);
    }
  };

  // Process completion
  const handleProcessCompletion = async () => {
    if (!requireClass()) return;

    setProcessingCompletion(true);
    addLog('🔍 Searching for assignment ZIP in Downloads...');
    
    try {
      const result = await processCompletion(drive, selectedClass, dontOverride, addLog);
      
      if (result.success) {
        addLog('✅ Completion processing completed!');
        addLog('✅ Auto-assigned 10 points to all submissions');
        
        if (result.assignment_name) {
          const rawAssignmentName = result.assignment_name.trim();
          setLastProcessedAssignment({
            name: rawAssignmentName,
            className: selectedClass,
            zipPath: ''
          });
        }
      } else if (result.error === 'Multiple ZIP files found') {
        setZipFiles(result.zip_files || []);
        setZipSelectionMode('completion');
        setShowZipSelection(true);
        return;
      } else {
        displayError(result.error, addLog);
      }
    } catch (error) {
      displayError(error instanceof Error ? error.message : 'Unknown error', addLog);
    } finally {
      setProcessingCompletion(false);
    }
  };

  // Extract grades
  const handleExtractGrades = async () => {
    if (!requireClass()) return;

    setExtracting(true);
    addLog('🔬 Starting grade extraction...');
    
    try {
      const result = await extractGrades(drive, selectedClass, state.selectedPdfPathForExtraction || undefined, addLog);
      
      if (result.success && result.confidenceScores) {
        setConfidenceScores(result.confidenceScores);
      } else {
        setConfidenceScores(null);
      }
      
      if (result.success && result.assignmentName) {
        const displayName = formatAssignmentDisplayName(result.assignmentName, selectedClass);
        setLastProcessedAssignment({
          name: displayName,
          className: selectedClass,
          zipPath: result.pdfPath || state.selectedPdfPathForExtraction || ''
        });
      }
      
      if (!result.success) {
        if (result.error && (!result.logs || result.logs.length === 0)) {
          displayError(result.error, addLog);
        }
      }
    } catch (error) {
      displayError(error instanceof Error ? error.message : 'Unknown error', addLog);
    } finally {
      setExtracting(false);
    }
  };

  // Handle PDF file selection for grade extraction
  const handleSelectPdfFileForExtraction = async () => {
    if (!requireClass()) return;

    try {
      if ((window as any).electronAPI?.showOpenDialog) {
        let pathInfo = pdfsFolderPath;
        if (!pathInfo) {
          pathInfo = await getPdfsFolderPath(drive, selectedClass);
          if (pathInfo) {
            setPdfsFolderPath(pathInfo);
          }
        }
        
        const dialogOptions: any = {
          filters: [{ name: 'PDF Files', extensions: ['pdf'] }],
          properties: ['openFile']
        };
        
        if (pathInfo && pathInfo.existingPath) {
          dialogOptions.defaultPath = pathInfo.existingPath;
        }
        
        const result = await (window as any).electronAPI.showOpenDialog(dialogOptions);
        
        if (result && !result.canceled && result.filePaths && result.filePaths.length > 0) {
          const filePath = result.filePaths[0];
          const fileName = filePath.split(/[/\\]/).pop() || '';
          addLog(`📄 Selected PDF for extraction: ${fileName}`);
          
          setSelectedPdfPathForExtraction(filePath);
          
          const rawAssignmentName = fileName.replace(/\.pdf$/i, '').trim();
          const displayName = formatAssignmentDisplayName(rawAssignmentName, selectedClass);
          
          setLastProcessedAssignment({
            name: displayName,
            className: selectedClass,
            zipPath: filePath
          });
          
          addLog(`✅ PDF set for extraction. Click "EXTRACT GRADES" to process.`);
        }
      } else {
        // Browser mode
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.pdf';
        input.onchange = async (e: any) => {
          const file = e.target.files?.[0];
          if (file) {
            addLog(`📄 Selected PDF for extraction: ${file.name}`);
            setUploadedPdfFileForExtraction(file);
            const rawAssignmentName = file.name.replace(/\.pdf$/i, '').trim();
            const displayName = formatAssignmentDisplayName(rawAssignmentName, selectedClass);
            setLastProcessedAssignment({
              name: displayName,
              className: selectedClass,
              zipPath: ''
            });
            addLog(`✅ PDF set for extraction. Click "EXTRACT GRADES" to process.`);
          }
        };
        input.click();
      }
    } catch (error) {
      addLog(`❌ Error selecting PDF: ${error}`);
    }
  };

  // Handle PDF file selection for split
  const handleSelectPdfFile = async () => {
    if (!requireClass()) return;

    try {
      if ((window as any).electronAPI?.showOpenDialog) {
        let pathInfo = pdfsFolderPath;
        if (!pathInfo) {
          pathInfo = await getPdfsFolderPath(drive, selectedClass);
          if (pathInfo) {
            setPdfsFolderPath(pathInfo);
          }
        }
        
        const dialogOptions: any = {
          filters: [{ name: 'PDF Files', extensions: ['pdf'] }],
          properties: ['openFile']
        };
        
        if (pathInfo && pathInfo.existingPath) {
          dialogOptions.defaultPath = pathInfo.existingPath;
        }
        
        const result = await (window as any).electronAPI.showOpenDialog(dialogOptions);
        
        if (result && !result.canceled && result.filePaths && result.filePaths.length > 0) {
          const filePath = result.filePaths[0];
          const fileName = filePath.split(/[/\\]/).pop() || '';
          addLog(`📄 Selected: ${fileName}`);
          
          const rawAssignmentName = fileName.replace(/\.pdf$/i, '').trim();
          const displayName = formatAssignmentDisplayName(rawAssignmentName, selectedClass);
          
          setLastProcessedAssignment({
            name: displayName,
            className: selectedClass,
            zipPath: filePath
          });
          
          addLog(`✅ PDF set as current assignment. Click "SPLIT PDF AND REZIP" to process.`);
        }
      } else {
        // Browser mode
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.pdf';
        input.onchange = async (e: any) => {
          const file = e.target.files?.[0];
          if (file) {
            addLog(`📄 Selected: ${file.name}`);
            setUploadedPdfFile(file);
            const rawAssignmentName = file.name.replace(/\.pdf$/i, '').trim();
            const displayName = formatAssignmentDisplayName(rawAssignmentName, selectedClass);
            setLastProcessedAssignment({
              name: displayName,
              className: selectedClass,
              zipPath: ''
            });
            addLog(`✅ PDF set as current assignment. Click "SPLIT PDF AND REZIP" to process.`);
          }
        };
        input.click();
      }
    } catch (error) {
      addLog(`❌ Error selecting PDF: ${error}`);
    }
  };
  
  // Handle PDF upload and split (for browser mode)
  const handleSplitPdfUpload = async (file: File) => {
    if (!requireClass()) return;

    setSplitting(true);
    addLog('📦 Starting PDF split and rezip...');
    
    try {
      const result = await splitPdfUpload(drive, selectedClass, file, addLog);
      
      if (!result.success) {
        displayError(result.error, addLog);
      }
    } catch (error) {
      displayError(error instanceof Error ? error.message : 'Unknown error', addLog);
    } finally {
      setSplitting(false);
    }
  };

  // Split PDF and rezip
  const handleSplitPdf = async (assignmentName: string | null = null, pdfPath: string | null = null) => {
    if (!requireClass()) return;

    if (!pdfPath && uploadedPdfFile && uploadedPdfFile.name) {
      await handleSplitPdfUpload(uploadedPdfFile);
      return;
    }

    setSplitting(true);
    addLog('📦 Starting PDF split and rezip...');
    
    try {
      let finalAssignmentName = assignmentName;
      
      if (!finalAssignmentName && pdfPath) {
        const filename = pdfPath.split(/[/\\]/).pop() || '';
        finalAssignmentName = filename.replace(/\.pdf$/i, '').trim();
      } else if (!finalAssignmentName && lastProcessedAssignment && lastProcessedAssignment.className === selectedClass) {
        finalAssignmentName = lastProcessedAssignment.name;
      }
      
      const result = await splitPdf(drive, selectedClass, finalAssignmentName, pdfPath, addLog);
      
      if (!result.success) {
        displayError(result.error, addLog);
      }
    } catch (error) {
      displayError(error instanceof Error ? error.message : 'Unknown error', addLog);
    } finally {
      setSplitting(false);
    }
  };

  // Open folder
  const handleOpenFolder = async () => {
    if (!requireClass()) return;
    
    try {
      const openClassFolderOnly = !lastProcessedAssignment || lastProcessedAssignment.className !== selectedClass;
      const result = await openFolder(drive, selectedClass, addLog, openClassFolderOnly);
      
      if (result.success) {
        if (openClassFolderOnly) {
          addLog('✅ Class roster folder opened');
        } else {
          addLog('✅ Grade processing folder opened');
        }
      } else {
        if (result.error?.includes('No grade processing folder found')) {
          addLog('❌ No grade processing folder found');
        } else {
          addLog(`❌ ${result.error}`);
        }
      }
    } catch (error) {
      addLog(`❌ ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  // Open class roster folder
  const handleOpenClassRosterFolder = async () => {
    if (!requireClass()) return;
    
    try {
      const result = await openFolder(drive, selectedClass, addLog, true);
      
      if (result.success) {
        addLog('📂 Class roster folder opened');
      } else {
        addLog(`❌ ${result.error}`);
      }
    } catch (error) {
      addLog(`❌ ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  // Clear all data
  const handleClearAllData = async () => {
    if (!requireClass()) return;

    if (lastProcessedAssignment && lastProcessedAssignment.className === selectedClass) {
      const assignmentName = lastProcessedAssignment.name;
      const folderDisplayName = formatAssignmentFolderName(assignmentName, selectedClass);
      
      setClearOptionsConfig({
        title: 'Clear Current Assignment',
        message: `Select how to clear "${folderDisplayName}":`,
        hasCurrentAssignment: true,
        onConfirm: async (option: ClearOption) => {
          setShowClearOptions(false);
          setClearing(true);
          addLog('🗑️ Starting cleanup...');
          
          try {
            let saveFoldersAndPdf = false;
            let saveCombinedPdf = false;
            let deleteEverything = false;
            let deleteArchivedToo = false;
            
            if (option === 'saveFoldersAndPdf') {
              saveFoldersAndPdf = true;
            } else if (option === 'saveCombinedPdf') {
              saveCombinedPdf = true;
            } else if (option === 'deleteEverything') {
              deleteArchivedToo = true;
            }
            
            const result = await clearAllData(
              drive, 
              selectedClass, 
              assignmentName, 
              saveFoldersAndPdf, 
              saveCombinedPdf,
              deleteEverything,
              deleteArchivedToo,
              addLog
            );
            
            if (result.success) {
              setLastProcessedAssignment(null);
            } else {
              displayError(result.error, addLog);
            }
          } catch (error) {
            displayError(error instanceof Error ? error.message : 'Unknown error', addLog);
          } finally {
            setClearing(false);
          }
        }
      });
      setShowClearOptions(true);
      return;
    }

    try {
      const result = await listProcessingFolders(drive, selectedClass);
      
      if (result.success && result.folders) {
        if (result.folders.length === 0) {
          addLog('❌ No processing or archived folders found for this class');
          return;
        }
        
        setProcessingFolders(result.folders);
        setSelectedAssignments(new Set());
        setWasSelectAllUsed(false);
        setShowAssignmentSelection(true);
      } else {
        addLog('❌ No processing or archived folders found for this class');
      }
    } catch (error) {
      displayError(error instanceof Error ? error.message : 'Unknown error', addLog);
    }
  };
  
  // Handle assignment selection from modal
  const handleAssignmentSelection = () => {
    if (selectedAssignments.size === 0) {
      addLog('❌ No assignments selected');
      return;
    }
    
    const assignmentsList: string[] = Array.from(selectedAssignments);
    
    const unarchivedCount = processingFolders.filter(f => 
      f.name.toLowerCase().startsWith('grade processing ')
    ).length;
    const allCount = processingFolders.length;
    
    if (wasSelectAllUsed && (assignmentsList.length === unarchivedCount || assignmentsList.length === allCount)) {
      setShowAssignmentSelection(false);
      setClearOptionsConfig({
        title: 'Clear All Assignments',
        message: `Select how to clear ${assignmentsList.length} assignment(s):`,
        hasCurrentAssignment: false,
        onBack: () => {
          setShowClearOptions(false);
          setShowAssignmentSelection(true);
        },
        onConfirm: async (option: ClearOption) => {
          await executeClearForAssignments(assignmentsList, option);
        }
      });
      setShowClearOptions(true);
      return;
    }
    
    setShowAssignmentSelection(false);
    setClearOptionsConfig({
      title: 'Clear Assignment',
      message: `Select how to clear ${assignmentsList.length} assignment(s):`,
      hasCurrentAssignment: false,
      onBack: () => {
        setShowClearOptions(false);
        setShowAssignmentSelection(true);
      },
      onConfirm: async (option: ClearOption) => {
        await executeClearForAssignments(assignmentsList, option);
      }
    });
    setShowClearOptions(true);
  };
  
  // Helper to execute clear for assignments (deduplicated logic)
  const executeClearForAssignments = async (assignmentsList: string[], option: ClearOption) => {
    setShowClearOptions(false);
    setClearing(true);
    addLog('🗑️ Starting cleanup...');
    
    try {
      let saveFoldersAndPdf = false;
      let saveCombinedPdf = false;
      let deleteEverything = false;
      let deleteArchivedToo = false;
      
      if (option === 'saveFoldersAndPdf') {
        saveFoldersAndPdf = true;
      } else if (option === 'saveCombinedPdf') {
        saveCombinedPdf = true;
      } else if (option === 'deleteEverything') {
        deleteEverything = true;
      }
      
      let successCount = 0;
      let failCount = 0;
      
      if (deleteEverything) {
        const result = await clearAllData(
          drive, 
          selectedClass, 
          assignmentsList[0] as string,
          saveFoldersAndPdf, 
          saveCombinedPdf,
          deleteEverything,
          deleteArchivedToo,
          addLog
        );
        
        if (result.success) {
          successCount = assignmentsList.length;
        } else {
          failCount = assignmentsList.length;
          displayError(`  ❌ Failed: ${result.error || 'Unknown error'}`, addLog);
        }
      } else {
        for (const assignmentName of assignmentsList) {
          const result = await clearAllData(
            drive, 
            selectedClass, 
            assignmentName as string, 
            saveFoldersAndPdf, 
            saveCombinedPdf,
            deleteEverything,
            deleteArchivedToo,
            addLog
          );
          
          if (result.success) {
            successCount++;
          } else {
            failCount++;
            displayError(`  ❌ Failed: ${result.error || 'Unknown error'}`, addLog);
          }
        }
      }
      
      if (lastProcessedAssignment && selectedAssignments.has(lastProcessedAssignment.name)) {
        setLastProcessedAssignment(null);
      }
    } catch (error) {
      displayError(error instanceof Error ? error.message : 'Unknown error', addLog);
    } finally {
      setClearing(false);
    }
  };
  
  // Handle assignment selection modal close
  const handleAssignmentModalClose = () => {
    setShowAssignmentSelection(false);
    setSelectedAssignments(new Set());
    setWasSelectAllUsed(false);
    setClearing(false);
  };
  
  // Toggle assignment selection
  const handleToggleAssignment = (assignmentName: string) => {
    setSelectedAssignments(prev => {
      const newSet = new Set(prev);
      if (newSet.has(assignmentName)) {
        newSet.delete(assignmentName);
      } else {
        newSet.add(assignmentName);
      }
      if (wasSelectAllUsed && newSet.size !== processingFolders.length) {
        setWasSelectAllUsed(false);
      }
      return newSet;
    });
  };
  
  // Select all assignments
  const handleSelectAll = (folderNames?: string[]) => {
    if (folderNames) {
      setSelectedAssignments(new Set(folderNames));
    } else {
      setSelectedAssignments(new Set(processingFolders.map(f => f.name)));
    }
    setWasSelectAllUsed(true);
  };
  
  // Deselect all assignments
  const handleDeselectAll = () => {
    setSelectedAssignments(new Set());
    setWasSelectAllUsed(false);
  };

  // Email all students
  const handleEmailAll = async () => {
    if (!selectedClass) return;
    addLog('📧 Loading students for email...');
    try {
      const students = await loadStudentsForEmail();
      addLog(`✅ Loaded ${students.length} students`);
      setEmailStudents(students);
      setEmailModalMode('all');
      setShowEmailModal(true);
    } catch (error) {
      addLog(`❌ Error loading students: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  // Email students without assignment
  const handleEmailWithoutAssignment = async () => {
    if (!selectedClass) return;
    addLog('📧 Loading students without assignment...');
    try {
      const students = await loadStudentsForEmail();
      setEmailStudents(students);
      setEmailModalMode('without-assignment');
      setShowEmailModal(true);
    } catch (error) {
      addLog(`❌ Error loading students: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  return {
    handleClassChange,
    handleOpenDownloads,
    handleProcessQuizzes,
    handleZipSelection,
    handleZipModalClose,
    handleZipModalSelect,
    handleCompletionZipSelection,
    handleProcessCompletion,
    handleExtractGrades,
    handleSelectPdfFileForExtraction,
    handleSelectPdfFile,
    handleSplitPdfUpload,
    handleSplitPdf,
    handleOpenFolder,
    handleOpenClassRosterFolder,
    handleClearAllData,
    handleAssignmentSelection,
    handleAssignmentModalClose,
    handleToggleAssignment,
    handleSelectAll,
    handleDeselectAll,
    handleEmailAll,
    handleEmailWithoutAssignment,
    loadStudentsForEmail
  };
}
