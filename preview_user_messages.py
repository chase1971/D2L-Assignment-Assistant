#!/usr/bin/env python3
"""
Interactive Preview of User-Facing Log Messages
Shows what users will see during different operations in the app.
"""

import sys
import os
from rich.console import Console
from rich.panel import Panel
from rich import box
import time

# Fix Windows encoding for emojis
if sys.platform == 'win32':
    import io
    import codecs
    # Set UTF-8 encoding for stdout/stderr
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

console = Console()

# Define scenarios - what users see during different operations
SCENARIOS = {
    "Process Quizzes (Success)": [
        "🔍 Searching for assignment ZIP in Downloads...",
        "✅ Found: Quiz 4 (7.1 - 7.4) Download.zip",
        "✅ Extracted 26 student folders",
        "✅ Combined PDF created!",
        "📄 Combined PDF — 26 submissions (click to open)",
        "✅ Quiz processing completed!",
    ],
    
    "Process Quizzes (Error - No ZIP)": [
        "🔍 Searching for assignment ZIP in Downloads...",
        "❌ No ZIP files found in Downloads",
        "",
        "Please download the quiz submissions first.",
    ],
    
    "Process Completion (Success)": [
        "🔍 Searching for assignment ZIP in Downloads...",
        "✅ Found: Assignment 1 Download.zip",
        "✅ Extracted 18 student folders",
        "✅ Combined PDF created!",
        "✅ Auto-assigned 10 points to 18 submissions",
        "✅ Completion processing completed!",
        "📋 Open Import File",
    ],
    
    "Extract Grades (Success)": [
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
    
    "Extract Grades (Error - Missing Column)": [
        "🔬 Starting grade extraction...",
        "",
        "❌ The import file is missing the Email column.",
        "",
        "Please download a fresh import file from D2L that includes all required columns:",
        "OrgDefinedId, Username, First Name, Last Name, and Email.",
    ],
    
    "Extract Grades (Error - File Not Found)": [
        "🔬 Starting grade extraction...",
        "",
        "❌ Import file not found. Please download a fresh import file from D2L.",
    ],
    
    "Extract Grades (Error - File Locked)": [
        "🔬 Starting grade extraction...",
        "",
        "❌ Import file is locked. Please close Excel and try again.",
    ],
    
    "Extract Grades (Error - File Corrupted)": [
        "🔬 Starting grade extraction...",
        "",
        "❌ Import file is empty or corrupted. Please download a fresh import file from D2L.",
    ],
    
    "Extract Grades (Error - Cannot Open)": [
        "🔬 Starting grade extraction...",
        "",
        "❌ Import file cannot be opened. The file may be corrupted. Please download a fresh import file from D2L.",
    ],
    
    "Extract Grades (Error - Extraction Failed)": [
        "🔬 Starting grade extraction...",
        "",
        "❌ Extraction failed",
    ],
    
    "Process Completion (Error - Missing Column)": [
        "🔍 Searching for assignment ZIP in Downloads...",
        "",
        "❌ The import file is missing the Email column.",
        "",
        "Please download a fresh import file from D2L that includes all required columns:",
        "OrgDefinedId, Username, First Name, Last Name, and Email.",
    ],
    
    "Process Completion (Error - File Not Found)": [
        "🔍 Searching for assignment ZIP in Downloads...",
        "",
        "❌ Import file not found. Please download a fresh import file from D2L.",
    ],
    
    "Process Completion (Error - File Locked)": [
        "🔍 Searching for assignment ZIP in Downloads...",
        "",
        "❌ Import file is locked. Please close Excel and try again.",
    ],
    
    "Process Completion (Error - File Corrupted)": [
        "🔍 Searching for assignment ZIP in Downloads...",
        "",
        "❌ Import file is empty or corrupted. Please download a fresh import file from D2L.",
    ],
    
    "Process Completion (Error - Cannot Open)": [
        "🔍 Searching for assignment ZIP in Downloads...",
        "",
        "❌ Import file cannot be opened. The file may be corrupted. Please download a fresh import file from D2L.",
    ],
    
    "Split PDF (Success)": [
        "📦 Starting PDF split and rezip...",
        "✅ Successfully split PDF for 26 students",
        "✅ Created ZIP file: Quiz 4 (7.1 - 7.4) Download.zip",
        "✅ Split PDF and rezip completed!",
    ],
    
    "Split PDF (Error)": [
        "📦 Starting PDF split and rezip...",
        "❌ Split PDF failed",
    ],
    
    "Open Folder (Success)": [
        "📂 Opening grade processing folder...",
        "✅ Grade processing folder opened!",
    ],
    
    "Open Folder (No Processing Folder)": [
        "📂 Opening grade processing folder...",
        "❌ No grade processing folder found",
    ],
    
    "Clear Data (Success)": [
        "🗑️ Clearing all processing data...",
        "✅ All data cleared successfully!",
    ],
    
    "Load Classes (Success)": [
        "📂 Loading classes from Rosters etc folder...",
        "✅ Found 5 classes",
    ],
    
    "Load Classes (Error)": [
        "📂 Loading classes from Rosters etc folder...",
        "❌ Could not find roster folder",
    ],
}


def print_scenario(name: str, messages: list):
    """Print a scenario with nice formatting"""
    console.print()
    console.print(Panel.fit(
        f"[bold cyan]{name}[/bold cyan]",
        border_style="cyan",
        box=box.ROUNDED
    ))
    console.print()
    
    for msg in messages:
        if not msg.strip():
            console.print()  # Empty line
        elif msg.startswith("❌"):
            console.print(f"[red]{msg}[/red]")
        elif msg.startswith("✅"):
            console.print(f"[green]{msg}[/green]")
        elif msg.startswith("⚠️"):
            console.print(f"[yellow]{msg}[/yellow]")
        elif msg.startswith("🔍") or msg.startswith("🔬") or msg.startswith("📦"):
            console.print(f"[cyan]{msg}[/cyan]")
        elif msg.startswith("📄") or msg.startswith("📋") or msg.startswith("📂") or msg.startswith("📁"):
            console.print(f"[blue]{msg}[/blue]")
        elif msg.startswith("🗑️"):
            console.print(f"[magenta]{msg}[/magenta]")
        elif msg.startswith("   "):  # Indented messages (issues, grades list)
            if "❌" in msg:
                console.print(f"[red]{msg}[/red]")
            elif "⚠️" in msg:
                console.print(f"[yellow]{msg}[/yellow]")
            else:
                console.print(f"[dim]{msg}[/dim]")
        elif msg.startswith("    "):  # More indented (grade list items)
            if "✅" in msg:
                console.print(f"[green]{msg}[/green]")
            elif "⚠️" in msg:
                console.print(f"[yellow]{msg}[/yellow]")
            else:
                console.print(f"[dim]{msg}[/dim]")
        else:
            console.print(msg)
    
    console.print()


def show_all_scenarios():
    """Show all scenarios"""
    console.print()
    console.print(Panel.fit(
        "[bold white]User Message Preview[/bold white]\n"
        "[dim]This shows what users will see during different operations[/dim]",
        border_style="white",
        box=box.DOUBLE
    ))
    
    for name, messages in SCENARIOS.items():
        print_scenario(name, messages)
        time.sleep(0.5)  # Small delay between scenarios


def show_single_scenario(scenario_name: str):
    """Show a single scenario"""
    if scenario_name in SCENARIOS:
        print_scenario(scenario_name, SCENARIOS[scenario_name])
    else:
        console.print(f"[red]Scenario '{scenario_name}' not found![/red]")
        console.print(f"\nAvailable scenarios:")
        for name in SCENARIOS.keys():
            console.print(f"  • {name}")


def interactive_menu():
    """Interactive menu to select scenarios"""
    console.print()
    console.print(Panel.fit(
        "[bold white]User Message Preview - Interactive Menu[/bold white]",
        border_style="white",
        box=box.DOUBLE
    ))
    console.print()
    
    scenarios_list = list(SCENARIOS.keys())
    
    while True:
        console.print("[bold]Available Scenarios:[/bold]")
        for i, name in enumerate(scenarios_list, 1):
            console.print(f"  [cyan]{i}.[/cyan] {name}")
        console.print(f"  [cyan]0.[/cyan] Show all scenarios")
        console.print(f"  [cyan]q.[/cyan] Quit")
        console.print()
        
        choice = console.input("[bold green]Select scenario (number): [/bold green]").strip()
        
        if choice.lower() == 'q':
            break
        elif choice == '0':
            show_all_scenarios()
            break
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(scenarios_list):
                    show_single_scenario(scenarios_list[idx])
                    console.print()
                    input("[dim]Press Enter to continue...[/dim]")
                    console.clear()
                else:
                    console.print("[red]Invalid choice![/red]\n")
            except ValueError:
                console.print("[red]Please enter a number![/red]\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Show specific scenario from command line
        scenario_name = " ".join(sys.argv[1:])
        show_single_scenario(scenario_name)
    else:
        # Interactive menu
        interactive_menu()

