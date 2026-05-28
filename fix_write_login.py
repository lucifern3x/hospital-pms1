#!/usr/bin/env python3
"""Generate complete write_login.py from scratch."""
import os

# Read the original content
src = r'D:\hospital_pms\hospital_pms\write_login.py'

# The original content (lines 1-404) is stored directly
# We need to rewrite the file completely

# First, let's just write the correct content from a known clean starting point
# Read what we have now
with open(src, 'r', encoding='utf-8') as f:
    content = f.read()

# Find all function defs
import re
funcs = list(re.finditer(r'^def _part\d+_\w+\(', content, re.MULTILINE))
print(f"Found {len(funcs)} functions:")
for f in funcs:
    print(f"  {f.group()} at pos {f.start()}")

# Find end of _part4
idx4_end = content.find('"""\n', content.find('def _part4'))
if idx4_end > 0:
    idx4_end += 5  # past the closing """
    print(f"_part4 ends at pos {idx4_end}")
    
    # Keep up to _part4 end
    clean = content[:idx4_end]
    
    # Write back
    with open(src, 'w', encoding='utf-8') as f:
        f.write(clean)
    print(f"Wrote {len(clean)} chars to file")
else:
    print("Could not find _part4 end")

