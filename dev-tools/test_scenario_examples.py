#!/usr/bin/env python3
"""
Example usage of the test scenario runner.

This file shows how to programmatically create and run test scenarios.
You can use this as a template for creating your own test cases.
"""

from test_scenario_runner import TestScenario, run_scenario, ScenarioBuilder


def example_missing_pdf():
    """Example: Test what happens when a student has no PDF."""
    print("\n" + "="*70)
    print("EXAMPLE: Missing PDF Scenario")
    print("="*70)
    
    scenario = TestScenario(
        "Missing PDF Test",
        "Testing error handling when a student doesn't have a PDF"
    )
    
    # Add students
    scenario.add_student("John", "Smith", "jsmith01", "normal", pdf_pages=5)
    scenario.add_student("Jane", "Doe", "jdoe02", "no_pdf")  # No PDF!
    scenario.add_student("Bob", "Johnson", "bjohnson03", "normal", pdf_pages=6)
    
    run_scenario(scenario)


def example_duplicate_submission():
    """Example: Test duplicate submission handling."""
    print("\n" + "="*70)
    print("EXAMPLE: Duplicate Submission Scenario")
    print("="*70)
    
    scenario = TestScenario(
        "Duplicate Submission Test",
        "Testing that duplicate submissions are detected and logged"
    )
    
    scenario.add_student("John", "Smith", "jsmith01", "normal", pdf_pages=5)
    scenario.add_student("Jane", "Doe", "jdoe02", "duplicate", pdf_pages=8)
    # Jane submitted twice - should see logging about newer submission
    
    run_scenario(scenario)


def example_multiple_issues():
    """Example: Test multiple different issues at once."""
    print("\n" + "="*70)
    print("EXAMPLE: Multiple Issues Scenario")
    print("="*70)
    
    scenario = TestScenario(
        "Multiple Issues Test",
        "Testing various edge cases together"
    )
    
    scenario.add_student("John", "Smith", "jsmith01", "normal", pdf_pages=5)
    scenario.add_student("Jane", "Doe", "jdoe02", "no_pdf")
    scenario.add_student("Bob", "Johnson", "bjohnson03", "duplicate", pdf_pages=6)
    scenario.add_student("Alice", "Williams", "awilliams04", "multiple_pdfs", 
                       num_pdfs=3, pdf_pages=4)
    scenario.add_student("Charlie", "Brown", "cbrown05", "unreadable", file_type="image")
    scenario.add_student("Diana", "Prince", "dprince06", "empty")
    
    run_scenario(scenario)


def example_using_builder():
    """Example: Using the ScenarioBuilder helper."""
    print("\n" + "="*70)
    print("EXAMPLE: Using ScenarioBuilder")
    print("="*70)
    
    # Use pre-built scenarios
    scenario = ScenarioBuilder.create_no_pdf_scenario()
    run_scenario(scenario)


if __name__ == "__main__":
    print("\n" + "="*70)
    print("TEST SCENARIO EXAMPLES")
    print("="*70)
    print("\nThis script demonstrates how to create and run test scenarios.")
    print("Uncomment the examples you want to run below.\n")
    
    # Uncomment the examples you want to run:
    
    # example_missing_pdf()
    # example_duplicate_submission()
    # example_multiple_issues()
    # example_using_builder()
    
    print("\nTo run examples, uncomment them in the main block above.")
