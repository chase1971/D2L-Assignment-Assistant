#!/usr/bin/env python3
"""
Enhanced Log Preview GUI
- Left sidebar: Clickable list of actions
- Middle: List of scenarios with descriptive labels
- Right: Split view - "User Sees" (with examples) | "Developer Code"
"""

import tkinter as tk
from tkinter import ttk, font
import json
import os
import sys
import subprocess

# Fix Windows encoding for emojis
if sys.platform == 'win32':
    import io
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


class LogPreviewGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("D2L Assignment Assistant - Log Preview")
        self.root.geometry("1600x900")
        self.root.minsize(1200, 700)
        
        # Dark theme colors
        self.colors = {
            'bg_dark': '#1e1e1e',
            'bg_medium': '#252526',
            'bg_light': '#2d2d30',
            'bg_highlight': '#094771',
            'fg': '#d4d4d4',
            'fg_dim': '#808080',
            'accent': '#0078d4',
            'success': '#4ec9b0',
            'error': '#f14c4c',
            'warning': '#cca700',
            'info': '#3794ff',
            'border': '#3c3c3c',
        }
        
        self.root.configure(bg=self.colors['bg_dark'])
        
        # Load extracted logs
        self.logs_data = self.load_logs()
        
        # Current selections
        self.current_action = None
        self.current_log = None
        self.scenario_widgets = []
        
        # Setup UI
        self.setup_ui()
        
        # Load initial data
        self.populate_actions()
    
    def load_logs(self):
        """Load extracted_logs.json"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(script_dir, 'extracted_logs.json')
        
        if not os.path.exists(json_path):
            print("extracted_logs.json not found. Running extractor...")
            self.run_extractor()
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {'logs': [], 'logs_by_action': {}, 'actions': []}
    
    def run_extractor(self):
        """Run the log extractor script"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        extractor_path = os.path.join(script_dir, 'log_extractor.py')
        subprocess.run([sys.executable, extractor_path], cwd=script_dir)
    
    def setup_ui(self):
        """Setup the main UI layout"""
        # Main container
        main_frame = tk.Frame(self.root, bg=self.colors['bg_dark'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Header
        header = tk.Frame(main_frame, bg=self.colors['bg_medium'], height=50)
        header.pack(fill=tk.X, pady=(0, 5))
        header.pack_propagate(False)
        
        title = tk.Label(header, text="📋 Log Message Preview", 
                        font=('Segoe UI', 16, 'bold'),
                        bg=self.colors['bg_medium'], fg=self.colors['fg'])
        title.pack(side=tk.LEFT, padx=15, pady=10)
        
        # Refresh button
        refresh_btn = tk.Button(header, text="🔄 Refresh", 
                               font=('Segoe UI', 10),
                               bg=self.colors['accent'], fg='white',
                               relief=tk.FLAT, padx=15, pady=5,
                               command=self.refresh_logs)
        refresh_btn.pack(side=tk.RIGHT, padx=15, pady=10)
        
        # Stats label
        self.stats_label = tk.Label(header, text="", 
                                    font=('Segoe UI', 10),
                                    bg=self.colors['bg_medium'], fg=self.colors['fg_dim'])
        self.stats_label.pack(side=tk.RIGHT, padx=15)
        
        # Content area - 3 panes
        content = tk.Frame(main_frame, bg=self.colors['bg_dark'])
        content.pack(fill=tk.BOTH, expand=True)
        
        # === LEFT PANE - Actions list ===
        left_pane = tk.Frame(content, bg=self.colors['bg_medium'], width=200)
        left_pane.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        left_pane.pack_propagate(False)
        
        # User-facing actions section
        user_actions_label = tk.Label(left_pane, text="USER-FACING ACTIONS", 
                                     font=('Segoe UI', 10, 'bold'),
                                     bg=self.colors['bg_medium'], fg=self.colors['fg_dim'])
        user_actions_label.pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        # User-facing actions container
        user_actions_container = tk.Frame(left_pane, bg=self.colors['bg_medium'])
        user_actions_container.pack(fill=tk.BOTH, expand=True, padx=5)
        
        user_actions_canvas = tk.Canvas(user_actions_container, bg=self.colors['bg_medium'],
                                        highlightthickness=0)
        user_actions_scrollbar = tk.Scrollbar(user_actions_container, orient=tk.VERTICAL,
                                              command=user_actions_canvas.yview)
        self.user_actions_frame = tk.Frame(user_actions_canvas, bg=self.colors['bg_medium'])
        
        self.user_actions_frame.bind('<Configure>', 
            lambda e: user_actions_canvas.configure(scrollregion=user_actions_canvas.bbox('all')))
        
        user_actions_canvas.create_window((0, 0), window=self.user_actions_frame, anchor=tk.NW)
        user_actions_canvas.configure(yscrollcommand=user_actions_scrollbar.set)
        
        user_actions_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        user_actions_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Separator
        separator1 = tk.Frame(left_pane, bg=self.colors['bg_light'], height=2)
        separator1.pack(fill=tk.X, padx=10, pady=10)
        
        # UI Transformations section
        ui_transforms_label = tk.Label(left_pane, text="UI TRANSFORMATIONS", 
                                      font=('Segoe UI', 10, 'bold'),
                                      bg=self.colors['bg_medium'], fg=self.colors['warning'])
        ui_transforms_label.pack(anchor=tk.W, padx=10, pady=(5, 5))
        
        # UI Transformations button
        self.ui_transforms_btn = tk.Button(left_pane, 
                           text="🔗 Clickable Links & Buttons",
                           font=('Segoe UI', 9),
                           bg=self.colors['bg_light'],
                           fg=self.colors['warning'],
                           activebackground=self.colors['bg_highlight'],
                           activeforeground='white',
                           relief=tk.FLAT,
                           anchor=tk.W,
                           padx=10, pady=6,
                           width=22,
                           command=self.show_ui_transformations)
        self.ui_transforms_btn.pack(fill=tk.X, padx=5, pady=1)
        
        # Dynamic Examples button
        self.dynamic_btn = tk.Button(left_pane, 
                           text="🔄 Dynamic Log Examples",
                           font=('Segoe UI', 9),
                           bg=self.colors['bg_light'],
                           fg=self.colors['warning'],
                           activebackground=self.colors['bg_highlight'],
                           activeforeground='white',
                           relief=tk.FLAT,
                           anchor=tk.W,
                           padx=10, pady=6,
                           width=22,
                           command=self.show_dynamic_examples)
        self.dynamic_btn.pack(fill=tk.X, padx=5, pady=1)
        
        # Separator
        separator2 = tk.Frame(left_pane, bg=self.colors['bg_light'], height=2)
        separator2.pack(fill=tk.X, padx=10, pady=10)
        
        # Debugging logs section
        debug_actions_label = tk.Label(left_pane, text="DEBUGGING LOGS", 
                                      font=('Segoe UI', 10, 'bold'),
                                      bg=self.colors['bg_medium'], fg=self.colors['fg_dim'])
        debug_actions_label.pack(anchor=tk.W, padx=10, pady=(5, 5))
        
        # Debugging actions container
        debug_actions_container = tk.Frame(left_pane, bg=self.colors['bg_medium'])
        debug_actions_container.pack(fill=tk.BOTH, expand=True, padx=5)
        
        debug_actions_canvas = tk.Canvas(debug_actions_container, bg=self.colors['bg_medium'],
                                         highlightthickness=0)
        debug_actions_scrollbar = tk.Scrollbar(debug_actions_container, orient=tk.VERTICAL,
                                               command=debug_actions_canvas.yview)
        self.debug_actions_frame = tk.Frame(debug_actions_canvas, bg=self.colors['bg_medium'])
        
        self.debug_actions_frame.bind('<Configure>', 
            lambda e: debug_actions_canvas.configure(scrollregion=debug_actions_canvas.bbox('all')))
        
        debug_actions_canvas.create_window((0, 0), window=self.debug_actions_frame, anchor=tk.NW)
        debug_actions_canvas.configure(yscrollcommand=debug_actions_scrollbar.set)
        
        debug_actions_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        debug_actions_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.action_buttons = {}
        self.debug_action_buttons = {}
        self.is_debug_mode = False
        
        # === MIDDLE PANE - Scenarios list ===
        middle_pane = tk.Frame(content, bg=self.colors['bg_medium'], width=350)
        middle_pane.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        middle_pane.pack_propagate(False)
        
        self.scenarios_label = tk.Label(middle_pane, text="SCENARIOS", 
                                        font=('Segoe UI', 10, 'bold'),
                                        bg=self.colors['bg_medium'], fg=self.colors['fg_dim'])
        self.scenarios_label.pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        # Scenarios list with scrollbar
        scenarios_container = tk.Frame(middle_pane, bg=self.colors['bg_medium'])
        scenarios_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        
        scenarios_canvas = tk.Canvas(scenarios_container, bg=self.colors['bg_medium'],
                                     highlightthickness=0)
        scenarios_scrollbar = tk.Scrollbar(scenarios_container, orient=tk.VERTICAL,
                                           command=scenarios_canvas.yview)
        self.scenarios_frame = tk.Frame(scenarios_canvas, bg=self.colors['bg_medium'])
        
        self.scenarios_frame.bind('<Configure>',
            lambda e: scenarios_canvas.configure(scrollregion=scenarios_canvas.bbox('all')))
        
        scenarios_canvas.create_window((0, 0), window=self.scenarios_frame, anchor=tk.NW)
        scenarios_canvas.configure(yscrollcommand=scenarios_scrollbar.set)
        
        scenarios_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scenarios_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.scenarios_canvas = scenarios_canvas
        
        # === RIGHT PANE - Split view ===
        right_pane = tk.Frame(content, bg=self.colors['bg_dark'])
        right_pane.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # --- TOP: Trigger/Context Section (fixed height) ---
        trigger_frame = tk.Frame(right_pane, bg=self.colors['bg_medium'], height=70)
        trigger_frame.pack(fill=tk.X, pady=(0, 5))
        trigger_frame.pack_propagate(False)
        
        trigger_header = tk.Frame(trigger_frame, bg=self.colors['bg_light'])
        trigger_header.pack(fill=tk.X)
        
        tk.Label(trigger_header, text="📌 WHEN THIS HAPPENS", 
                font=('Segoe UI', 10, 'bold'),
                bg=self.colors['bg_light'], fg=self.colors['warning']).pack(side=tk.LEFT, padx=10, pady=6)
        
        self.trigger_text = tk.Label(trigger_frame, text="Select a scenario to see what triggers it",
                                     font=('Segoe UI', 10),
                                     bg=self.colors['bg_medium'], fg=self.colors['fg'],
                                     wraplength=900, justify=tk.LEFT,
                                     anchor=tk.NW, padx=15, pady=8)
        self.trigger_text.pack(fill=tk.BOTH, expand=True)
        
        # --- BOTTOM: Side-by-side resizable panes ---
        # Using PanedWindow for resizable split
        split_pane = ttk.PanedWindow(right_pane, orient=tk.HORIZONTAL)
        split_pane.pack(fill=tk.BOTH, expand=True)
        
        # LEFT SIDE: User Sees Section
        user_frame = tk.Frame(split_pane, bg=self.colors['bg_medium'])
        split_pane.add(user_frame, weight=1)
        
        user_header = tk.Frame(user_frame, bg=self.colors['bg_light'])
        user_header.pack(fill=tk.X)
        
        tk.Label(user_header, text="👤 USER SEES (Example)", 
                font=('Segoe UI', 10, 'bold'),
                bg=self.colors['bg_light'], fg=self.colors['success']).pack(side=tk.LEFT, padx=10, pady=8)
        
        # User message display with scrollbar
        user_content = tk.Frame(user_frame, bg=self.colors['bg_medium'])
        user_content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        user_scroll = tk.Scrollbar(user_content)
        user_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.user_text = tk.Text(user_content, wrap=tk.WORD,
                                 font=('Consolas', 11),
                                 bg=self.colors['bg_light'], fg=self.colors['fg'],
                                 relief=tk.FLAT, padx=10, pady=10,
                                 state='disabled',
                                 yscrollcommand=user_scroll.set)
        self.user_text.pack(fill=tk.BOTH, expand=True)
        user_scroll.config(command=self.user_text.yview)
        
        # Configure tags for message types
        self.user_text.tag_configure('error', foreground=self.colors['error'])
        self.user_text.tag_configure('success', foreground=self.colors['success'])
        self.user_text.tag_configure('warning', foreground=self.colors['warning'])
        self.user_text.tag_configure('info', foreground=self.colors['info'])
        
        # Configure tags for colorized parts
        self.user_text.tag_configure('emoji', foreground='#ffd700')  # Gold for emojis
        self.user_text.tag_configure('number', foreground='#4ec9b0')  # Teal for numbers
        self.user_text.tag_configure('name', foreground='#9cdcfe')   # Light blue for names
        self.user_text.tag_configure('confidence', foreground='#ce9178')  # Orange for confidence values
        self.user_text.tag_configure('file_path', foreground='#d7ba7d')  # Tan for file paths
        
        # RIGHT SIDE: Developer Code Section
        dev_frame = tk.Frame(split_pane, bg=self.colors['bg_medium'])
        split_pane.add(dev_frame, weight=1)
        
        dev_header = tk.Frame(dev_frame, bg=self.colors['bg_light'])
        dev_header.pack(fill=tk.X)
        
        tk.Label(dev_header, text="💻 DEVELOPER CODE", 
                font=('Segoe UI', 10, 'bold'),
                bg=self.colors['bg_light'], fg=self.colors['info']).pack(side=tk.LEFT, padx=10, pady=8)
        
        self.dev_location = tk.Label(dev_header, text="", 
                                     font=('Segoe UI', 9),
                                     bg=self.colors['bg_light'], fg=self.colors['fg_dim'])
        self.dev_location.pack(side=tk.RIGHT, padx=10, pady=8)
        
        # Developer code display with scrollbar
        dev_content = tk.Frame(dev_frame, bg=self.colors['bg_medium'])
        dev_content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        dev_scroll = tk.Scrollbar(dev_content)
        dev_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.dev_text = tk.Text(dev_content, wrap=tk.WORD,
                               font=('Consolas', 11),
                               bg='#1e1e1e', fg='#d4d4d4',
                               relief=tk.FLAT, padx=15, pady=15,
                               state='disabled',
                               yscrollcommand=dev_scroll.set)
        self.dev_text.pack(fill=tk.BOTH, expand=True)
        dev_scroll.config(command=self.dev_text.yview)
        
        # Syntax highlighting tags
        self.dev_text.tag_configure('comment', foreground='#6a9955')
    
    def populate_actions(self):
        """Populate the actions sidebar with user-facing and debugging sections"""
        # Clear existing buttons
        for widget in self.user_actions_frame.winfo_children():
            widget.destroy()
        for widget in self.debug_actions_frame.winfo_children():
            widget.destroy()
        self.action_buttons = {}
        self.debug_action_buttons = {}
        
        # User-facing actions
        user_actions = self.logs_data.get('actions', [])
        for action in user_actions:
            count = len(self.logs_data.get('logs_by_action', {}).get(action, []))
            btn = tk.Button(self.user_actions_frame, 
                           text=f"{action} ({count})",
                           font=('Segoe UI', 10),
                           bg=self.colors['bg_light'],
                           fg=self.colors['fg'],
                           activebackground=self.colors['bg_highlight'],
                           activeforeground='white',
                           relief=tk.FLAT,
                           anchor=tk.W,
                           padx=10, pady=8,
                           width=22,
                           command=lambda a=action, d=False: self.on_action_selected(a, d))
            btn.pack(fill=tk.X, pady=1)
            self.action_buttons[action] = btn
        
        # Debugging actions
        debug_actions = self.logs_data.get('debugging_actions', [])
        for action in debug_actions:
            count = len(self.logs_data.get('debugging_logs_by_action', {}).get(action, []))
            btn = tk.Button(self.debug_actions_frame, 
                           text=f"{action} ({count})",
                           font=('Segoe UI', 9),
                           bg=self.colors['bg_light'],
                           fg=self.colors['fg_dim'],
                           activebackground=self.colors['bg_highlight'],
                           activeforeground='white',
                           relief=tk.FLAT,
                           anchor=tk.W,
                           padx=10, pady=6,
                           width=22,
                           command=lambda a=action, d=True: self.on_action_selected(a, d))
            btn.pack(fill=tk.X, pady=1)
            self.debug_action_buttons[action] = btn
        
        user_total = self.logs_data.get('user_facing_logs', 0)
        debug_total = self.logs_data.get('debugging_logs', 0)
        self.stats_label.config(text=f"User: {user_total} | Debug: {debug_total}")
        
        # Select first user-facing action by default
        if user_actions:
            self.on_action_selected(user_actions[0], False)
    
    def on_action_selected(self, action, is_debug=False):
        """Handle action selection"""
        self.current_action = action
        self.is_debug_mode = is_debug
        
        # Update button highlighting for user-facing
        for a, btn in self.action_buttons.items():
            if a == action and not is_debug:
                btn.configure(bg=self.colors['bg_highlight'], fg='white')
            else:
                btn.configure(bg=self.colors['bg_light'], fg=self.colors['fg'])
        
        # Update button highlighting for debugging
        for a, btn in self.debug_action_buttons.items():
            if a == action and is_debug:
                btn.configure(bg=self.colors['bg_highlight'], fg='white')
            else:
                btn.configure(bg=self.colors['bg_light'], fg=self.colors['fg_dim'])
        
        # Populate scenarios
        self.populate_scenarios(action, is_debug)
        
        # Update header
        prefix = "DEBUG - " if is_debug else ""
        self.scenarios_label.config(text=f"SCENARIOS - {prefix}{action}")
    
    def populate_scenarios(self, action, is_debug=False):
        """Populate scenarios for selected action"""
        # Clear existing scenarios
        for widget in self.scenarios_frame.winfo_children():
            widget.destroy()
        self.scenario_widgets = []
        
        # Get logs from appropriate source
        if is_debug:
            logs = self.logs_data.get('debugging_logs_by_action', {}).get(action, [])
        else:
            logs = self.logs_data.get('logs_by_action', {}).get(action, [])
        
        # Group logs by scenario
        by_scenario = {}
        for log in logs:
            scenario = log.get('scenario', 'Unknown')
            if scenario not in by_scenario:
                by_scenario[scenario] = []
            by_scenario[scenario].append(log)
        
        # Create scenario buttons
        for scenario, scenario_logs in sorted(by_scenario.items()):
            first_log = scenario_logs[0]
            log_type = first_log.get('type', 'info')
            icons = {'error': '❌', 'success': '✅', 'warning': '⚠️', 'info': 'ℹ️'}
            icon = icons.get(log_type, '•')
            
            type_colors = {
                'error': self.colors['error'],
                'success': self.colors['success'],
                'warning': self.colors['warning'],
                'info': self.colors['info']
            }
            color = type_colors.get(log_type, self.colors['fg'])
            
            # Create frame for scenario
            frame = tk.Frame(self.scenarios_frame, bg=self.colors['bg_light'], cursor='hand2')
            frame.pack(fill=tk.X, pady=2)
            
            # Scenario label
            label_text = f"{icon} {scenario}"
            if len(scenario_logs) > 1:
                label_text += f" ({len(scenario_logs)})"
            
            label = tk.Label(frame, text=label_text,
                           font=('Segoe UI', 10),
                           bg=self.colors['bg_light'],
                           fg=color,
                           anchor=tk.W,
                           padx=10, pady=8)
            label.pack(fill=tk.X)
            
            # Bind click events
            for widget in [frame, label]:
                widget.bind('<Button-1>', lambda e, l=scenario_logs, f=frame: self.on_scenario_selected(l, f))
                widget.bind('<Enter>', lambda e, f=frame: f.configure(bg=self.colors['bg_highlight']))
                widget.bind('<Leave>', lambda e, f=frame, c=self.colors['bg_light']: 
                           f.configure(bg=c) if f not in [w[0] for w in self.scenario_widgets if w[1]] else None)
            
            self.scenario_widgets.append((frame, False, scenario_logs))
        
        # Select first scenario by default
        if self.scenario_widgets:
            first_frame, _, first_logs = self.scenario_widgets[0]
            self.on_scenario_selected(first_logs, first_frame)
    
    def on_scenario_selected(self, logs, frame):
        """Handle scenario selection"""
        # Update highlighting
        for f, _, _ in self.scenario_widgets:
            f.configure(bg=self.colors['bg_light'])
            for child in f.winfo_children():
                child.configure(bg=self.colors['bg_light'])
        
        frame.configure(bg=self.colors['bg_highlight'])
        for child in frame.winfo_children():
            child.configure(bg=self.colors['bg_highlight'])
        
        # Update scenario_widgets to track selection
        self.scenario_widgets = [(f, f == frame, l) for f, _, l in self.scenario_widgets]
        
        # Display the log(s)
        self.display_logs(logs)
    
    def display_logs(self, logs):
        """Display selected logs in the three panels"""
        if not logs:
            return
        
        first_log = logs[0]
        
        # === TRIGGER SECTION ===
        trigger = first_log.get('trigger', '')
        if trigger:
            self.trigger_text.config(text=trigger)
        else:
            self.trigger_text.config(text=f"This message appears during: {first_log.get('scenario', 'Unknown')}")
        
        # === USER SEES SECTION (with colorized example values) ===
        self.user_text.configure(state='normal')
        self.user_text.delete(1.0, tk.END)
        
        for i, log in enumerate(logs):
            if i > 0:
                self.user_text.insert(tk.END, "\n\n")
            
            # Use the example_message (with realistic values) instead of raw_message
            message = log.get('example_message', log.get('raw_message', ''))
            log_type = log.get('type', 'info')
            
            # Colorize the message with different colors for different parts
            self.colorize_message(message, log_type)
        
        self.user_text.configure(state='disabled')
        
        # === DEVELOPER CODE SECTION ===
        self.dev_text.configure(state='normal')
        self.dev_text.delete(1.0, tk.END)
        
        for i, log in enumerate(logs):
            if i > 0:
                self.dev_text.insert(tk.END, "\n\n" + "─" * 50 + "\n\n")
            
            # File/line reference (for AI to find)
            file_info = f"# {log['file']}:{log['line']}"
            if log.get('function'):
                file_info += f" in {log['function']}()"
            
            self.dev_text.insert(tk.END, file_info + "\n", 'comment')
            self.dev_text.insert(tk.END, log.get('code', ''))
        
        self.dev_text.configure(state='disabled')
        
        # Update location label
        if len(logs) == 1:
            log = logs[0]
            self.dev_location.config(text=f"{log['file']}:{log['line']}")
        else:
            files = set(l['file'] for l in logs)
            self.dev_location.config(text=f"{len(logs)} messages in {len(files)} file(s)")
    
    def colorize_message(self, message, log_type):
        """Insert message with colorized parts (emojis, numbers, names, etc.)"""
        import re
        
        # Default tag based on log type
        default_tag = log_type if log_type in ['error', 'success', 'warning', 'info'] else 'info'
        
        # Create a list of (start, end, tag) tuples
        # We'll mark which character positions belong to which tags
        char_tags = [default_tag] * len(message)
        
        # Process patterns in order of specificity (most specific first)
        # 1. Confidence values (e.g., "confidence: 0.92")
        for match in re.finditer(r'confidence:\s*\d+\.?\d*', message):
            start, end = match.span()
            for i in range(start, end):
                char_tags[i] = 'confidence'
        
        # 2. File paths with extensions (e.g., "Import File.csv")
        for match in re.finditer(r'\b[A-Z][a-zA-Z\s]+\.(csv|pdf|zip|CSV|PDF|ZIP)\b', message):
            start, end = match.span()
            for i in range(start, end):
                if char_tags[i] == default_tag:  # Don't override confidence
                    char_tags[i] = 'file_path'
        
        # 3. Student names (two capitalized words, not already tagged)
        for match in re.finditer(r'\b([A-Z][a-z]+\s+[A-Z][a-z]+)\b', message):
            start, end = match.span()
            # Only tag if not part of file path or confidence
            if all(char_tags[i] == default_tag for i in range(start, end)):
                for i in range(start, end):
                    char_tags[i] = 'name'
        
        # 4. Numbers (not part of confidence, file paths, or names)
        for match in re.finditer(r'\b\d+\.?\d*\b', message):
            start, end = match.span()
            # Only tag if not already tagged
            if all(char_tags[i] == default_tag for i in range(start, end)):
                for i in range(start, end):
                    char_tags[i] = 'number'
        
        # 5. Emojis (override everything)
        for match in re.finditer(r'[❌✅⚠️📋📊🔬📄📦🔍💡🔗🔄📌]', message):
            start, end = match.span()
            for i in range(start, end):
                char_tags[i] = 'emoji'
        
        # Now insert the message with appropriate tags
        # Group consecutive characters with the same tag
        current_tag = char_tags[0]
        current_start = 0
        
        for i in range(1, len(message)):
            if char_tags[i] != current_tag:
                # Insert the segment with the current tag
                if i > current_start:
                    self.user_text.insert(tk.END, message[current_start:i], current_tag)
                current_tag = char_tags[i]
                current_start = i
        
        # Insert the last segment
        if current_start < len(message):
            self.user_text.insert(tk.END, message[current_start:], current_tag)
    
    def show_ui_transformations(self):
        """Show UI Transformations - how raw logs become clickable elements"""
        # Update highlighting
        self.ui_transforms_btn.configure(bg=self.colors['bg_highlight'], fg='white')
        self.dynamic_btn.configure(bg=self.colors['bg_light'], fg=self.colors['warning'])
        
        for a, btn in self.action_buttons.items():
            btn.configure(bg=self.colors['bg_light'], fg=self.colors['fg'])
        for a, btn in self.debug_action_buttons.items():
            btn.configure(bg=self.colors['bg_light'], fg=self.colors['fg_dim'])
        
        self.scenarios_label.config(text="UI TRANSFORMATIONS")
        
        # Clear scenarios
        for widget in self.scenarios_frame.winfo_children():
            widget.destroy()
        self.scenario_widgets = []
        
        ui_transforms = self.logs_data.get('ui_transformations', {})
        
        for name, transform in ui_transforms.items():
            frame = tk.Frame(self.scenarios_frame, bg=self.colors['bg_light'], cursor='hand2')
            frame.pack(fill=tk.X, pady=2)
            
            label = tk.Label(frame, text=f"🔗 {name}",
                           font=('Segoe UI', 10),
                           bg=self.colors['bg_light'],
                           fg=self.colors['info'],
                           anchor=tk.W,
                           padx=10, pady=8)
            label.pack(fill=tk.X)
            
            for widget in [frame, label]:
                widget.bind('<Button-1>', lambda e, t=transform, n=name, f=frame: self.display_ui_transform(t, n, f))
                widget.bind('<Enter>', lambda e, f=frame: f.configure(bg=self.colors['bg_highlight']))
                widget.bind('<Leave>', lambda e, f=frame: f.configure(bg=self.colors['bg_light']))
            
            self.scenario_widgets.append((frame, False, transform))
        
        # Select first
        if ui_transforms:
            first_name = list(ui_transforms.keys())[0]
            first_transform = ui_transforms[first_name]
            first_frame = self.scenario_widgets[0][0]
            self.display_ui_transform(first_transform, first_name, first_frame)
    
    def display_ui_transform(self, transform, name, frame):
        """Display a UI transformation"""
        # Update highlighting
        for f, _, _ in self.scenario_widgets:
            f.configure(bg=self.colors['bg_light'])
            for child in f.winfo_children():
                child.configure(bg=self.colors['bg_light'])
        
        frame.configure(bg=self.colors['bg_highlight'])
        for child in frame.winfo_children():
            child.configure(bg=self.colors['bg_highlight'])
        
        # Trigger
        link_action = transform.get('link_action', '')
        action = transform.get('action', '')
        self.trigger_text.config(text=f"Action: {action}\nLink: {link_action}")
        
        # User sees
        self.user_text.configure(state='normal')
        self.user_text.delete(1.0, tk.END)
        
        self.user_text.insert(tk.END, "RAW LOG MESSAGE:\n", 'info')
        self.user_text.insert(tk.END, transform.get('raw_example', '') + "\n\n")
        self.user_text.insert(tk.END, "↓ TRANSFORMED IN UI ↓\n\n", 'warning')
        self.user_text.insert(tk.END, "USER ACTUALLY SEES:\n", 'success')
        self.user_text.insert(tk.END, transform.get('user_sees', ''))
        
        if transform.get('has_link'):
            self.user_text.insert(tk.END, "\n\n💡 ", 'info')
            self.user_text.insert(tk.END, "(This appears as a clickable link in the UI)", 'info')
        
        self.user_text.configure(state='disabled')
        
        # Developer code
        self.dev_text.configure(state='normal')
        self.dev_text.delete(1.0, tk.END)
        
        self.dev_text.insert(tk.END, "# Matching pattern in LogTerminal.tsx\n", 'comment')
        self.dev_text.insert(tk.END, f"pattern: /{transform.get('pattern', '')}/\n\n")
        self.dev_text.insert(tk.END, "# The raw log statement that triggers this:\n", 'comment')
        self.dev_text.insert(tk.END, f"addLog('{transform.get('raw_example', '')}')\n\n")
        self.dev_text.insert(tk.END, "# Or from Python:\n", 'comment')
        self.dev_text.insert(tk.END, f"log_callback('{transform.get('raw_example', '')}')")
        
        self.dev_text.configure(state='disabled')
        
        self.dev_location.config(text="LogTerminal.tsx")
    
    def show_dynamic_examples(self):
        """Show Dynamic Log Examples - logs built in loops"""
        # Update highlighting
        self.dynamic_btn.configure(bg=self.colors['bg_highlight'], fg='white')
        self.ui_transforms_btn.configure(bg=self.colors['bg_light'], fg=self.colors['warning'])
        
        for a, btn in self.action_buttons.items():
            btn.configure(bg=self.colors['bg_light'], fg=self.colors['fg'])
        for a, btn in self.debug_action_buttons.items():
            btn.configure(bg=self.colors['bg_light'], fg=self.colors['fg_dim'])
        
        self.scenarios_label.config(text="DYNAMIC LOG EXAMPLES")
        
        # Clear scenarios
        for widget in self.scenarios_frame.winfo_children():
            widget.destroy()
        self.scenario_widgets = []
        
        dynamic_examples = self.logs_data.get('dynamic_log_examples', {})
        
        for name, example in dynamic_examples.items():
            frame = tk.Frame(self.scenarios_frame, bg=self.colors['bg_light'], cursor='hand2')
            frame.pack(fill=tk.X, pady=2)
            
            label = tk.Label(frame, text=f"🔄 {name.replace('_', ' ').title()}",
                           font=('Segoe UI', 10),
                           bg=self.colors['bg_light'],
                           fg=self.colors['success'],
                           anchor=tk.W,
                           padx=10, pady=8)
            label.pack(fill=tk.X)
            
            for widget in [frame, label]:
                widget.bind('<Button-1>', lambda e, ex=example, n=name, f=frame: self.display_dynamic_example(ex, n, f))
                widget.bind('<Enter>', lambda e, f=frame: f.configure(bg=self.colors['bg_highlight']))
                widget.bind('<Leave>', lambda e, f=frame: f.configure(bg=self.colors['bg_light']))
            
            self.scenario_widgets.append((frame, False, example))
        
        # Select first
        if dynamic_examples:
            first_name = list(dynamic_examples.keys())[0]
            first_example = dynamic_examples[first_name]
            first_frame = self.scenario_widgets[0][0]
            self.display_dynamic_example(first_example, first_name, first_frame)
    
    def display_dynamic_example(self, example, name, frame):
        """Display a dynamic log example"""
        # Update highlighting
        for f, _, _ in self.scenario_widgets:
            f.configure(bg=self.colors['bg_light'])
            for child in f.winfo_children():
                child.configure(bg=self.colors['bg_light'])
        
        frame.configure(bg=self.colors['bg_highlight'])
        for child in frame.winfo_children():
            child.configure(bg=self.colors['bg_highlight'])
        
        # Trigger
        self.trigger_text.config(text=example.get('description', ''))
        
        # User sees
        self.user_text.configure(state='normal')
        self.user_text.delete(1.0, tk.END)
        
        self.user_text.insert(tk.END, "EXAMPLE MESSAGE:\n\n", 'info')
        self.user_text.insert(tk.END, example.get('example', ''), 'success')
        self.user_text.insert(tk.END, "\n\n💡 ", 'info')
        self.user_text.insert(tk.END, f"This appears during: {example.get('action', 'Unknown')}", 'info')
        
        self.user_text.configure(state='disabled')
        
        # Developer code
        self.dev_text.configure(state='normal')
        self.dev_text.delete(1.0, tk.END)
        
        self.dev_text.insert(tk.END, f"# Dynamic log: {name}\n", 'comment')
        self.dev_text.insert(tk.END, "# This log is built in a loop at runtime.\n", 'comment')
        self.dev_text.insert(tk.END, "# The pattern cannot be extracted statically,\n", 'comment')
        self.dev_text.insert(tk.END, "# so we document it here with an example.\n\n", 'comment')
        self.dev_text.insert(tk.END, f"# Action: {example.get('action', '')}\n", 'comment')
        self.dev_text.insert(tk.END, f"# Description: {example.get('description', '')}\n\n", 'comment')
        self.dev_text.insert(tk.END, f"log_callback(\"{example.get('example', '')}\")")
        
        self.dev_text.configure(state='disabled')
        
        self.dev_location.config(text="(Dynamic - see source files)")
    
    def refresh_logs(self):
        """Refresh logs by re-running extractor"""
        self.stats_label.config(text="Refreshing...")
        self.root.update()
        
        self.run_extractor()
        self.logs_data = self.load_logs()
        
        # Clear and repopulate
        for widget in self.user_actions_frame.winfo_children():
            widget.destroy()
        for widget in self.debug_actions_frame.winfo_children():
            widget.destroy()
        self.action_buttons = {}
        self.debug_action_buttons = {}
        
        self.populate_actions()
        self.stats_label.config(text=f"Total: {self.logs_data.get('total_logs', 0)} log statements - Refreshed!")


def main():
    root = tk.Tk()
    app = LogPreviewGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
