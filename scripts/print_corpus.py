import json
d = json.load(open('corpus_ledger.json', 'r', encoding='utf-8'))
papers = d['entries']
for p in papers:
    yr = p.get('year') or '?'
    cites = p.get('cited_by_count', 0)
    arxiv = p.get('arxiv_id') or ''
    oa = 'OA' if p.get('is_oa') else ''
    print(f"{p['id']:>3} | {p['title'][:72]:72} | {yr:>5} | {cites:>5} | {oa:>3} | {arxiv}")
print(f"\nTotal: {len(papers)} papers")
