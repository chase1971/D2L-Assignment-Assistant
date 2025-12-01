#!/usr/bin/env python3
"""
Fixed CLI script for grade extraction - based on working minimal version
Usage: python extract_grades_cli_fixed.py <drive> <className>
"""

import sys
import os
import json
import pandas as pd
from extract_grades_simple import extract_grades
from config_reader import get_rosters_path

def main():
    if len(sys.argv) != 3:
        print(json.dumps({
            "success": False,
            "error": "Usage: python extract_grades_cli_fixed.py <drive> <className>"
        }))
        sys.exit(1)
    
    drive = sys.argv[1]
    class_name = sys.argv[2]
    
    try:
        logs = []
        logs.append(f"🔬 Extracting grades from PDF using OCR for {class_name}")
        
        # Get configured rosters path
        rosters_path = get_rosters_path()
        class_folders = [f for f in os.listdir(rosters_path) if class_name in f]
        
        if not class_folders:
            logs.append("❌ Class folder not found")
            raise Exception("Class folder not found")
        
        class_folder = os.path.join(rosters_path, class_folders[0])
        grade_processing_folder = os.path.join(class_folder, "grade processing")
        combined_pdf_path = os.path.join(grade_processing_folder, "PDFs", "1combinedpdf.pdf")
        
        if not os.path.exists(combined_pdf_path):
            logs.append("❌ Combined PDF not found")
            raise Exception("Combined PDF not found")
        
        logs.append(f"📄 Found combined PDF: {os.path.basename(combined_pdf_path)}")
        
        # Extract grades
        logs.append("🔍 Extracting grades from combined PDF using OCR...")
        
        def log_callback(message):
            logs.append(message)
        
        grades_result = extract_grades(combined_pdf_path, log_callback)
        
        # Convert to simple format
        grades_dict = {}
        for student_name, grade_info in grades_result.items():
            if isinstance(grade_info, dict) and 'grade' in grade_info:
                grades_dict[student_name] = grade_info['grade']
            else:
                grades_dict[student_name] = str(grade_info)
        
        logs.append(f"📊 Extracted {len(grades_dict)} grades")
        
        # Update CSV
        import_file_path = os.path.join(class_folder, "Import file.csv")
        if os.path.exists(import_file_path):
            logs.append("📝 Updating Import file...")
            df = pd.read_csv(import_file_path)
            
            # Find quiz column
            grade_columns = [col for col in df.columns if 'Points Grade' in col or 'Quiz' in col]
            if grade_columns:
                quiz_column = grade_columns[0]
            else:
                quiz_column = df.columns[-2]
            
            logs.append(f"📊 Using column: {quiz_column}")
            
            # Update grades
            updated_count = 0
            for student_name, grade in grades_dict.items():
                name_parts = student_name.split()
                if len(name_parts) >= 2:
                    first_name = name_parts[0].lower()
                    last_name = ' '.join(name_parts[1:]).lower()
                    
                    # Match by both first and last name
                    mask = (df['First Name'].str.lower().str.contains(first_name, na=False)) & \
                           (df['Last Name'].str.lower().str.contains(last_name, na=False))
                    
                    if mask.any():
                        df.loc[mask, quiz_column] = grade
                        updated_count += 1
                        logs.append(f"✅ Updated {student_name}: {grade}")
                    else:
                        logs.append(f"⚠️ Could not match: {student_name}")
            
            # Save updated CSV
            df.to_csv(import_file_path, index=False)
            logs.append(f"✅ Updated {updated_count} grades in Import file")
            
            # Verify the update
            logs.append("🔍 Verifying update...")
            df_check = pd.read_csv(import_file_path)
            non_empty_grades = df_check[quiz_column].dropna()
            logs.append(f"📊 Found {len(non_empty_grades)} non-empty grades")
            
        else:
            logs.append("❌ Import file not found")
            raise Exception("Import file not found")
        
        # Open the Excel file
        try:
            import subprocess
            import platform
            
            if os.path.exists(import_file_path):
                if platform.system() == "Windows":
                    os.startfile(import_file_path)
                elif platform.system() == "Darwin":  # macOS
                    subprocess.run(["open", import_file_path])
                else:  # Linux
                    subprocess.run(["xdg-open", import_file_path])
                
                logs.append(f"📊 Opened Excel file: Import file.csv")
            else:
                logs.append("⚠️ Import file not found for opening")
                
        except Exception as e:
            logs.append(f"⚠️ Could not open Excel file: {str(e)}")
        
        logs.append("✅ Grade extraction completed successfully!")
        
        response = {
            "success": True,
            "message": "Grade extraction completed",
            "logs": logs
        }
        
        print(json.dumps(response))
        
    except Exception as e:
        error_response = {
            "success": False,
            "error": str(e),
            "logs": logs if 'logs' in locals() else [f"❌ Error: {str(e)}"]
        }
        print(json.dumps(error_response))
        sys.exit(1)

if __name__ == "__main__":
    main()
