import os
import re

# Configuration
SOURCES_DIR = "sources"
OUTPUT_FILE = "index.html"

# Predefined colors for tags to give a minimal "pop of color"
TAG_COLORS = {
    "machinists": "#2ed573",
    "electronics": "#ffa502",
    "workshop": "#ff4757",
    "aesthetics": "#1e90ff",
    "software": "#a55eea",
    "opinions_lifestyle": "#ff6b81",
    "agriculture_solarpunk": "#00b894",
    "research": "#f39c12",
    "film_inspiration": "#8e44ad",
}

# Fallback palette for any dynamic/inline tags added
FALLBACK_PALETTE = [
    "#ff9ff3",
    "#feca57",
    "#ff6b6b",
    "#48dbfb",
    "#1dd1a1",
    "#5f27cd",
    "#c8d6e5",
    "#ff9a9e",
]


def get_tag_color(tag):
    normalized = tag.lower().replace(" ", "_")
    if normalized in TAG_COLORS:
        return TAG_COLORS[normalized]
    hash_val = sum(ord(c) for c in normalized)
    return FALLBACK_PALETTE[hash_val % len(FALLBACK_PALETTE)]


def format_tag(tag):
    return tag.replace("_", " ").title()


def parse_markdown_links(content, default_tag):
    """Extracts title, URL, and inline tags from markdown links."""
    links = []
    # Regex to capture [Title](URL) and any trailing text for tags
    pattern = re.compile(r"-\s*\[(.*?)\]\((.*?)\)(.*)")
    for line in content.splitlines():
        match = pattern.search(line)
        if match:
            title = match.group(1).strip()
            url = match.group(2).strip()
            remainder = match.group(3).strip()

            # Extract inline tags starting with #
            inline_tags = [
                t.strip("#").lower() for t in remainder.split() if t.startswith("#")
            ]

            # Combine default tag (from filename) with inline tags
            tags = {default_tag.lower()}
            tags.update(inline_tags)

            display_url = (
                url.replace("https://", "").replace("http://", "").replace("www.", "")
            )
            if display_url.endswith("/"):
                display_url = display_url[:-1]

            links.append(
                {
                    "title": title,
                    "url": url,
                    "display_url": display_url,
                    "tags": sorted(list(tags)),
                }
            )
    return links


def build_html(all_links, all_unique_tags):
    html = [
        "<!DOCTYPE html>",
        '<html lang="en">',
        "<head>",
        '    <meta charset="UTF-8">',
        '    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
        "    <title>Inspiration Sources</title>",
        '    <link rel="stylesheet" href="styles.css">',
        "    <style>",
        "        /* Notion-style Tags & Grid Additions */",
        "        .filter-section { margin-bottom: 2rem; }",
        "        .filter-title { font-size: 0.9rem; margin-bottom: 0.8rem; font-family: var(--font-mono, monospace); color: #888; text-transform: uppercase; letter-spacing: 0.05em; }",
        "        .tag-filters { display: flex; flex-wrap: wrap; gap: 0.5rem; }",
        "        .tag-btn {",
        "            padding: 0.4rem 0.9rem;",
        "            border-radius: 20px;",
        "            border: 1px solid #eaeaea;",
        "            background: #fafafa;",
        "            font-size: 0.8rem;",
        "            font-family: var(--font-mono, monospace);",
        "            cursor: pointer;",
        "            transition: all 0.2s ease;",
        "            color: #555;",
        "            outline: none;",
        "        }",
        "        .tag-btn:hover { background: #f0f0f0; border-color: #ccc; }",
        "        .tag-btn.active {",
        "            color: #fff;",
        "            border-color: transparent;",
        "            box-shadow: 0 2px 6px rgba(0,0,0,0.15);",
        "            font-weight: bold;",
        "        }",
        "        .links-grid {",
        "            display: grid;",
        "            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));",
        "            gap: 1.5rem;",
        "            list-style: none;",
        "            padding: 0;",
        "        }",
        "        /* Overrides for existing generic 'a' styles in styles.css */",
        "        a.link-card {",
        "            padding: 1.2rem !important;",
        "            border: 1px solid #eaeaea !important;",
        "            border-radius: 12px;",
        "            background: #fff;",
        "            transition: all 0.2s ease;",
        "            display: flex;",
        "            flex-direction: column;",
        "            gap: 0.8rem;",
        "            text-decoration: none;",
        "            color: inherit;",
        "        }",
        "        a.link-card:hover {",
        "            background-color: #fff !important;",
        "            border-color: #ccc !important;",
        "            box-shadow: 0 4px 12px rgba(0,0,0,0.06);",
        "            transform: translateY(-2px);",
        "        }",
        "        .link-card .source-name {",
        "            font-weight: 600;",
        "            font-size: 1.1rem;",
        "            display: block;",
        "            color: var(--text-color, #111);",
        "        }",
        "        .link-card .source-url {",
        "            font-size: 0.8rem;",
        "            color: #888;",
        "            font-family: var(--font-mono, monospace);",
        "            word-break: break-all;",
        "            display: block;",
        "            margin-top: 0.2rem;",
        "        }",
        "        .card-tags {",
        "            display: flex;",
        "            flex-wrap: wrap;",
        "            gap: 0.4rem;",
        "            margin-top: auto;",
        "            padding-top: 0.5rem;",
        "        }",
        "        .card-tag {",
        "            font-size: 0.7rem;",
        "            padding: 0.2rem 0.6rem;",
        "            border-radius: 12px;",
        "            color: #fff;",
        "            font-family: var(--font-mono, monospace);",
        "            font-weight: 500;",
        "        }",
        "        .hidden { display: none !important; }",
        "    </style>",
        "</head>",
        "<body>",
        "    <header>",
        "        <h1>Sources</h1>",
        '        <p class="intro">A curated, filterable list of makers, machinists, and aesthetic inspiration.</p>',
        "    </header>",
        "    <main>",
        '        <section class="filter-section">',
        '            <div class="filter-title">Filter Tags</div>',
        '            <div class="tag-filters" id="tag-filters">',
    ]

    # Build tag buttons
    for tag in sorted(all_unique_tags):
        color = get_tag_color(tag)
        display_tag = format_tag(tag)
        # Store the base color as a CSS var for the active state toggle
        html.append(
            f'                <button class="tag-btn" data-tag="{tag}" style="--active-bg: {color};">{display_tag}</button>'
        )

    html.append("            </div>")
    html.append("        </section>")
    html.append('        <div class="links-grid" id="links-grid">')

    # Build link cards
    for link in sorted(all_links, key=lambda x: x["title"].lower()):
        tags_str = ",".join(link["tags"])
        html.append(
            f'            <a href="{link["url"]}" target="_blank" class="link-card" data-tags="{tags_str}">'
        )
        html.append(f"                <div>")
        html.append(
            f'                    <span class="source-name">{link["title"]}</span>'
        )
        html.append(
            f'                    <span class="source-url">{link["display_url"]}</span>'
        )
        html.append(f"                </div>")
        html.append(f'                <div class="card-tags">')
        for tag in link["tags"]:
            color = get_tag_color(tag)
            display_tag = format_tag(tag)
            html.append(
                f'                    <span class="card-tag" style="background-color: {color};">{display_tag}</span>'
            )
        html.append(f"                </div>")
        html.append(f"            </a>")

    html.extend(
        [
            "        </div>",
            "    </main>",
            "    <footer>",
            "        <p>Collated with &hearts;</p>",
            "    </footer>",
            "    <script>",
            "        document.addEventListener('DOMContentLoaded', () => {",
            "            const tagBtns = document.querySelectorAll('.tag-btn');",
            "            const linkCards = document.querySelectorAll('.link-card');",
            "            let activeTags = new Set();",
            "",
            "            tagBtns.forEach(btn => {",
            "                btn.addEventListener('click', () => {",
            "                    const tag = btn.dataset.tag;",
            "                    const color = btn.style.getPropertyValue('--active-bg');",
            "                    if (activeTags.has(tag)) {",
            "                        activeTags.delete(tag);",
            "                        btn.classList.remove('active');",
            "                        btn.style.backgroundColor = '';",
            "                    } else {",
            "                        activeTags.add(tag);",
            "                        btn.classList.add('active');",
            "                        btn.style.backgroundColor = color;",
            "                    }",
            "                    filterLinks();",
            "                });",
            "            });",
            "",
            "            function filterLinks() {",
            "                if (activeTags.size === 0) {",
            "                    linkCards.forEach(card => card.classList.remove('hidden'));",
            "                    return;",
            "                }",
            "                linkCards.forEach(card => {",
            "                    const cardTags = card.dataset.tags.split(',');",
            "                    // Show if card has ALL selected tags (AND logic) ",
            "                    // Or ANY selected tag (OR logic). Using OR logic for easy browsing.",
            "                    const hasTag = cardTags.some(t => activeTags.has(t));",
            "                    if (hasTag) {",
            "                        card.classList.remove('hidden');",
            "                    } else {",
            "                        card.classList.add('hidden');",
            "                    }",
            "                });",
            "            }",
            "        });",
            "    </script>",
            "</body>",
            "</html>",
        ]
    )

    return "\n".join(html)


def main():
    if not os.path.exists(SOURCES_DIR):
        print(f"Error: Directory '{SOURCES_DIR}' not found.")
        return

    all_links = []
    all_unique_tags = set()

    # Process all markdown files
    for filename in os.listdir(SOURCES_DIR):
        if filename.endswith(".md"):
            filepath = os.path.join(SOURCES_DIR, filename)
            # The filename minus .md acts as the primary category/tag
            default_tag = filename[:-3]

            with open(filepath, "r") as f:
                content = f.read()

            links = parse_markdown_links(content, default_tag)
            all_links.extend(links)

            for link in links:
                all_unique_tags.update(link["tags"])

    # Generate and write HTML
    full_html = build_html(all_links, all_unique_tags)

    with open(OUTPUT_FILE, "w") as f:
        f.write(full_html)

    print(f"Successfully rebuilt {OUTPUT_FILE} with Notion-style tag filtering!")


if __name__ == "__main__":
    main()
