# fix_all_templates.py
import os
import re

def fix_templates():
    templates_dir = 'frontend/templates'
    
    for filename in os.listdir(templates_dir):
        if filename.endswith('.html'):
            filepath = os.path.join(templates_dir, filename)
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Fix the CSS link syntax error
            # Pattern: href="{{ url_for('static', filename='css/style.css'|category_color }}"
            # Should be: href="{{ url_for('static', filename='css/style.css') }}"
            fixed_content = re.sub(
                r'href="{{ url_for\(\'static\', filename=\'css/style\.css\'\|category_color }}"',
                'href="{{ url_for(\'static\', filename=\'css/style.css\') }}"',
                content
            )
            
            # Also fix any other filter syntax errors in url_for
            fixed_content = re.sub(
                r'url_for\([^)]+\|[^)]+\)',
                lambda m: m.group().split('|')[0] + ')',
                fixed_content
            )
            
            if content != fixed_content:
                with open(filepath, 'w') as f:
                    f.write(fixed_content)
                print(f"✅ Fixed {filename}")
            else:
                print(f"✓ {filename} already OK")

if __name__ == '__main__':
    fix_templates()