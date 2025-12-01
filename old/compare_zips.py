#!/usr/bin/env python3
"""Compare two ZIP files to find differences"""
import zipfile
import sys
import os

if len(sys.argv) != 3:
    print("Usage: python compare_zips.py <zip1> <zip2>")
    sys.exit(1)

zip1_path = sys.argv[1]
zip2_path = sys.argv[2]

if not os.path.exists(zip1_path):
    print(f"ERROR: {zip1_path} not found")
    sys.exit(1)

if not os.path.exists(zip2_path):
    print(f"ERROR: {zip2_path} not found")
    sys.exit(1)

print("=" * 60)
print("COMPARING ZIP FILES")
print("=" * 60)
print(f"\nZIP 1: {os.path.basename(zip1_path)}")
print(f"ZIP 2: {os.path.basename(zip2_path)}")

with zipfile.ZipFile(zip1_path, 'r') as z1, zipfile.ZipFile(zip2_path, 'r') as z2:
    files1 = set(z1.namelist())
    files2 = set(z2.namelist())
    
    print(f"\nZIP 1 has {len(files1)} files")
    print(f"ZIP 2 has {len(files2)} files")
    
    # Check index.html
    has_index1 = 'index.html' in files1
    has_index2 = 'index.html' in files2
    print(f"\nZIP 1 has index.html: {has_index1}")
    print(f"ZIP 2 has index.html: {has_index2}")
    
    if has_index1 and has_index2:
        info1 = z1.getinfo('index.html')
        info2 = z2.getinfo('index.html')
        print(f"\nindex.html comparison:")
        print(f"  ZIP 1: size={info1.file_size}, compressed={info1.compress_size}, compress_type={info1.compress_type} (0=STORED, 8=DEFLATED)")
        print(f"  ZIP 2: size={info2.file_size}, compressed={info2.compress_size}, compress_type={info2.compress_type}")
        
        # Read and compare content
        content1 = z1.read('index.html')
        content2 = z2.read('index.html')
        print(f"  Content identical: {content1 == content2}")
        if content1 != content2:
            print(f"  Content length diff: {len(content1) - len(content2)} bytes")
    
    # Check root-level files
    root_files1 = [f for f in files1 if '/' not in f]
    root_files2 = [f for f in files2 if '/' not in f]
    print(f"\nRoot-level files:")
    print(f"  ZIP 1: {root_files1}")
    print(f"  ZIP 2: {root_files2}")
    
    # Find differences
    only_in_1 = files1 - files2
    only_in_2 = files2 - files1
    
    if only_in_1:
        print(f"\nFiles only in ZIP 1 ({len(only_in_1)}):")
        for f in sorted(list(only_in_1))[:10]:
            print(f"  {f}")
        if len(only_in_1) > 10:
            print(f"  ... and {len(only_in_1) - 10} more")
    
    if only_in_2:
        print(f"\nFiles only in ZIP 2 ({len(only_in_2)}):")
        for f in sorted(list(only_in_2))[:10]:
            print(f"  {f}")
        if len(only_in_2) > 10:
            print(f"  ... and {len(only_in_2) - 10} more")
    
    # Check compression types
    comp1 = set([z1.getinfo(f).compress_type for f in files1])
    comp2 = set([z2.getinfo(f).compress_type for f in files2])
    print(f"\nCompression types used:")
    print(f"  ZIP 1: {comp1}")
    print(f"  ZIP 2: {comp2}")
    
    # Check if folders match
    folders1 = set([f.split('/')[0] for f in files1 if '/' in f])
    folders2 = set([f.split('/')[0] for f in files2 if '/' in f])
    print(f"\nTop-level folders:")
    print(f"  ZIP 1: {len(folders1)} folders")
    print(f"  ZIP 2: {len(folders2)} folders")
    
    only_folders1 = folders1 - folders2
    only_folders2 = folders2 - folders1
    
    if only_folders1:
        print(f"  Folders only in ZIP 1: {only_folders1}")
    if only_folders2:
        print(f"  Folders only in ZIP 2: {only_folders2}")

print("\n" + "=" * 60)

