#!/usr/bin/env python3
"""
Test Log Viewer GUI for D2L Assignment Assistant

A mouse-only interface for previewing log outputs for different scenarios.
Select an action and scenario from dropdowns, click Run, and see the logs.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import os
import sys

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import config reader to get actual paths
try:
    from config_reader import get_downloads_path
    DOWNLOADS_PATH = get_downloads_path()
except ImportError:
    DOWNLOADS_PATH = os.path.join(os.path.expanduser('~'), 'Downloads')


# =============================================================================
# CONSTANTS
# =============================================================================

# Window dimensions
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700
WINDOW_MIN_WIDTH = 800
WINDOW_MIN_HEIGHT = 500
LEFT_PANEL_WIDTH = 280

# Colors (VS Code Dark theme inspired)
COLOR_BG = "#1e1e1e"
COLOR_FG = "#d4d4d4"
COLOR_SUCCESS = "#4ec9b0"
COLOR_ERROR = "#f14c4c"
COLOR_WARNING = "#cca700"
COLOR_INFO = "#569cd6"
COLOR_ACTION = "#ce9178"
COLOR_DIM = "#808080"

# Fonts
FONT_MAIN = ("Segoe UI", 10)
FONT_HEADER = ("Segoe UI", 14, "bold")
FONT_BOLD = ("Segoe UI", 10, "bold")
FONT_SMALL = ("Segoe UI", 8)
FONT_MONO = ("Consolas", 11)

# Common error message suffix
REQUIRED_COLUMNS_MSG = (
    "Please download a fresh import file from D2L that includes all required columns:\n"
    "OrgDefinedId, Username, First Name, Last Name, and Email."
)


# =============================================================================
# REAL LOG SCENARIOS - Based on actual app output
# =============================================================================

# These match what the user actually sees in the app
MOCK_LOGS = {
    "Process Quizzes": {
        "Success": [
            "✅ Class loaded: TTH 11-1220 FM 4202",
            "🔍 Searching for assignment ZIP in Downloads...",
            "📦 Processing: Quiz 4 (7.1 - 7.4) Download Dec 12, 2025 446 PM.zip",
            "✓ Using: Quiz 4 (7.1 - 7.4) Download Dec 12, 2025 446 PM.zip",
            "Existing folder found, creating backup...",
            "to: grade processing - backup - 2025-12-13_21-20-13",
            "Backup created successfully",
            "Assignment: Quiz 4 (7.1 - 7.4)",
            "✅ Extracted 26 student folders",
            "Loaded Import File: 26 students",
            "✅ Combined PDF created!",
            "✅ Quiz processing completed!",
        ],
        
        "Error - No ZIP files": [
            "✅ Class loaded: TTH 11-1220 FM 4202",
            "🔍 Searching for assignment ZIP in Downloads...",
            f"❌ No ZIP files found in {DOWNLOADS_PATH}",
            "",
            "Please download the quiz submissions first",
            f"and put them in: {DOWNLOADS_PATH}",
        ],
        
        "Error - Multiple ZIP files (shows modal)": [
            "✅ Class loaded: TTH 11-1220 FM 4202",
            "🔍 Searching for assignment ZIP in Downloads...",
            "",
            "(Multiple ZIP files found - selection modal appears)",
            "",
            "User selects: Quiz 4 (7.1 - 7.4) Download.zip",
            "",
            "📦 Processing: Quiz 4 (7.1 - 7.4) Download.zip",
            "✅ Extracted 26 student folders",
            "Loaded Import File: 26 students",
            "✅ Combined PDF created!",
            "✅ Quiz processing completed!",
        ],
        
        "Error - Wrong ZIP": [
            "✅ Class loaded: TTH 11-1220 FM 4202",
            "🔍 Searching for assignment ZIP in Downloads...",
            "📦 Processing: Random File.zip",
            "",
            "❌ Zip file does not contain student assignments",
        ],
        
        "Error - Wrong Class": [
            "✅ Class loaded: TTH 11-1220 FM 4202",
            "🔍 Searching for assignment ZIP in Downloads...",
            "📦 Processing: Quiz 4 Download.zip",
            "✅ Extracted 25 student folders",
            "Loaded Import File: 30 students",
            "",
            "❌ Zip file does not contain students from TTH 11-1220 FM 4202",
        ],
        
        "Error - Corrupted ZIP": [
            "✅ Class loaded: TTH 11-1220 FM 4202",
            "🔍 Searching for assignment ZIP in Downloads...",
            "📦 Processing: Quiz 4 Download.zip",
            "",
            "❌ This file can't be opened",
        ],
        
        "Error - No class selected": [
            "❌ Please select a class first",
        ],
        
        "With duplicate submission": [
            "✅ Class loaded: TTH 11-1220 FM 4202",
            "🔍 Searching for assignment ZIP in Downloads...",
            "📦 Processing: Quiz 4 Download.zip",
            "✅ Extracted 27 student folders",
            "Loaded Import File: 26 students",
            "",
            "   Jane Doe: Found newer submission (Jan 15, 2:45 PM), using that",
            "",
            "✅ Combined PDF created!",
            "✅ Quiz processing completed!",
        ],
        
        "With unreadable file (image)": [
            "✅ Class loaded: TTH 11-1220 FM 4202",
            "🔍 Searching for assignment ZIP in Downloads...",
            "📦 Processing: Quiz 4 Download.zip",
            "✅ Extracted 26 student folders",
            "Loaded Import File: 26 students",
            "",
            "   Jane Doe: image file → unreadable",
            "",
            "✅ Combined PDF created!",
            "✅ Quiz processing completed!",
        ],
        
        "With missing submission": [
            "✅ Class loaded: TTH 11-1220 FM 4202",
            "🔍 Searching for assignment ZIP in Downloads...",
            "📦 Processing: Quiz 4 Download.zip",
            "✅ Extracted 25 student folders",
            "Loaded Import File: 26 students",
            "",
            "   Bob Johnson: No submission",
            "",
            "✅ Combined PDF created!",
            "✅ Quiz processing completed!",
        ],
        
        "With multiple PDFs (combined)": [
            "✅ Class loaded: TTH 11-1220 FM 4202",
            "🔍 Searching for assignment ZIP in Downloads...",
            "📦 Processing: Quiz 4 Download.zip",
            "✅ Extracted 26 student folders",
            "Loaded Import File: 26 students",
            "",
            "   Jane Doe: 3 PDFs found, combining",
            "",
            "Students who submitted multiple PDFs (combined automatically):",
            "   • Jane Doe",
            "",
            "✅ Combined PDF created!",
            "✅ Quiz processing completed!",
        ],
    },
    
    "Process Completion": {
        "Success": [
            "✅ Class loaded: ENGL 200",
            "🔍 Searching for assignment ZIP in Downloads...",
            "📦 Processing: Essay 1 Download.zip",
            "✅ Extracted 18 student folders",
            "Loaded Import File: 20 students",
            "✅ Combined PDF created!",
            "✅ Completion processing completed!",
            "✅ Auto-assigned 10 points to all submissions",
        ],
        
        "Error - No ZIP files": [
            "✅ Class loaded: ENGL 200",
            "🔍 Searching for assignment ZIP in Downloads...",
            f"❌ No ZIP files found in {DOWNLOADS_PATH}",
            "",
            "Please download the quiz submissions first",
            f"and put them in: {DOWNLOADS_PATH}",
        ],
        
        "Error - File locked (Excel open)": [
            "✅ Class loaded: ENGL 200",
            "🔍 Searching for assignment ZIP in Downloads...",
            "📦 Processing: Essay 1 Download.zip",
            "✅ Extracted 18 student folders",
            "",
            "❌ Import file is locked. Please close Excel and try again.",
        ],
        
        "Error - Missing Username column": [
            "✅ Class loaded: ENGL 200",
            "🔍 Searching for assignment ZIP in Downloads...",
            "",
            "❌ The import file is missing the Username column.",
            "",
            REQUIRED_COLUMNS_MSG,
        ],
        
        "Error - Missing First Name column": [
            "✅ Class loaded: ENGL 200",
            "🔍 Searching for assignment ZIP in Downloads...",
            "",
            "❌ The import file is missing the First Name column.",
            "",
            REQUIRED_COLUMNS_MSG,
        ],
        
        "Error - Missing Last Name column": [
            "✅ Class loaded: ENGL 200",
            "🔍 Searching for assignment ZIP in Downloads...",
            "",
            "❌ The import file is missing the Last Name column.",
            "",
            REQUIRED_COLUMNS_MSG,
        ],
        
        "Error - Missing Email column": [
            "✅ Class loaded: ENGL 200",
            "🔍 Searching for assignment ZIP in Downloads...",
            "",
            "❌ The import file is missing the Email column.",
            "",
            REQUIRED_COLUMNS_MSG,
        ],
        
        "Error - Missing multiple columns": [
            "✅ Class loaded: ENGL 200",
            "🔍 Searching for assignment ZIP in Downloads...",
            "",
            "❌ The import file is missing the Username, First Name columns.",
            "",
            REQUIRED_COLUMNS_MSG,
        ],
        
        "Error - Import file not found": [
            "✅ Class loaded: ENGL 200",
            "🔍 Searching for assignment ZIP in Downloads...",
            "",
            "❌ Import file not found. Please download a fresh import file from D2L.",
        ],
        
        "Error - File corrupted": [
            "✅ Class loaded: ENGL 200",
            "🔍 Searching for assignment ZIP in Downloads...",
            "",
            "❌ Import file is empty or corrupted. Please download a fresh import file from D2L.",
        ],
        
        "With missing submissions": [
            "✅ Class loaded: ENGL 200",
            "🔍 Searching for assignment ZIP in Downloads...",
            "📦 Processing: Essay 1 Download.zip",
            "✅ Extracted 18 student folders",
            "Loaded Import File: 20 students",
            "",
            "   Jane Doe: No submission → 0 points",
            "   Charlie Brown: No submission → 0 points",
            "",
            "✅ Combined PDF created!",
            "✅ Completion processing completed!",
            "✅ Auto-assigned 10 points to 18 submissions",
            "",
            "❌ STUDENT ERRORS AND WARNINGS:",
            "❌ Jane Doe: No submission",
            "❌ Charlie Brown: No submission",
        ],
    },
    
    "Extract Grades": {
        "Success": [
            "🔬 Starting grade extraction...",
            "",
            "📋 EXTRACTED GRADES:",
            "    1. John Smith: 95 ✅ (confidence: 0.92)",
            "    2. Jane Doe: 87 ⚠️ (confidence: 0.65)",
            "    3. Bob Johnson: 100 ✅ (confidence: 0.98)",
            "    4. Alice Williams: 92 ✅ (confidence: 0.89)",
            "",
            "📊 Processed 26 students",
            "",
            "✅ Grade extraction complete!",
            "",
            "⚠️ ISSUES FOUND (Please Review):",
            "   ⚠️ Jane Doe: 87 (low confidence: 0.65 – needs verification)",
            "",
            "📋 Open Import File",
        ],
        
        "Error - Missing Username column": [
            "🔬 Starting grade extraction...",
            "",
            "❌ The import file is missing the Username column.",
            "",
            REQUIRED_COLUMNS_MSG,
        ],
        
        "Error - Missing First Name column": [
            "🔬 Starting grade extraction...",
            "",
            "❌ The import file is missing the First Name column.",
            "",
            REQUIRED_COLUMNS_MSG,
        ],
        
        "Error - Missing Last Name column": [
            "🔬 Starting grade extraction...",
            "",
            "❌ The import file is missing the Last Name column.",
            "",
            REQUIRED_COLUMNS_MSG,
        ],
        
        "Error - Missing multiple columns": [
            "🔬 Starting grade extraction...",
            "",
            "❌ The import file is missing the Username, Email columns.",
            "",
            REQUIRED_COLUMNS_MSG,
        ],
        
        "Error - File not found": [
            "🔬 Starting grade extraction...",
            "",
            "❌ Import file not found. Please download a fresh import file from D2L.",
        ],
        
        "Error - File locked": [
            "🔬 Starting grade extraction...",
            "",
            "❌ Import file is locked. Please close Excel and try again.",
        ],
        
        "Error - File corrupted": [
            "🔬 Starting grade extraction...",
            "",
            "❌ Import file is empty or corrupted. Please download a fresh import file from D2L.",
        ],
        
        "Error - No grades found in PDF": [
            "🔬 Starting grade extraction...",
            "📊 Scanning 26 pages for grades",
            "🔍 Extracting names and grades...",
            "",
            "❌ No grades were extracted from the PDF",
            "",
            "The OCR could not find any grade values.",
            "Make sure you're using the Combined PDF that contains student scores.",
        ],
        
        "Error - Wrong file or class": [
            "🔬 Starting grade extraction...",
            "",
            "❌ Oops. You've chosen the wrong file or class. Try again.",
        ],
        
        "Error - PDF conversion failed": [
            "🔬 Starting grade extraction...",
            "",
            "❌ Could not convert PDF to images: Poppler not found or PDF is invalid",
            "",
            "This usually means the PDF file is corrupted or not a valid PDF.",
        ],
    },
    
    "Split PDF & Rezip": {
        "Success": [
            "📦 Starting PDF split and rezip...",
            "✅ Successfully split PDF for 26 students",
            "✅ Created ZIP file: Quiz 4 (7.1 - 7.4) Download.zip",
            "✅ Split PDF and rezip completed!",
        ],
        
        "Error - Failed": [
            "📦 Starting PDF split and rezip...",
            "❌ Split PDF failed",
        ],
    },
    
    "Open Folder": {
        "Success": [
            "📂 Opening grade processing folder...",
            "✅ Grade processing folder opened!",
        ],
        
        "Error - No processing folder": [
            "📂 Opening grade processing folder...",
            "❌ No grade processing folder found",
        ],
    },
    
    "Clear Data": {
        "Success": [
            "🗑️ Clearing all processing data...",
            "✅ All data cleared successfully!",
        ],
    },
    
    "Load Classes": {
        "Success": [
            "📂 Loading classes from Rosters etc folder...",
            "✅ Found 5 classes",
        ],
        
        "Error - Folder not found": [
            "📂 Loading classes from Rosters etc folder...",
            "❌ Could not find roster folder",
        ],
    },
    
    "Open Downloads": {
        "Success": [
            "📁 Opening Downloads folder...",
            "✅ Downloads folder opened successfully!",
        ],
    },
}


# =============================================================================
# GUI APPLICATION
# =============================================================================

class TestLogViewerGUI:
    """
    GUI application for previewing log outputs for different scenarios.
    
    Allows testing the application's response to various conditions
    (success, errors, edge cases) without running real data.
    """
    
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("D2L Assignment Assistant - Test Log Viewer")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        
        # Configure style
        style = ttk.Style()
        style.configure("TLabel", font=FONT_MAIN)
        style.configure("TButton", font=FONT_MAIN)
        style.configure("Header.TLabel", font=FONT_HEADER)
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main container with horizontal layout
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # =====================================================================
        # LEFT SIDE PANEL - Controls
        # =====================================================================
        left_panel = ttk.Frame(main_frame, width=LEFT_PANEL_WIDTH)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)  # Keep fixed width
        
        # Header
        header = ttk.Label(
            left_panel, 
            text="Test Log Viewer", 
            style="Header.TLabel"
        )
        header.pack(pady=(0, 5))
        
        # Description
        desc = ttk.Label(
            left_panel,
            text="Select an action and scenario,\nthen click Run Test.",
            foreground="gray",
            justify=tk.CENTER
        )
        desc.pack(pady=(0, 20))
        
        # Separator
        ttk.Separator(left_panel, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # Action selection
        ttk.Label(left_panel, text="Action:", font=FONT_BOLD).pack(anchor=tk.W, pady=(10, 5))
        
        self.action_var = tk.StringVar()
        self.action_combo = ttk.Combobox(
            left_panel, 
            textvariable=self.action_var,
            state="readonly",
            width=35
        )
        self.action_combo["values"] = list(MOCK_LOGS.keys())
        self.action_combo.pack(fill=tk.X, pady=(0, 15))
        self.action_combo.bind("<<ComboboxSelected>>", self.on_action_changed)
        
        # Scenario selection
        ttk.Label(left_panel, text="Scenario:", font=FONT_BOLD).pack(anchor=tk.W, pady=(10, 5))
        
        self.scenario_var = tk.StringVar()
        self.scenario_combo = ttk.Combobox(
            left_panel,
            textvariable=self.scenario_var,
            state="readonly",
            width=35
        )
        self.scenario_combo.pack(fill=tk.X, pady=(0, 20))
        
        # Separator
        ttk.Separator(left_panel, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # Run button (large)
        self.run_button = ttk.Button(
            left_panel,
            text="▶  Run Test",
            command=self.run_test
        )
        self.run_button.pack(fill=tk.X, pady=(15, 10), ipady=10)
        
        # Clear button
        self.clear_button = ttk.Button(
            left_panel,
            text="Clear Log",
            command=self.clear_output
        )
        self.clear_button.pack(fill=tk.X, pady=(0, 10), ipady=5)
        
        # Spacer to push info to bottom
        spacer = ttk.Frame(left_panel)
        spacer.pack(fill=tk.BOTH, expand=True)
        
        # Info at bottom - show current downloads path
        ttk.Separator(left_panel, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        info_label = ttk.Label(
            left_panel,
            text=f"Downloads folder:\n{DOWNLOADS_PATH}",
            foreground="gray",
            font=FONT_SMALL,
            justify=tk.CENTER,
            wraplength=LEFT_PANEL_WIDTH - 20
        )
        info_label.pack(pady=(5, 0))
        
        # =====================================================================
        # RIGHT SIDE - Log Output (takes remaining space)
        # =====================================================================
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Label for output
        output_label = ttk.Label(right_panel, text="Log Output:", font=FONT_BOLD)
        output_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Scrolled text widget for logs (full height)
        self.log_text = scrolledtext.ScrolledText(
            right_panel,
            wrap=tk.WORD,
            font=FONT_MONO,
            bg=COLOR_BG,
            fg=COLOR_FG,
            insertbackground="white",
            state=tk.DISABLED
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags for coloring
        self.log_text.tag_configure("success", foreground=COLOR_SUCCESS)
        self.log_text.tag_configure("error", foreground=COLOR_ERROR)
        self.log_text.tag_configure("warning", foreground=COLOR_WARNING)
        self.log_text.tag_configure("info", foreground=COLOR_INFO)
        self.log_text.tag_configure("action", foreground=COLOR_ACTION)
        self.log_text.tag_configure("dim", foreground=COLOR_DIM)
        
        # Set default selections
        if MOCK_LOGS:
            first_action = list(MOCK_LOGS.keys())[0]
            self.action_var.set(first_action)
            self.update_scenarios(first_action)
    
    def on_action_changed(self, event=None) -> None:
        """Update scenario dropdown when action changes."""
        action = self.action_var.get()
        self.update_scenarios(action)
    
    def update_scenarios(self, action: str) -> None:
        """Update the scenario dropdown based on selected action."""
        if action in MOCK_LOGS:
            scenarios = list(MOCK_LOGS[action].keys())
            self.scenario_combo["values"] = scenarios
            if scenarios:
                self.scenario_var.set(scenarios[0])
    
    def run_test(self) -> None:
        """Display the mock logs for the selected scenario."""
        action = self.action_var.get()
        scenario = self.scenario_var.get()
        
        if not action or not scenario:
            return
        
        logs = MOCK_LOGS.get(action, {}).get(scenario, ["No logs available for this scenario."])
        
        # Clear previous output
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        
        # Insert logs with formatting
        for line in logs:
            self.insert_formatted_line(line)
        
        self.log_text.config(state=tk.DISABLED)
        self.log_text.see(1.0)  # Scroll to top
    
    def insert_formatted_line(self, line: str) -> None:
        """Insert a line with appropriate formatting/colors based on emoji prefixes."""
        # Success messages (green checkmark)
        if line.startswith("✅") or line.startswith("✓"):
            self.log_text.insert(tk.END, line + "\n", "success")
        # Error messages (red X)
        elif line.startswith("❌"):
            self.log_text.insert(tk.END, line + "\n", "error")
        # Warning messages (yellow warning)
        elif line.startswith("⚠️") or "⚠️" in line:
            self.log_text.insert(tk.END, line + "\n", "warning")
        # Search/processing actions (blue)
        elif line.startswith("🔍") or line.startswith("🔬") or line.startswith("📦"):
            self.log_text.insert(tk.END, line + "\n", "info")
        # Folder/file actions (orange)
        elif line.startswith("📂") or line.startswith("📁") or line.startswith("📋") or line.startswith("📄") or line.startswith("📊"):
            self.log_text.insert(tk.END, line + "\n", "action")
        # Clear data (magenta)
        elif line.startswith("🗑️"):
            self.log_text.insert(tk.END, line + "\n", "action")
        # Indented messages (dimmed)
        elif line.startswith("   ") or line.startswith("    "):
            if "❌" in line:
                self.log_text.insert(tk.END, line + "\n", "error")
            elif "⚠️" in line:
                self.log_text.insert(tk.END, line + "\n", "warning")
            elif "✅" in line:
                self.log_text.insert(tk.END, line + "\n", "success")
            else:
                self.log_text.insert(tk.END, line + "\n", "dim")
        # Parenthetical notes
        elif line.startswith("("):
            self.log_text.insert(tk.END, line + "\n", "dim")
        # Default - normal text
        else:
            self.log_text.insert(tk.END, line + "\n")
    
    def clear_output(self) -> None:
        """Clear the log output area."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)


def main() -> None:
    """Launch the Test Log Viewer GUI application."""
    root = tk.Tk()
    TestLogViewerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
