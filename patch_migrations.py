import glob
import re

for filepath in glob.glob("backend/apps/*/migrations/*.py"):
    with open(filepath, "r") as f:
        content = f.read()

    # Find any on_delete=django.db.models.deletion.* and append db_constraint=False
    new_content = re.sub(
        r"(on_delete=django\.db\.models\.deletion\.[A-Z_]+)",
        r"\1, db_constraint=False",
        content
    )
    
    if new_content != content:
        with open(filepath, "w") as f:
            f.write(new_content)
        print(f"Patched {filepath}")

print("All migrations patched for db_constraint=False.")
