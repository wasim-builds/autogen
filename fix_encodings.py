import os
import re

def fix_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Regex to find open(..., "r") or open(..., "rt")
        # and safely append encoding="utf-8"
        new_content = re.sub(
            r'open\(([^,]+),\s*(["\']r["\']|["\']rt["\'])\s*\)',
            r'open(\1, \2, encoding="utf-8")',
            content
        )
        
        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Fixed: {os.path.relpath(filepath, '/home/wasim/Projects/autogen')}")
    except Exception as e:
        print(f"Error processing {filepath}: {e}")

if __name__ == "__main__":
    target_dir = '/home/wasim/Projects/autogen/python'
    count = 0
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.endswith('.py'):
                fix_file(os.path.join(root, file))
