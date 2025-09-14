#!/usr/bin/env python3
"""
Fix import paths in all test files to use consistent pattern
"""

import os
import re
from pathlib import Path

def fix_import_path(file_path):
    """Fix import path in a single file"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match various import path setups
    patterns_to_replace = [
        (r'prj_root = Path\(__file__\)\.parent\s*\nsys\.path\.insert\(0, str\(prj_root\)\)',
         'prj_root = Path(__file__).parent.parent\nsys.path.insert(0, str(prj_root))'),
        
        (r'src_path = Path\(__file__\)\.parent / "src"\s*\nsys\.path\.insert\(0, str\(src_path\)\)',
         'prj_root = Path(__file__).parent.parent\nsys.path.insert(0, str(prj_root))'),
         
        (r'src_path = Path\(__file__\)\.parent\.parent\s*\nsys\.path\.insert\(0, str\(src_path\)\)',
         'prj_root = Path(__file__).parent.parent\nsys.path.insert(0, str(prj_root))'),
         
        # For files that just had parent without parent.parent
        (r'# Add project root to path\s*\nprj_root = Path\(__file__\)\.parent\s*\nsys\.path\.insert\(0, str\(prj_root\)\)',
         '# Add project root to path\nprj_root = Path(__file__).parent.parent\nsys.path.insert(0, str(prj_root))')
    ]
    
    # Apply replacements
    updated = False
    for pattern, replacement in patterns_to_replace:
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            updated = True
    
    # Check if file needs the standard import pattern added
    if 'sys.path.insert' not in content and 'from src.' in content:
        # Add standard import setup after pathlib import
        import_addition = """
# Add project root to path
prj_root = Path(__file__).parent.parent
sys.path.insert(0, str(prj_root))
"""
        
        # Insert after pathlib import
        if 'from pathlib import Path' in content:
            content = content.replace('from pathlib import Path', 'from pathlib import Path' + import_addition)
            updated = True
        elif 'import sys' in content and 'from pathlib' not in content:
            content = content.replace('import sys', 'import sys\nfrom pathlib import Path' + import_addition)
            updated = True
    
    # Write back if updated
    if updated:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    return False

def main():
    """Fix import paths in all test files"""
    
    tests_dir = Path(__file__).parent
    
    # Find all Python files in tests directory
    test_files = list(tests_dir.glob('*.py'))
    
    print(f"🔧 FIXING IMPORT PATHS IN TEST FILES")
    print(f"Found {len(test_files)} Python files in tests directory")
    print("=" * 60)
    
    fixed_count = 0
    
    for file_path in test_files:
        if file_path.name == __file__.split('/')[-1]:  # Skip this script
            continue
            
        try:
            if fix_import_path(file_path):
                print(f"✅ Fixed: {file_path.name}")
                fixed_count += 1
            else:
                print(f"⏭️  Skipped: {file_path.name} (no changes needed)")
                
        except Exception as e:
            print(f"❌ Error fixing {file_path.name}: {e}")
    
    print("=" * 60)
    print(f"📊 SUMMARY: Fixed {fixed_count} files")
    print()
    print("✅ All test files should now use consistent import pattern:")
    print("   prj_root = Path(__file__).parent.parent")
    print("   sys.path.insert(0, str(prj_root))")

if __name__ == "__main__":
    main()