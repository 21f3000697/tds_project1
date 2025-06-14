import os
import re
from typing import List, Dict, Tuple
def load_markdown_file(filepath: str) -> str:
    if not os.path.exists(filepath):
        return ""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def extract_links(markdown_text: str) -> List[Dict[str, str]]:
    pattern = r'\[([^\]]+)\]\((https?://[^\)]+)\)'
    matches = re.findall(pattern, markdown_text)
    return [{"text": text, "url": url} for text, url in matches]

def load_documents() -> List[Dict[str, str]]:
    course_md = load_markdown_file("course.md")
    discourse_md = load_markdown_file("discourse.md")

    return [
        {"source": "course", "content": course_md},
        {"source": "discourse", "content": discourse_md}
    ]


import difflib

def search_documents(query: str, documents: List[Dict]) -> Tuple[str, List[Dict[str, str]]]:
    query_lower = query.lower()
    best_match = ""
    best_score = 0.0
    best_links = []

    for doc in documents:
        paragraphs = doc["content"].split("\n\n")
        for para in paragraphs:
            score = difflib.SequenceMatcher(None, query_lower, para.lower()).ratio()
            if score > best_score:
                best_score = score
                best_match = para
                best_links = extract_links(para)

    if best_score > 0.3:  # Threshold to filter noise
        return best_match.strip(), best_links

    return "Sorry, I couldn't find a relevant answer.", []
