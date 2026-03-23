import json
import os
import urllib.request
import time

papers = [
    {"id": "1", "arxiv_id": "1912.01603"},
    {"id": "2", "arxiv_id": "2010.02193"},
    {"id": "3", "arxiv_id": "1906.08253"},
    {"id": "4", "arxiv_id": "1811.04551"},
    {"id": "5", "arxiv_id": "1805.12114"}
]

os.makedirs("papers", exist_ok=True)

for p in papers:
    pid = p["id"]
    arxiv = p["arxiv_id"]
    os.makedirs(f"papers/{pid}", exist_ok=True)
    
    url = f"https://alphaxiv.org/abs/{arxiv}.md"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            md_content = response.read().decode('utf-8')
            with open(f"papers/{pid}/paper.md", "w", encoding="utf-8") as f:
                f.write(md_content)
        print(f"Paper {pid} ({arxiv}): Fetched {len(md_content)} bytes")
    except Exception as e:
        print(f"Paper {pid} ({arxiv}): Failed at {url} - {e}")
        # Try finding overview
        url = f"https://alphaxiv.org/overview/{arxiv}.md"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                md_content = response.read().decode('utf-8')
                with open(f"papers/{pid}/paper.md", "w", encoding="utf-8") as f:
                    f.write(md_content)
            print(f"Paper {pid} ({arxiv}): Fetched {len(md_content)} bytes (overview)")
        except Exception as e:
            print(f"Paper {pid} ({arxiv}): Failed overview at {url} - {e}")
    time.sleep(1)
