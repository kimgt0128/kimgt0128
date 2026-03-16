import feedparser
import re
from datetime import datetime

def clean_html(raw_html):
    """HTML 태그 제거 및 공백 정리"""
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    cleantext = re.sub(r'\s+', ' ', cleantext)
    return cleantext.strip()

def get_thumbnail(entry):
    """RSS에서 썸네일 URL 추출"""
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
    """날짜 형식 변환 (YYYY.MM.DD)"""
    try:
        date_obj = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
        return date_obj.strftime('%Y.%m.%d')
    except:
        return date_str

def create_blog_table(feed_url, max_posts=6):
    """3x2 마크다운 테이블 생성"""
    feed = feedparser.parse(feed_url)
    entries = feed.entries[:max_posts]
    
    table = "| | | |\n|---|---|---|\n"
    
    for i in range(0, len(entries), 3):
        row_entries = entries[i:i+3]
        row = "|"
        for entry in row_entries:
            if entry:
                thumbnail = get_thumbnail(entry)
                title = entry.title
                link = entry.link
                description = clean_html(entry.get('description', ''))[:50] + '...'
                pub_date = format_date(entry.get('published', ''))
                
                cell = f'<a href="{link}"><img src="{thumbnail}" width="300" height="200" alt="{title}"></a><br/>' \
                       f'**[{title}]({link})**<br/>{description}<br/>{pub_date}'
                row += f" {cell} |"
            else:
                row += " |"
        
        table += row + "\n"
        
    return table

def update_readme(readme_path, table_content):
    """마커 사이의 내용을 업데이트"""
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()

    start_marker = "<!-- BLOG_START -->"  # ✅ README.md와 완전히 동일
    end_marker = "<!-- BLOG_END -->"      # ✅ README.md와 완전히 동일

    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker)

    # ✅ 마커 못 찾으면 즉시 종료 (맨 위에 쓰는 버그 방지)
    if start_idx == -1 or end_idx == -1:
        print(f"❌ 마커를 찾을 수 없습니다! README.md에 아래 두 줄이 있는지 확인하세요.")
        print(f"   {start_marker}")
        print(f"   {end_marker}")
        exit(1)

    new_content = (
        content[:start_idx + len(start_marker)] +
        "\n" + table_content + "\n" +
        content[end_idx:]
    )

    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("✅ README.md updated successfully!")

if __name__ == "__main__":
    RSS_FEED_URL = "https://wondrous-developer.tistory.com/rss"
    README_PATH = "README.md"
    
    print("📡 Fetching blog posts...")
    table = create_blog_table(RSS_FEED_URL, max_posts=6)
    
    print("📝 Updating README.md...")
    update_readme(README_PATH, table)