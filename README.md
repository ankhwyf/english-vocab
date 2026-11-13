# 英语生词库

从 Flowus 绘本笔记里自动提取的「生疏词」清单 —— 也就是你在 `单词` 列里用**代码块或加粗**标出来的那些。

**用途定位**：这里是**取词素材库**，不是单词专项练习册。每整理完一篇新课文，出练习题和中译英时
从这里抓一批旧词混进去，让学过的词在新句子里反复复现。练习永远跟着课文走，不单独按词出题。

- **240 条**，覆盖 60 个课程/主题（字母书、SUPER CUTE!、Animal Safari、Read and Play 等）
- 每条带中文释义，按来源课程分组

## 文件

| 文件 | 用途 |
| --- | --- |
| `words.json` | 主数据。`{en, zh, src, group}` |
| `words.csv` | 导入 Excel / Anki 用（UTF-8 BOM，Excel 直接打开不乱码） |
| `words.js` | 给本地 HTML 读的版本（`window.WORDS`），避开 `file://` 的 fetch 限制 |
| `words.md` | 人读版，按课程分组的表格 |
| `practice.html` | **生词练习器**：英→中 / 中→英 四选一，自动记错词，可只练错词、按课程筛范围 |
| `practice-standalone.html` | 同一个练习器，**数据已内嵌**（32 KB 单文件，发给别人也不会缺 words.js） |
| `word-family-practice.html` | 词族三课练习册（Gum on the Rug / Look at My Pen / Look at It Go，28 题） |

## 怎么用

双击 `practice.html`，浏览器打开即可，不需要联网、不需要起服务。

- 每轮 10 题，答错的词会进「错词本」，顶部可切换范围
- `practice-standalone.html` 是自包含版本，单个文件拷走就能用；`practice.html` 需要和 `words.js` 放一起
- 键盘 `1`–`4` 直接选
- 进度和错词存在浏览器 localStorage 里，关掉再开还在

## 怎么更新

数据来自 Flowus 数据库 `6da864d4-5037-41b0-997f-1db473f90f71` 的「单词」列：
凡是设成**代码块**或**加粗**的片段，按 `英文(中文释义)` 的格式解析。

在 Flowus 里加了新词之后，重新跑一次 `scripts/build_vocab.py`（需要 `flowus` CLI 和 token）：

```sh
export FLOWUS_TOKEN=...
python3 scripts/build_vocab.py
```

脚本会重新生成 `words.json / words.csv / words.js / words.md` 四个文件。
新词如果在脚本的 `ZH` 字典里没有释义，会被剔除并打印出来，补一行就行。

## 同步到 GitHub

仓库：https://github.com/ankhwyf/english-vocab

```sh
git add -A
git commit -m "更新生词库"
git push
```

换电脑：

```sh
git clone git@github.com:ankhwyf/english-vocab.git
cd english-vocab
open practice.html
```

用 https 克隆也行（`https://github.com/ankhwyf/english-vocab.git`），但推送需要 token；
这台机器走的是 SSH，密钥在 `WorkBuddy/2026-09-30-17-09-49/.ssh/id_ed25519`，
仓库里用 `core.sshCommand` 指向它。换机器时在那个 GitHub 账号下再加一把公钥即可。
