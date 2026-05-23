import os
import glob
import re

for file002 in glob.glob("backend/apps/*/migrations/0002_initial.py"):
    app_dir = os.path.dirname(file002)
    file001 = os.path.join(app_dir, "0001_initial.py")
    
    if not os.path.exists(file001):
        continue
        
    with open(file002, "r") as f:
        content2 = f.read()
        
    with open(file001, "r") as f:
        content1 = f.read()
        
    # Extract operations from 0002_initial.py
    # They are in a list operations = [...]
    ops_match = re.search(r"operations\s*=\s*\[(.*?)\]\s*$", content2, re.DOTALL)
    if ops_match:
        ops = ops_match.group(1).strip()
        # Find where operations = [ ends in 0001_initial.py
        # We can just inject them into the end of operations in 0001
        content1 = re.sub(r"(operations\s*=\s*\[)", r"\1\n        " + ops.replace("\\", "\\\\") + ",", content1, count=1)
        
        # We also need to add swappable_dependency to 0001_initial.py dependencies
        if "swappable_dependency" in content2:
            content1 = content1.replace("from django.db import migrations, models", "from django.db import migrations, models\nfrom django.conf import settings")
            content1 = re.sub(r"(dependencies\s*=\s*\[)", r"\1\n        migrations.swappable_dependency(settings.AUTH_USER_MODEL),", content1)
            
        with open(file001, "w") as f:
            f.write(content1)
            
    # Delete 0002_initial.py
    os.remove(file002)

print("Merged all 0002_initial.py into 0001_initial.py")
