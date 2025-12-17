import React, { useState } from 'react';
import { FolderOpen, ArrowRight, ArrowLeft, Check } from 'lucide-react';
import { selectFolder, addClass, ClassData } from '../services/quizGraderService';

interface ClassSetupWizardProps {
  isDark: boolean;
  onComplete: (classes: ClassData[]) => void;
  onCancel: () => void;
  metalButtonClass: (isDark: boolean) => string;
  metalButtonStyle: (isDark: boolean) => React.CSSProperties | undefined;
  initialClasses: ClassData[];
}

interface ClassInput {
  value: string;
  label: string;
  rosterFolderPath: string;
  error?: string;
}

export default function ClassSetupWizard({
  isDark,
  onComplete,
  onCancel,
  metalButtonClass,
  metalButtonStyle,
  initialClasses,
}: ClassSetupWizardProps) {
  const [step, setStep] = useState<'count' | 'input' | 'saving'>('count');
  const [classCount, setClassCount] = useState<number>(1);
  const [currentClassIndex, setCurrentClassIndex] = useState<number>(0);
  const [classInputs, setClassInputs] = useState<ClassInput[]>([]);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string>('');

  const handleCountSubmit = () => {
    if (classCount < 1 || classCount > 6) {
      setError('Please select a number between 1 and 6');
      return;
    }
    
    // Initialize class inputs
    const inputs: ClassInput[] = [];
    for (let i = 0; i < classCount; i++) {
      inputs.push({
        value: '',
        label: '',
        rosterFolderPath: '',
      });
    }
    setClassInputs(inputs);
    setStep('input');
    setError('');
  };

  const handleBrowseFolder = async () => {
    try {
      setError(''); // Clear any errors
      
      // Check if Electron API is available
      const electronAPI = (window as any).electronAPI;
      
      if (electronAPI?.showOpenDialog) {
        // Use Electron's native dialog
        const result = await electronAPI.showOpenDialog({
          properties: ['openDirectory'],
          title: 'Select Roster Folder',
          buttonLabel: 'Select Folder'
        });
        
        if (result && !result.canceled && result.filePaths && result.filePaths.length > 0) {
          const folderPath = result.filePaths[0];
          const folderName = folderPath.split(/[\\/]/).pop() || '';
          
          // Check if this folder already exists in any class
          const isDuplicate = initialClasses.some(cls => 
            cls.value === folderName || 
            cls.rosterFolderPath.toLowerCase() === folderPath.toLowerCase()
          );
          
          // Update current class input with FULL PATH
          const updated = [...classInputs];
          updated[currentClassIndex] = {
            ...updated[currentClassIndex],
            rosterFolderPath: folderPath,
            label: updated[currentClassIndex].label || folderName,
            value: folderName,
            error: isDuplicate ? 'This folder already exists in your classes' : undefined,
          };
          setClassInputs(updated);
          
          if (isDuplicate) {
            setError('❌ This folder already exists in your classes. Please select a different folder.');
          }
        }
      } else {
        // Fallback: Use backend API (PowerShell dialog)
        const result = await selectFolder();
        
        if (result.success && result.folderPath) {
          const folderPath = result.folderPath;
          const folderName = folderPath.split(/[\\/]/).pop() || '';
          
          // Check if this folder already exists in any class
          const isDuplicate = initialClasses.some(cls => 
            cls.value === folderName || 
            cls.rosterFolderPath.toLowerCase() === folderPath.toLowerCase()
          );
          
          // Update current class input with FULL PATH
          const updated = [...classInputs];
          updated[currentClassIndex] = {
            ...updated[currentClassIndex],
            rosterFolderPath: folderPath,
            label: updated[currentClassIndex].label || folderName,
            value: folderName,
            error: isDuplicate ? 'This folder already exists in your classes' : undefined,
          };
          setClassInputs(updated);
          
          if (isDuplicate) {
            setError('❌ This folder already exists in your classes. Please select a different folder.');
          }
        } else {
          setError(result.error || 'No folder selected');
        }
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to select folder';
      setError(errorMsg);
    }
  };

  const handleInputChange = (field: 'label', value: string) => {
    const updated = [...classInputs];
    updated[currentClassIndex] = {
      ...updated[currentClassIndex],
      [field]: value,
      error: undefined,
    };
    setClassInputs(updated);
  };

  const validateCurrentClass = (): boolean => {
    const current = classInputs[currentClassIndex];
    
    // Check if there's already an error (like duplicate folder)
    if (current.error) {
      setError(current.error);
      return false;
    }
    
    if (!current.rosterFolderPath.trim()) {
      const updated = [...classInputs];
      updated[currentClassIndex] = {
        ...updated[currentClassIndex],
        error: 'Roster folder path is required',
      };
      setClassInputs(updated);
      setError('❌ Roster folder path is required');
      return false;
    }
    
    if (!current.label.trim()) {
      const updated = [...classInputs];
      updated[currentClassIndex] = {
        ...updated[currentClassIndex],
        error: 'Class name is required',
      };
      setClassInputs(updated);
      setError('❌ Class name is required');
      return false;
    }
    
    if (!current.value.trim()) {
      const updated = [...classInputs];
      updated[currentClassIndex] = {
        ...updated[currentClassIndex],
        error: 'Class value is required',
      };
      setClassInputs(updated);
      setError('❌ Class value is required');
      return false;
    }
    
    return true;
  };

  const handleNext = () => {
    if (!validateCurrentClass()) {
      return;
    }
    
    if (currentClassIndex < classInputs.length - 1) {
      setCurrentClassIndex(currentClassIndex + 1);
    } else {
      handleSaveClasses();
    }
  };

  const handlePrevious = () => {
    if (currentClassIndex > 0) {
      setCurrentClassIndex(currentClassIndex - 1);
    }
  };

  const handleSaveClasses = async () => {
    setSaving(true);
    setStep('saving');
    setError('');
    
    try {
      for (const classInput of classInputs) {
        const result = await addClass({
          value: classInput.value,
          label: classInput.label,
          rosterFolderPath: classInput.rosterFolderPath,
        });
        
        // Check for actual success with class data returned
        if (!result.success) {
          throw new Error(result.error || 'Failed to add class');
        }
        
        // Log success message (will be displayed in terminal)
        console.log(`Class "${classInput.label}" added successfully`);
      }
      
      setSaving(false);
      // Call onComplete to close modal and refresh
      onComplete([]);  // Parent will reload from backend
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save classes');
      setSaving(false);
      setStep('input');
    }
  };

  const currentClass = classInputs[currentClassIndex];

  return (
    <div className="space-y-6">
      {/* Step 1: How many classes */}
      {step === 'count' && (
        <>
          <div>
            <h3 className={`text-lg font-semibold mb-2 ${isDark ? 'text-cyan-400' : 'text-[#1a2942]'}`}>
              How many classes are you teaching this semester?
            </h3>
            <p className={`text-sm mb-4 ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
              Select the number of classes
            </p>
            
            <select
              value={classCount}
              onChange={(e) => {
                setClassCount(parseInt(e.target.value));
                setError('');
              }}
              className={`px-4 py-3 rounded-lg border text-lg ${
                isDark
                  ? 'bg-[#1a2942] border-[#2a3952] text-gray-300'
                  : 'bg-white border-gray-400 text-gray-800'
              }`}
              style={{ maxWidth: '200px' }}
            >
              <option value="1">1 class</option>
              <option value="2">2 classes</option>
              <option value="3">3 classes</option>
              <option value="4">4 classes</option>
              <option value="5">5 classes</option>
              <option value="6">6 classes</option>
            </select>
            
            {error && (
              <p className="text-red-500 text-sm mt-2">
                {error}
              </p>
            )}
          </div>
          
          <div className="flex gap-3 justify-end">
            <button
              onClick={onCancel}
              className={`px-6 py-2 rounded-lg border ${metalButtonClass(isDark)}`}
              style={metalButtonStyle(isDark)}
            >
              Cancel
            </button>
            <button
              onClick={handleCountSubmit}
              className={`px-6 py-2 rounded-lg border ${metalButtonClass(isDark)} flex items-center gap-2`}
              style={metalButtonStyle(isDark)}
            >
              Next
              <ArrowRight size={16} />
            </button>
          </div>
        </>
      )}

      {/* Step 2: Input class details */}
      {step === 'input' && currentClass && (
        <>
          <div>
            <h3 className={`text-lg font-semibold mb-2 ${isDark ? 'text-cyan-400' : 'text-[#1a2942]'}`}>
              Class {currentClassIndex + 1} of {classInputs.length}
            </h3>
            
            {/* Global error message at top */}
            {error && (
              <div className="mb-4 p-3 rounded-lg bg-red-500/10 border border-red-500/50">
                <p className="text-red-500 text-sm">
                  {error}
                </p>
              </div>
            )}
            
            <div className="space-y-4">
              {/* Roster Folder Path */}
              <div>
                <label className={`block text-sm font-medium mb-2 ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>
                  Roster Folder Path *
                </label>
                <div className="flex gap-2">
                  {currentClass.rosterFolderPath ? (
                    <div className={`flex-1 px-4 py-2 rounded-lg border ${
                      isDark
                        ? 'bg-[#1a2942] border-[#2a3952] text-gray-300'
                        : 'bg-white border-gray-400 text-gray-800'
                    }`}>
                      {currentClass.rosterFolderPath}
                    </div>
                  ) : (
                    <div className={`flex-1 px-4 py-2 rounded-lg border italic ${
                      isDark
                        ? 'bg-[#1a2942] border-[#2a3952] text-gray-500'
                        : 'bg-white border-gray-400 text-gray-500'
                    }`}>
                      No folder selected
                    </div>
                  )}
                  <button
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      handleBrowseFolder();
                    }}
                    type="button"
                    className={`px-4 py-2 rounded-lg border ${metalButtonClass(isDark)} flex items-center gap-2`}
                    style={{
                      ...metalButtonStyle(isDark),
                      cursor: 'pointer',
                      pointerEvents: 'auto'
                    }}
                  >
                    <FolderOpen size={16} />
                    Browse
                  </button>
                </div>
              </div>
              
              {/* Class Name (Label) - Only show after folder is selected */}
              {currentClass.rosterFolderPath && (
                <div>
                  <label className={`block text-sm font-medium mb-2 ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>
                    Class Name (Display) *
                  </label>
                  <input
                    type="text"
                    value={currentClass.label}
                    onChange={(e) => handleInputChange('label', e.target.value)}
                    placeholder="FM 4202 (TTH 11:00-12:20)"
                    className={`w-full px-4 py-2 rounded-lg border ${
                      isDark
                        ? 'bg-[#1a2942] border-[#2a3952] text-gray-300'
                        : 'bg-white border-gray-400 text-gray-800'
                    }`}
                  />
                  <p className={`text-xs mt-1 ${isDark ? 'text-gray-500' : 'text-gray-600'}`}>
                    Defaults to folder name, but you can customize it
                  </p>
                </div>
              )}
              
              {currentClass.error && (
                <p className="text-red-500 text-sm">
                  {currentClass.error}
                </p>
              )}
            </div>
          </div>
          
          <div className="flex gap-3 justify-between">
            <button
              onClick={currentClassIndex === 0 ? onCancel : handlePrevious}
              className={`px-6 py-2 rounded-lg border ${metalButtonClass(isDark)} flex items-center gap-2`}
              style={metalButtonStyle(isDark)}
            >
              <ArrowLeft size={16} />
              {currentClassIndex === 0 ? 'Cancel' : 'Previous'}
            </button>
            <button
              onClick={handleNext}
              className={`px-6 py-2 rounded-lg border ${metalButtonClass(isDark)} flex items-center gap-2`}
              style={metalButtonStyle(isDark)}
            >
              {currentClassIndex === classInputs.length - 1 ? 'Save Classes' : 'Next'}
              {currentClassIndex === classInputs.length - 1 ? <Check size={16} /> : <ArrowRight size={16} />}
            </button>
          </div>
          
          {/* Progress indicator */}
          <div className="flex gap-2 justify-center">
            {classInputs.map((_, index) => (
              <div
                key={index}
                className={`h-2 w-8 rounded-full ${
                  index === currentClassIndex
                    ? isDark ? 'bg-cyan-400' : 'bg-[#1a2942]'
                    : index < currentClassIndex
                    ? isDark ? 'bg-cyan-700' : 'bg-gray-400'
                    : isDark ? 'bg-[#2a3952]' : 'bg-gray-300'
                }`}
              />
            ))}
          </div>
        </>
      )}

      {/* Step 3: Saving */}
      {step === 'saving' && (
        <div className="text-center py-8">
          <div className={`text-lg font-semibold mb-4 ${isDark ? 'text-cyan-400' : 'text-[#1a2942]'}`}>
            {saving ? 'Saving classes...' : '✅ Classes saved successfully!'}
          </div>
          {saving && (
            <div className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
              Please wait...
            </div>
          )}
          {error && (
            <p className="text-red-500 text-sm mt-2">
              {error}
            </p>
          )}
        </div>
      )}
    </div>
  );
}

