# merge_course_markdown.py

import os

input_dir = "tds_pages_md"
output_file = "course.md"

with open(output_file, "w", encoding="utf-8") as outfile:
    for filename in sorted(os.listdir(input_dir)):
        if filename.endswith(".md"):
            filepath = os.path.join(input_dir, filename)
            with open(filepath, "r", encoding="utf-8") as infile:
                content = infile.read()
                outfile.write(f"\n\n---\n# {filename.replace('_', ' ').replace('.md', '')}\n\n")
                outfile.write(content)
