import glob
import re

for model_file in glob.glob("backend/apps/*/models.py"):
    with open(model_file, "r") as f:
        content = f.read()
    
    # Remove previously added db_constraint=False just in case
    content = content.replace("db_constraint=False, ", "")
    
    # Prepend db_constraint=False to all ForeignKey and OneToOneField
    content = re.sub(r'(models\.(?:ForeignKey|OneToOneField)\s*\()', r'\1db_constraint=False, ', content)
    
    with open(model_file, "w") as f:
        f.write(content)

print("db_constraint=False added to all foreign keys.")
