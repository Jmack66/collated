import os
import re

# Configuration
SOURCES_DIR = 'sources'
OUTPUT_FILE = 'index.html'

# Order of categories to appear on the page
CATEGORY_ORDER = [
    'machinists',
    'electronics',
    'workshop',
    'aesthetics',
    'software',
    'opinions_lifestyle'
]

# Metadata for each category
CATEGORY_META = {
    'machinists': {'title': 'Machinists', 'class': 'cat-machinists'},
    'electronics': {'title': 'Electronics', 'class': 'cat-electronics'},
    'workshop': {'title': 'Workshop & Builds', 'class': 'cat-workshop'},
    'aesthetics': {'title': 'Aesthetics & Design', 'class': 'cat-aesthetics'},
    'software': {'title': 'Software & Tech', 'class': 'cat-software'},
    'opinions_lifestyle': {'title': 'Opinions and Lifestyle', 'class': 'cat-opinions-lifestyle'}
}

HTML_HEADER = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Inspiration Sources</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <header>
        <h1>Sources</h1>
        <p class="intro">A curated list of makers, machinists, and aesthetic inspiration.</p>
    </header>

    <main>
"""

HTML_FOOTER = """    </main>

    <footer>
        <p>Collated with &hearts;</p>
    </footer>
</body>
</html>
"""

def parse_markdown_links(content):
    """Extracts title and URL from markdown links: - [Title](URL)"""
    links = []
    # Regex to capture [Title](URL)
    pattern = re.compile(r'-\s*\[(.*?)\]\((.*?)\)')
    for line in content.splitlines():
        match = pattern.search(line)
        if match:
            links.append({'title': match.group(1), 'url': match.group(2)})
    return links

def generate_section_html(key, links):
    meta = CATEGORY_META.get(key, {'title': key.capitalize(), 'class': f'cat-{key}'})
    
    html = f"""        <!-- Category: {meta['title']} -->
        <section class="{meta['class']}">
            <div class="category-header">
                <span class="category-marker"></span>
                <h2>{meta['title']}</h2>
            </div>
            <ul>
"""
    
    for link in links:
        # Simplistic domain extraction for display
        display_url = link['url'].replace('https://', '').replace('http://', '').replace('www.', '')
        if display_url.endswith('/'):
            display_url = display_url[:-1]
            
        html += f"""                <li><a href="{link['url']}" target="_blank">
                    <span class="source-name">{link['title']}</span>
                    <span class="source-url">{display_url}</span>
                </a></li>
"""
    
    html += """            </ul>
        </section>

"""
    return html

def main():
    if not os.path.exists(SOURCES_DIR):
        print(f"Error: Directory '{SOURCES_DIR}' not found.")
        return

    main_content = ""

    for key in CATEGORY_ORDER:
        filename = f"{key}.md"
        filepath = os.path.join(SOURCES_DIR, filename)
        
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                content = f.read()
            
            links = parse_markdown_links(content)
            if links:
                main_content += generate_section_html(key, links)
        else:
            print(f"Warning: File '{filepath}' not found.")

    full_html = HTML_HEADER + main_content + HTML_FOOTER

    with open(OUTPUT_FILE, 'w') as f:
        f.write(full_html)
    
    print(f"Successfully rebuilt {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
