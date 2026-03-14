import feedparser
import re
from datetime import datetime

def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    cleantext = re.sub(r'\s+', ' ', cleantext)
    return cleantext.strip()

def get_thumbnail(entry):
    if hasattr(entry, 'media_thumbnail'):
        return entry.media_thumbnail[0]['url']
    if hasattr(entry, 'enclosures') and entry.enclosures:
        for enclosure in entry.enclosures:
            if enclosure.get('type', '').startswith('image/'):
                return enclosure.get('url')
    if hasattr(entry, 'description'):
        img_match = re.search(r'<img[^>]+src="([^"]+)"', entry.description)
        if img_match:
            return img_match.group(1)
    return "https://github.com/user-attachments/assets/9ffcad01-a362-4ad3-b3eb-f648be5d75de"

def format_date(date_str):
    try:
        date_obj = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
        return date_obj.strftime('%Y.%m.%d')
    except:
        return date_str

def create_blog_table(feed_url, max_posts=6):
    feed = feedparser.parse(feed_url)
    entries = feed.entries[:max_posts]
    table = "| | | |\n|---|---|---|\n"
    for i in range(0, len(entries), 3):
        row_entries = entries[i:i+3]
        row = "|"
        for entry in row_entries:
            thumbnail = get_thumbnail(entry)
            title = entry.title
            link = entry.link
            description = clean_html(entry.get('description', ''))[:50] + '...'
            pub_date = format_date(entry.get('published', ''))
            cell = f'<a href="{link}"><img src="{thumbnail}" width="300" height="200" alt="{title}"></a><br/>' \
                   f'**[{title}]({link})**<br/>{description}<br/>{pub_date}'
            row += f" {cell} |"
        while len(row_entries) < 3:
            row += " |"
            row_entries.append(None)
        table += row + "\n"
    return table

def update_readme(readme_path, table_content):
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    start_marker = ""
    end_marker = ""
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker)
    if start_idx != -1 and end_idx != -1:
        new_content = (
            content[:start_idx + len(start_marker)] +
            "\n" + table_content + "\n" +
            content[end_idx:]
        )
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("✅ README.md updated!")
    else:
        print("❌ Markers not found!")

if __name__ == "__main__":
    # kimgt0128님의 블로그 RSS 주소
    RSS_FEED_URL = "https://wondrous-developer.tistory.com/rss"
    table = create_blog_table(RSS_FEED_URL, max_posts=6)
    update_readme("README.md", table)