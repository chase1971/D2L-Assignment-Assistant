# Refactoring Plan: `Option2.tsx` (D2L Assignment Assistant)

## Problem
`Option2.tsx` is a **1,967-line** React component that contains all state, handlers, business logic, and JSX for the main UI. Key issues:
- **35 useState declarations** crammed into one component
- **~300 lines of duplicated inline mouse event handlers** on ~15 buttons (onMouseEnter/Leave/Down/Up) — despite `useButtonInteractions` hook already existing and being unused
- **~930 lines of action handlers** inline in the component
- **~90 lines of copy-pasted clear logic** in `handleAssignmentSelection` (two nearly identical blocks)
- **3 duplicated "Current Assignment" display blocks** (~20 lines each)

## Strategy: Extract into hooks, a reusable button component, and utils

### New Files

```
src/components/
  MetalButton.tsx                          (reusable button — uses existing useButtonInteractions hook)
  CurrentAssignmentDisplay.tsx             (repeated UI block, extracted)
  utils/
    assignmentUtils.ts                     (pure functions: name formatting, error display)
  hooks/
    useOption2State.ts                     (all 35 useState + useEffects + addLog)
    useOption2Actions.ts                   (all 21 action handlers)
```

### What Each File Contains

#### `MetalButton.tsx` (~60 lines) — **Biggest single win: removes ~300 lines**
A reusable button that wraps the existing `useButtonInteractions` + `useThemeStyles` hooks internally.
```tsx
<MetalButton onClick={handleProcess} disabled={!selectedClass || processing}
  isDark={isDark} loading={processing} loadingText="PROCESSING...">
  PROCESS QUIZZES
</MetalButton>
```
Props: `onClick`, `disabled`, `children`, `isDark`, `variant` ('metal'|'danger'), `loading?`, `loadingText?`, `icon?`, `title?`, `style?`, `className?`, `scaleType?`

Replaces ~40 lines per button (inline styles + 4 mouse handlers + disabled logic) with ~6 lines.

#### `CurrentAssignmentDisplay.tsx` (~25 lines) — removes ~60 lines
The "Current Assignment: 📄 Quiz 1 FM 4202 / None" box used in Extract Grades, Split PDF, and Clear Data cards. Appears 3 times identically.

#### `utils/assignmentUtils.ts` (~80 lines) — removes ~80 lines
Pure functions with zero React dependencies:
- `extractClassCode(className)` — extracts "FM 4202" from "TTH 11-1220 FM 4202"
- `formatAssignmentDisplayName(assignmentName, className)` — cleans and formats
- `formatAssignmentFolderName(assignmentName, className)` — formats as "grade processing [CODE] [NAME]"
- `displayError(error, addLog)` — error formatting/display helper

#### `hooks/useOption2State.ts` (~300 lines) — removes ~280 lines
All state management extracted into a single custom hook:
- All 35 `useState` declarations
- `addLog` function with dedup/filter logic
- `useLogStream(addLog)` call
- Server status polling `useEffect`
- Class loading `useEffect` + `reloadClasses`
- `requireClass()` helper
- Returns typed state object with all values and setters

#### `hooks/useOption2Actions.ts` (~500 lines) — removes ~930 lines
All action handlers, taking the state object as input:
- `handleClassChange`, `handleOpenDownloads`
- `handleProcessQuizzes`, `handleZipSelection`, `handleZipModalClose/Select`
- `handleCompletionZipSelection`, `handleProcessCompletion`
- `handleExtractGrades`, `handleSelectPdfFileForExtraction`, `handleSelectPdfFile`
- `handleSplitPdfUpload`, `handleSplitPdf`
- `handleOpenFolder`, `handleOpenClassRosterFolder`
- `handleClearAllData`, `handleAssignmentSelection` (deduplicated)
- `handleAssignmentModalClose`, `handleToggleAssignment`, `handleSelectAll/DeselectAll`
- `handleEmailAll`, `handleEmailWithoutAssignment`
- `loadStudentsForEmail`

**Key dedup**: The two ~90-line identical blocks in `handleAssignmentSelection` become one shared `executeClearForAssignments()` helper.

### What Stays in Option2.tsx (~200 lines)
A thin orchestrator that:
1. Calls `useOption2State()` → all state
2. Calls `useOption2Actions(state)` → all handlers
3. Returns JSX using `MetalButton`, `CurrentAssignmentDisplay`, `ActionCard`, modals, `NavigationBar`, `LogTerminal`

### Impact Summary

| Extraction | Lines removed from Option2 |
|---|---|
| `MetalButton.tsx` (replaces inline handlers) | ~300 |
| `useOption2Actions.ts` (all handlers) | ~930 |
| `useOption2State.ts` (all state + lifecycle) | ~280 |
| `assignmentUtils.ts` (pure functions) | ~80 |
| `CurrentAssignmentDisplay.tsx` (3 duped blocks) | ~60 |
| Dedup in `handleAssignmentSelection` | ~90 |
| **Option2.tsx: 1,967 → ~200 lines** | **~1,740** |

### Implementation Order
1. **`assignmentUtils.ts`** — zero-risk pure function extraction
2. **`MetalButton.tsx`** — biggest win, replace buttons one card at a time
3. **`CurrentAssignmentDisplay.tsx`** — small presentational extraction
4. **`useOption2State.ts`** — move all state out
5. **`useOption2Actions.ts`** — move all handlers out (with dedup)
6. **Final cleanup of Option2.tsx** — slim orchestrator

### Critical Files
- `src/components/Option2.tsx` — the file being refactored (1,967 → ~200 lines)
- `src/components/hooks/useButtonInteractions.ts` — existing hook, consumed by new MetalButton
- `src/components/hooks/useModal.ts` — existing hook, can optionally replace raw useState modal pairs
- `src/components/hooks/useThemeStyles.ts` — existing hook, consumed by MetalButton
- `src/components/constants/ui-constants.ts` — has disabled button constants for MetalButton
- `src/services/quizGraderService.ts` — service layer imported by useOption2Actions

### Verification
- Run `npm run dev` and confirm the app loads with no errors
- Verify all buttons have correct hover/press/disabled effects
- Test: Process Quizzes, Process Completion, Extract Grades, Split PDF, Clear Data, Email flows
- Verify dark/light mode toggle works correctly
- Confirm all modals open/close properly
