#!/usr/bin/env python3
"""Simple test for grade extraction without file opening logic"""

import os
import pandas as pd
from extract_grades_simple import extract_grades

def main():
    class_name = "TTH 8-920  CA 4201"
    drive = "C"
    
    print(f"🔬 Testing grade extraction for {class_name}")
    
    # Paths
    rosters_path = os.path.join(f"{drive}:\\", "Users", "chase", "My Drive", "Rosters etc")
    class_folders = [f for f in os.listdir(rosters_path) if class_name in f]
    
    if not class_folders:
        print("❌ Class folder not found")
        return
    
    class_folder = os.path.join(rosters_path, class_folders[0])
    grade_processing_folder = os.path.join(class_folder, "grade processing")
    combined_pdf_path = os.path.join(grade_processing_folder, "PDFs", "1combinedpdf.pdf")
    
    if not os.path.exists(combined_pdf_path):
        print("❌ Combined PDF not found")
        return
    
    print(f"📄 Found combined PDF: {os.path.basename(combined_pdf_path)}")
    
    # Extract grades
    print("🔍 Extracting grades...")
    grades_result = extract_grades(combined_pdf_path, print)
    
    # Convert to simple format
    grades_dict = {}
    for student_name, grade_info in grades_result.items():
        if isinstance(grade_info, dict) and 'grade' in grade_info:
            grades_dict[student_name] = grade_info['grade']
        else:
            grades_dict[student_name] = str(grade_info)
    
    print(f"📊 Extracted {len(grades_dict)} grades")
    for name, grade in grades_dict.items():
        print(f"   {name}: {grade}")
    
    # Update CSV
    import_file_path = os.path.join(class_folder, "Import file.csv")
    if os.path.exists(import_file_path):
        print("📝 Updating Import file...")
        df = pd.read_csv(import_file_path)
        
        # Find quiz column
        grade_columns = [col for col in df.columns if 'Points Grade' in col or 'Quiz' in col]
        if grade_columns:
            quiz_column = grade_columns[0]
        else:
            quiz_column = df.columns[-2]
        
        print(f"📊 Using column: {quiz_column}")
        
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
                    print(f"✅ Updated {student_name}: {grade}")
                else:
                    print(f"⚠️ Could not match: {student_name}")
        
        # Save updated CSV
        df.to_csv(import_file_path, index=False)
        print(f"✅ Updated {updated_count} grades in Import file")
    else:
        print("❌ Import file not found")

if __name__ == "__main__":
    main()
