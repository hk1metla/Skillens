#!/usr/bin/env python3
"""
Word count tool for LaTeX documents.
Counts words by chapter, excluding LaTeX commands and comments.
"""
import re
import sys

def extract_chapter_content(text, chapter_num):
    """Extract content for a specific chapter."""
    # Pattern to match chapter sections
    patterns = [
        rf'\\section\{{.*?Chapter {chapter_num}.*?\}}',
        rf'\\section\{{.*?{chapter_num}\..*?\}}',
    ]
    
    # Find chapter start
    chapter_start = None
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            chapter_start = match.start()
            break
    
    if chapter_start is None:
        # Try to find by section number
        sections = list(re.finditer(r'\\section\{', text))
        if chapter_num <= len(sections):
            chapter_start = sections[chapter_num - 1].start()
    
    if chapter_start is None:
        return ""
    
    # Find next chapter or end of document
    next_chapter = re.search(r'\\section\{', text[chapter_start + 1:])
    if next_chapter:
        chapter_end = chapter_start + 1 + next_chapter.start()
    else:
        chapter_end = len(text)
    
    return text[chapter_start:chapter_end]

def clean_latex_text(text):
    """Remove LaTeX commands, comments, and formatting."""
    # Remove comments
    text = re.sub(r'%.*?$', '', text, flags=re.MULTILINE)
    
    # Remove LaTeX commands (but keep content in braces)
    text = re.sub(r'\\[a-zA-Z]+\*?(\[[^\]]*\])?(\{[^\}]*\})*', ' ', text)
    
    # Remove remaining braces
    text = re.sub(r'\{[^\}]*\}', ' ', text)
    text = re.sub(r'\[[^\]]*\]', ' ', text)
    
    # Remove special LaTeX characters
    text = re.sub(r'[\\&%$#_{}]', ' ', text)
    
    # Remove citations
    text = re.sub(r'\\citep?\{[^\}]*\}', ' ', text)
    text = re.sub(r'\\cite\{[^\}]*\}', ' ', text)
    
    # Remove references
    text = re.sub(r'\\ref\{[^\}]*\}', ' ', text)
    text = re.sub(r'\\label\{[^\}]*\}', ' ', text)
    
    # Remove figure/table includes
    text = re.sub(r'\\includegraphics.*?\{[^\}]*\}', ' ', text)
    text = re.sub(r'\\input\{[^\}]*\}', ' ', text)
    
    # Remove environments (but keep content)
    text = re.sub(r'\\begin\{[^\}]*\}', ' ', text)
    text = re.sub(r'\\end\{[^\}]*\}', ' ', text)
    
    # Remove itemize/enumerate markers
    text = re.sub(r'\\item', ' ', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def count_words(text):
    """Count words in cleaned text."""
    words = text.split()
    # Filter out very short "words" that are likely artifacts
    words = [w for w in words if len(w) > 1 or w.isalnum()]
    return len(words)

def main():
    file_path = "latex_documentation"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: {file_path} not found")
        sys.exit(1)
    
    # Chapter names mapping
    chapters = {
        1: "Introduction",
        2: "Literature Review", 
        3: "Design",
        4: "Implementation",
        5: "Evaluation",
        6: "Conclusion"
    }
    
    print("=" * 60)
    print("LaTeX Word Count by Chapter")
    print("=" * 60)
    print()
    
    total_words = 0
    limits = {
        1: 1000,
        2: 2500,
        3: 2000,
        4: 2500,
        5: 2500,
        6: 1000
    }
    total_limit = 10500
    
    results = []
    
    for num, name in chapters.items():
        chapter_text = extract_chapter_content(content, num)
        cleaned = clean_latex_text(chapter_text)
        word_count = count_words(cleaned)
        total_words += word_count
        limit = limits[num]
        status = "OK" if word_count <= limit else "EXCEEDS"
        
        results.append({
            'num': num,
            'name': name,
            'words': word_count,
            'limit': limit,
            'status': status
        })
        
        print(f"Chapter {num}: {name}")
        print(f"  Words: {word_count:,} / {limit:,} {status}")
        print()
    
    print("=" * 60)
    print(f"TOTAL: {total_words:,} / {total_limit:,}")
    print(f"Status: {'✓ OK' if total_words <= total_limit else '✗ EXCEEDS'}")
    print("=" * 60)
    print()
    
    # Generate LaTeX table code
    print("LaTeX Table Code:")
    print("-" * 60)
    print("\\begin{tabularx}{\\textwidth}{|l|r|r|X|}")
    print("\\hline")
    print("\\textbf{Chapter} & \\textbf{Words} & \\textbf{Limit} & \\textbf{Status} \\\\")
    print("\\hline")
    
    for r in results:
        print(f"{r['num']}. {r['name']} & {r['words']:,} & {r['limit']:,} & {r['status']} \\\\")
        print("\\hline")
    
    print(f"\\textbf{{TOTAL}} & \\textbf{{{total_words:,}}} & \\textbf{{{total_limit:,}}} & \\textbf{{{'OK' if total_words <= total_limit else 'EXCEEDS'}}} \\\\")
    print("\\hline")
    print("\\end{tabularx}")

if __name__ == "__main__":
    main()
