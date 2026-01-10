import requests
import json
import os
from datetime import datetime
import urllib3

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Hacker News API 基础 URL
BASE_URL = "https://hacker-news.firebaseio.com/v0"

def fetch_top_stories(limit=30):
    """获取热门故事的 ID 列表"""
    url = f"{BASE_URL}/topstories.json"
    response = requests.get(url, verify=False, timeout=10)
    story_ids = response.json()
    return story_ids[:limit]

def fetch_story_detail(story_id):
    """获取单个故事的详细信息"""
    url = f"{BASE_URL}/item/{story_id}.json"
    try:
        response = requests.get(url, verify=False, timeout=10)
        return response.json()
    except Exception as e:
        print(f"  ⚠️  获取故事 {story_id} 失败: {str(e)[:50]}")
        return None

def filter_ai_stories(stories):
    """筛选出 AI 相关的故事"""
    ai_keywords = ['ai', 'artificial intelligence', 'machine learning',
                   'ml', 'deep learning', 'llm', 'gpt', 'openai',
                   'claude', 'chatgpt', 'neural']

    ai_stories = []
    for story in stories:
        title = story.get('title', '').lower()
        if any(keyword in title for keyword in ai_keywords):
            ai_stories.append(story)

    return ai_stories

def save_to_json(data, filename):
    """保存数据到 JSON 文件"""
    os.makedirs('data', exist_ok=True)
    filepath = os.path.join('data', filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ 数据已保存到 {filepath}")

def main():
    print("🚀 开始爬取 Hacker News AI 相关热门故事...")

    # 1. 获取热门故事 ID
    story_ids = fetch_top_stories(limit=30)
    print(f"📊 获取到 {len(story_ids)} 个热门故事 ID")

    # 2. 获取每个故事的详情
    stories = []
    for i, story_id in enumerate(story_ids, 1):
        print(f"⏳ 正在获取第 {i}/{len(story_ids)} 个故事...")
        story = fetch_story_detail(story_id)
        if story and story.get('type') == 'story':
            stories.append({
                'title': story.get('title'),
                'url': story.get('url'),
                'score': story.get('score'),
                'by': story.get('by'),
                'time': story.get('time'),
                'descendants': story.get('descendants', 0),  # 评论数
                'hn_url': f"https://news.ycombinator.com/item?id={story_id}"
            })

    print(f"✅ 成功获取 {len(stories)} 个故事详情")

    # 3. 筛选 AI 相关故事
    ai_stories = filter_ai_stories(stories)
    print(f"🤖 筛选出 {len(ai_stories)} 个 AI 相关故事")

    # 4. 保存数据
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    save_to_json(ai_stories, f'hn_ai_stories_{timestamp}.json')

    # 5. 显示部分结果
    print("\n📰 部分 AI 相关故事：")
    for story in ai_stories[:5]:
        print(f"  • {story['title']} (👍 {story['score']})")

if __name__ == '__main__':
    main()
