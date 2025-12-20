#!/usr/bin/env python3
"""
Test Scenario Runner for D2L Assignment Assistant

This script allows you to test different scenarios without needing real data.
You can simulate:
- Students without PDFs
- Duplicate submissions
- Multiple PDFs per student
- Unreadable files
- And more...

Usage:
    python test_scenario_runner.py
"""

import os
import sys
import tempfile
import shutil
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
from pypdf import PdfWriter, PdfReader

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from submission_processor import process_submissions


class TestScenario:
    """Represents a test scenario configuration."""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.students = {}  # {student_name: StudentConfig}
        self.roster = []  # List of roster entries
    
    def add_student(self, first_name: str, last_name: str, username: str, 
                   scenario_type: str = "normal", **kwargs):
        """
        Add a student to the scenario.
        
        Args:
            first_name: Student's first name
            last_name: Student's last name
            username: Student's username
            scenario_type: One of:
                - "normal": Student has a single PDF (default)
                - "no_pdf": Student has no PDF in their folder
                - "duplicate": Student submitted twice (will create two folders)
                - "multiple_pdfs": Student has multiple PDFs
                - "unreadable": Student has non-PDF files (images, etc.)
                - "empty": Student folder is empty
            **kwargs: Additional options:
                - pdf_pages: Number of pages in PDF (default: 5)
                - num_pdfs: Number of PDFs for multiple_pdfs scenario (default: 2)
                - file_type: For unreadable, can be "image" or "other" (default: "image")
        """
        full_name = f"{first_name} {last_name}"
        self.students[full_name] = {
            "first_name": first_name,
            "last_name": last_name,
            "username": username,
            "scenario_type": scenario_type,
            **kwargs
        }
        
        # Add to roster
        self.roster.append({
            "First Name": first_name,
            "Last Name": last_name,
            "Username": username
        })
    
    def get_roster_df(self) -> pd.DataFrame:
        """Get roster as a pandas DataFrame."""
        return pd.DataFrame(self.roster)


class ScenarioBuilder:
    """Helper class to build test scenarios easily."""
    
    @staticmethod
    def create_basic_scenario() -> TestScenario:
        """Create a basic scenario with a few normal students."""
        scenario = TestScenario("Basic Scenario", "Normal submissions")
        scenario.add_student("John", "Smith", "jsmith01", "normal", pdf_pages=5)
        scenario.add_student("Jane", "Doe", "jdoe02", "normal", pdf_pages=8)
        scenario.add_student("Bob", "Johnson", "bjohnson03", "normal", pdf_pages=6)
        return scenario
    
    @staticmethod
    def create_no_pdf_scenario() -> TestScenario:
        """Create a scenario where one student has no PDF."""
        scenario = TestScenario("No PDF Scenario", "One student missing PDF")
        scenario.add_student("John", "Smith", "jsmith01", "normal", pdf_pages=5)
        scenario.add_student("Jane", "Doe", "jdoe02", "no_pdf")
        scenario.add_student("Bob", "Johnson", "bjohnson03", "normal", pdf_pages=6)
        return scenario
    
    @staticmethod
    def create_duplicate_submission_scenario() -> TestScenario:
        """Create a scenario where one student submitted twice."""
        scenario = TestScenario("Duplicate Submission", "Student submitted twice")
        scenario.add_student("John", "Smith", "jsmith01", "normal", pdf_pages=5)
        scenario.add_student("Jane", "Doe", "jdoe02", "duplicate", pdf_pages=8)
        scenario.add_student("Bob", "Johnson", "bjohnson03", "normal", pdf_pages=6)
        return scenario
    
    @staticmethod
    def create_mixed_scenario() -> TestScenario:
        """Create a scenario with multiple different issues."""
        scenario = TestScenario("Mixed Issues", "Various submission problems")
        scenario.add_student("John", "Smith", "jsmith01", "normal", pdf_pages=5)
        scenario.add_student("Jane", "Doe", "jdoe02", "no_pdf")
        scenario.add_student("Bob", "Johnson", "bjohnson03", "duplicate", pdf_pages=6)
        scenario.add_student("Alice", "Williams", "awilliams04", "multiple_pdfs", num_pdfs=3, pdf_pages=4)
        scenario.add_student("Charlie", "Brown", "cbrown05", "unreadable", file_type="image")
        scenario.add_student("Diana", "Prince", "dprince06", "empty")
        return scenario


def create_mock_pdf(pdf_path: str, num_pages: int = 5):
    """Create a mock PDF file with the specified number of pages."""
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    
    c = canvas.Canvas(pdf_path, pagesize=letter)
    for i in range(num_pages):
        c.drawString(100, 750, f"Test PDF Page {i+1} of {num_pages}")
        if i < num_pages - 1:
            c.showPage()
    c.save()


def create_mock_image(image_path: str):
    """Create a mock image file (actually just a text file with .jpg extension)."""
    # Create a minimal valid image header (PNG format)
    # For testing purposes, we'll just create a file that looks like an image
    with open(image_path, "wb") as f:
        # Write PNG header
        f.write(b'\x89PNG\r\n\x1a\n')
        f.write(b'Mock image file for testing')


def setup_test_environment(scenario: TestScenario, extraction_folder: str):
    """Set up the test environment with mock student folders."""
    # Create extraction folder
    os.makedirs(extraction_folder, exist_ok=True)
    
    # Process each student
    for student_name, config in scenario.students.items():
        scenario_type = config["scenario_type"]
        first_name = config["first_name"]
        last_name = config["last_name"]
        
        if scenario_type == "duplicate":
            # Create two submission folders with different timestamps
            timestamp1 = datetime(2025, 1, 15, 10, 30)
            timestamp2 = datetime(2025, 1, 15, 14, 45)
            
            folder1 = f"Submission - {student_name} - {timestamp1.strftime('%b %d, %Y %I:%M %p')}"
            folder2 = f"Submission - {student_name} - {timestamp2.strftime('%b %d, %Y %I:%M %p')}"
            
            folder_path1 = os.path.join(extraction_folder, folder1)
            folder_path2 = os.path.join(extraction_folder, folder2)
            os.makedirs(folder_path1, exist_ok=True)
            os.makedirs(folder_path2, exist_ok=True)
            
            # Add PDF to both (or just the newer one)
            pdf_pages = config.get("pdf_pages", 5)
            create_mock_pdf(os.path.join(folder_path1, "submission.pdf"), pdf_pages)
            create_mock_pdf(os.path.join(folder_path2, "submission.pdf"), pdf_pages)
            
        else:
            # Create single submission folder
            timestamp = datetime(2025, 1, 15, 12, 0)
            folder_name = f"Submission - {student_name} - {timestamp.strftime('%b %d, %Y %I:%M %p')}"
            folder_path = os.path.join(extraction_folder, folder_name)
            os.makedirs(folder_path, exist_ok=True)
            
            if scenario_type == "normal":
                pdf_pages = config.get("pdf_pages", 5)
                create_mock_pdf(os.path.join(folder_path, "submission.pdf"), pdf_pages)
                
            elif scenario_type == "no_pdf":
                # Create folder but no PDF
                pass
                
            elif scenario_type == "multiple_pdfs":
                num_pdfs = config.get("num_pdfs", 2)
                pdf_pages = config.get("pdf_pages", 4)
                for i in range(num_pdfs):
                    create_mock_pdf(
                        os.path.join(folder_path, f"submission_part{i+1}.pdf"), 
                        pdf_pages
                    )
                    
            elif scenario_type == "unreadable":
                file_type = config.get("file_type", "image")
                if file_type == "image":
                    create_mock_image(os.path.join(folder_path, "submission.jpg"))
                else:
                    # Create a text file or other non-PDF
                    with open(os.path.join(folder_path, "submission.txt"), "w") as f:
                        f.write("This is not a PDF file")
                        
            elif scenario_type == "empty":
                # Folder exists but is empty
                pass


def run_scenario(scenario: TestScenario, verbose: bool = True):
    """Run a test scenario and display the results."""
    print("\n" + "=" * 70)
    print(f"TEST SCENARIO: {scenario.name}")
    if scenario.description:
        print(f"Description: {scenario.description}")
    print("=" * 70)
    
    # Create temporary directories
    with tempfile.TemporaryDirectory() as temp_dir:
        extraction_folder = os.path.join(temp_dir, "extracted")
        pdf_output_folder = os.path.join(temp_dir, "pdfs")
        
        # Set up test environment
        print("\n[SETUP] Creating mock student folders...")
        setup_test_environment(scenario, extraction_folder)
        print(f"[SETUP] Created {len(scenario.students)} student folders")
        
        # Get roster
        roster_df = scenario.get_roster_df()
        print(f"[SETUP] Roster has {len(roster_df)} students")
        
        # Collect logs
        logs = []
        
        def log_callback(message):
            logs.append(message)
            if verbose:
                print(message)
        
        # Run the actual processing
        print("\n" + "-" * 70)
        print("RUNNING PROCESS_SUBMISSIONS")
        print("-" * 70 + "\n")
        
        try:
            submitted, unreadable, no_submission, pdf_paths, name_map, student_errors, page_counts = process_submissions(
                extraction_folder,
                roster_df,
                pdf_output_folder,
                log_callback=log_callback,
                is_completion_process=False
            )
            
            # Display results summary
            print("\n" + "=" * 70)
            print("RESULTS SUMMARY")
            print("=" * 70)
            print(f"✓ Submitted (with PDF): {len(submitted)}")
            print(f"  Students: {', '.join(sorted(submitted))}")
            print(f"\n⚠ Unreadable: {len(unreadable)}")
            if unreadable:
                print(f"  Students: {', '.join(sorted(unreadable))}")
            print(f"\n✗ No Submission: {len(no_submission)}")
            if no_submission:
                print(f"  Students: {', '.join(sorted(no_submission))}")
            
            if student_errors:
                print(f"\n📋 Errors/Warnings ({len(student_errors)}):")
                for error in student_errors:
                    print(f"  • {error}")
            
            if page_counts:
                print(f"\n📄 Page Counts:")
                for name, count in sorted(page_counts.items()):
                    print(f"  • {name}: {count} page(s)")
            
            print("\n" + "=" * 70)
            
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return True


def main():
    """Main entry point - allows user to select or create scenarios."""
    print("\n" + "=" * 70)
    print("D2L ASSIGNMENT ASSISTANT - TEST SCENARIO RUNNER")
    print("=" * 70)
    print("\nThis tool lets you test different submission scenarios without real data.")
    print("\nAvailable scenarios:")
    print("  1. Basic Scenario (normal submissions)")
    print("  2. No PDF Scenario (one student missing PDF)")
    print("  3. Duplicate Submission (student submitted twice)")
    print("  4. Mixed Issues (various problems)")
    print("  5. Custom Scenario (define your own)")
    print("  6. Run All Scenarios")
    
    choice = input("\nSelect scenario (1-6): ").strip()
    
    scenarios = []
    
    if choice == "1":
        scenarios.append(ScenarioBuilder.create_basic_scenario())
    elif choice == "2":
        scenarios.append(ScenarioBuilder.create_no_pdf_scenario())
    elif choice == "3":
        scenarios.append(ScenarioBuilder.create_duplicate_submission_scenario())
    elif choice == "4":
        scenarios.append(ScenarioBuilder.create_mixed_scenario())
    elif choice == "5":
        scenario = create_custom_scenario()
        if scenario:
            scenarios.append(scenario)
    elif choice == "6":
        scenarios = [
            ScenarioBuilder.create_basic_scenario(),
            ScenarioBuilder.create_no_pdf_scenario(),
            ScenarioBuilder.create_duplicate_submission_scenario(),
            ScenarioBuilder.create_mixed_scenario(),
        ]
    else:
        print("Invalid choice. Exiting.")
        return
    
    # Run scenarios
    for scenario in scenarios:
        run_scenario(scenario, verbose=True)
        if len(scenarios) > 1:
            input("\nPress Enter to continue to next scenario...")


def create_custom_scenario() -> Optional[TestScenario]:
    """Interactive function to create a custom scenario."""
    print("\n--- Creating Custom Scenario ---")
    name = input("Scenario name: ").strip()
    if not name:
        return None
    
    description = input("Description (optional): ").strip()
    scenario = TestScenario(name, description)
    
    print("\nAdd students (press Enter with empty name to finish):")
    while True:
        first = input("  First name: ").strip()
        if not first:
            break
        
        last = input("  Last name: ").strip()
        username = input("  Username: ").strip()
        
        print("  Scenario type:")
        print("    1. normal - Student has a single PDF")
        print("    2. no_pdf - Student has no PDF")
        print("    3. duplicate - Student submitted twice")
        print("    4. multiple_pdfs - Student has multiple PDFs")
        print("    5. unreadable - Student has non-PDF files")
        print("    6. empty - Student folder is empty")
        
        type_choice = input("  Select (1-6, default=1): ").strip() or "1"
        type_map = {
            "1": "normal",
            "2": "no_pdf",
            "3": "duplicate",
            "4": "multiple_pdfs",
            "5": "unreadable",
            "6": "empty"
        }
        scenario_type = type_map.get(type_choice, "normal")
        
        kwargs = {}
        if scenario_type in ["normal", "duplicate", "multiple_pdfs"]:
            pages = input("  PDF pages (default=5): ").strip()
            if pages:
                kwargs["pdf_pages"] = int(pages)
        
        if scenario_type == "multiple_pdfs":
            num = input("  Number of PDFs (default=2): ").strip()
            if num:
                kwargs["num_pdfs"] = int(num)
        
        if scenario_type == "unreadable":
            file_type = input("  File type (image/other, default=image): ").strip() or "image"
            kwargs["file_type"] = file_type
        
        scenario.add_student(first, last, username, scenario_type, **kwargs)
        print(f"  ✓ Added {first} {last}\n")
    
    return scenario if scenario.students else None


if __name__ == "__main__":
    main()
