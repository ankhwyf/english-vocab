#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""往词库里追加一篇课文的生词（不再重扫整个 Flowus 数据库）。

用法：
  python3 scripts/add_words.py --group "Hello! I'm a Spider" \
      crawl:crawl -- 爬（贴地慢爬，虫子、蜗牛、婴儿都用它） \
      snail:snail -- 蜗牛

或者先把条目写进 JSON 再用 --json 传入：
  python3 scripts/add_words.py --group X --json new.json
  # new.json: [{"en":"crawl","zh":"爬"}, ...]

只做三件事：合并进 words.json（同词只补释义/来源）、重排、重新生成
words.csv / words.js / words.md。已存在的词不会重复添加。
"""
import argparse, csv, json, os, sys
from collections import Counter
from itertools import groupby

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORDS = os.path.join(OUT, 'words.json')


def load():
    with open(WORDS, encoding='utf-8') as f:
        return json.load(f)


def write_all(words):
    words = sorted(words, key=lambda x: (x['group'], x['en']))
    with open(WORDS, 'w', encoding='utf-8') as f:
        json.dump(words, f, ensure_ascii=False, indent=1)

    with open(os.path.join(OUT, 'words.csv'), 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['单词', '中文', '来源课程'])
        for v in words:
            w.writerow([v['en'], v['zh'], ' / '.join(v['src'])])

    js = 'window.WORDS = ' + json.dumps(words, ensure_ascii=False, indent=1) + ';\n'
    with open(os.path.join(OUT, 'words.js'), 'w', encoding='utf-8') as f:
        f.write(js)

    lines = ['# 英语生词库', '',
             f'共 **{len(words)}** 条，按课程分组。新增课文时用 scripts/add_words.py 追加。', '',
             '按课程分组，方便按主题出题。', '']
    for g, grp in groupby(words, key=lambda x: x['group']):
        items = list(grp)
        lines += [f'## {g}（{len(items)}）', '', '| 单词 | 中文 |', '| --- | --- |']
        lines += [f"| {v['en']} | {v['zh']} |" for v in items]
        lines.append('')
    with open(os.path.join(OUT, 'words.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    return words


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--group', required=True, help='课程名，作为分组')
    ap.add_argument('--json', help='从 JSON 文件读条目：[{"en":..,"zh":..}]')
    ap.add_argument('pairs', nargs='*', help='en:zh 形式，如 crawl:爬')
    a = ap.parse_args()

    new = []
    if a.json:
        new += [{'en': v['en'], 'zh': v['zh']} for v in json.load(open(a.json, encoding='utf-8'))]
    for p in a.pairs:
        if ':' not in p:
            print('跳过（缺 zh）:', p); continue
        en, zh = p.split(':', 1)
        new.append({'en': en.strip().lower(), 'zh': zh.strip()})

    words = load()
    idx = {w['en']: w for w in words}
    added, merged = [], []
    for v in new:
        en = v['en'].strip().lower()
        if en in idx:
            w = idx[en]
            if not w.get('zh') and v['zh']:
                w['zh'] = v['zh']
            if a.group not in (w.get('src') or []):
                w.setdefault('src', []).append(a.group)
            merged.append(en)
        else:
            w = {'en': en, 'zh': v['zh'], 'src': [a.group], 'group': a.group}
            words.append(w); idx[en] = w; added.append(en)

    words = write_all(words)
    print('新增:', added or '无')
    print('已存在（补来源）:', merged or '无')
    print('总数:', len(words))


if __name__ == '__main__':
    main()
