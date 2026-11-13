import json, re, subprocess, os, sys

# 用法：FLOW_TOKEN 环境下跑 python3 scripts/build_vocab.py
# 需要 flowus CLI 已安装并配置 token（export FLOWUS_TOKEN=...）

DB = '6da864d4-5037-41b0-997f-1db473f90f71'
OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.makedirs(OUT, exist_ok=True)

# ---------- 一、从 Flowus 拉取标记片段 ----------
rows = []
cursor = None
while True:
    body = {'page_size': 100}
    if cursor:
        body['start_cursor'] = cursor
    json.dump(body, open('/tmp/q.json', 'w'))
    r = subprocess.run(['flowus', 'api', 'call', 'POST', f'/v2/databases/{DB}/query',
                        '--body', '/tmp/q.json'], capture_output=True, text=True)
    d = json.loads(r.stdout)
    rows += d.get('results') or []
    if d.get('has_more') and d.get('next_cursor'):
        cursor = d['next_cursor']
    else:
        break

items = []
for r in rows:
    p = r.get('properties') or {}
    title = ''.join(x.get('plain_text') or '' for x in ((p.get('标题') or {}).get('title') or []))
    rt = (p.get('单词') or {}).get('rich_text') or []
    buf = []
    for x in rt:
        a = x.get('annotations') or {}
        if a.get('code') or a.get('bold'):
            buf.append(x.get('plain_text') or '')
        else:
            if buf:
                items.append((title, ''.join(buf)))
                buf = []
    if buf:
        items.append((title, ''.join(buf)))

# ---------- 二、人工释义表（无释义的补齐 / 统一口径） ----------
ZH = {
 'chick':'雏鸟（小鸡、小企鹅、小天鹅都叫 chick）',
 'hatches':'孵化、破壳',
 'down feathers':'绒羽（down 是绒毛，feather 是羽毛总称）',
 'brood pouch':'育儿袋（企鹅腹部那块皮褶）',
 'beak':'鸟喙（只有鸟才有 beak）',
 'huddles':'挤成一团、蜷缩在一起',
 'stretches its wings':'伸展翅膀',
 'stretch out to relax':'伸展开、放松',
 'on its belly':'用肚子（贴着地面）',
 'rake':'耙子（园艺工具）',
 'rock':'岩石',
 'rug':'小地毯',
 'hummingbirds':'蜂鸟',
 'gorgets':'喉部斑羽（蜂鸟会闪光的那块）',
 'bills':'鸟喙（细长的喙常说 bill）',
 'lap up':'舔食、舐食（不是 suck）',
 'nestlings':'雏鸟（还没离巢的幼鸟）',
 'from':'从……（表来源）',
 'quilt':'被子（绗缝被）',
 'gum':'口香糖（不可数）',
 'rub':'擦、搓',
 'tug':'用力拉、拽',
 'tub':'浴缸、盆',
 'marsupials':'有袋类动物',
 'hop':'单脚或双脚跳',
 'outback':'澳大利亚内陆荒野',
 'graze':'食草动物低头啃草',
 'travel in mobs':'成群活动',
 'mobs':'一群（袋鼠的群）',
 'belly':'肚子',
 'pouches':'育儿袋',
 'one another':'互相（= each other）',
 'thump':'「咚」的一声、重击',
 'spot':'发现、看到',
 'cab':'驾驶室',
 'ladders':'梯子',
 'king-size beds':'特大号床（这里指车斗）',
 'pal':'好朋友（口语，= friend）',
 'tap the pot':'敲锅',
 'pan':'平底锅',
 'is off':'不在……上面（状态）',
 'fish':'鱼；捕鱼',
 'school':'一群鱼；学校',
 'elephants':'大象',
 'herd':'兽群（象、牛等）',
 'frogs':'青蛙',
 'army':'一大群（蛙）；军队',
 'dolphins':'海豚',
 'pod':'一小群（海豚、鲸）',
 'tube':'管子',
 'flute':'长笛',
 'tune':'曲调',
 'tuba':'大号（铜管乐器）',
 'an insect':'一只昆虫',
 'igloo':'冰屋',
 'iguana':'鬣蜥',
 'inchworm':'尺蠖',
 'chilly':'冷飕飕的（比 cold 轻）',
 'feel ill':'觉得不舒服',
 'hike':'徒步',
 'pine':'松树',
 'come in':'进来',
 'see-through':'透明的',
 'jump rope':'跳绳',
 'jar':'罐子',
 'jam':'果酱',
 'jet':'喷气机',
 'mitten':'连指手套',
 'mail':'邮件',
 'mop':'拖把；拖地',
 'nail':'钉子；指甲',
 'necklace':'项链',
 'rocket':'火箭',
 'tape':'胶带',
 'top':'顶部',
 'den':'洞穴（野兽的窝）',
 'pig':'猪',
 'wig':'假发',
 'jig':'吉格舞',
 'vehicle':'车辆',
 'cone':'圆锥；蛋筒',
 'hay':'干草',
 'ram':'公羊',
 'bat':'蝙蝠；球棒',
 'cereal':'麦片',
 'cage':'笼子',
 'moose':'驼鹿',
 'flames':'火焰',
 'berry':'浆果',
 'broccoli':'西兰花',
 'apricot':'杏',
 'pickle':'腌黄瓜',
 'plum':'李子',
 'pepper':'胡椒；辣椒',
 'toast':'吐司',
 'tie':'领带；系',
 'bowl':'碗',
 'bow':'弓；蝴蝶结',
 'pretzel':'椒盐卷饼',
 'avocado':'牛油果',
 'cut leaves into pieces':'把叶子切成碎片',
 'fungus':'真菌（复数 fungi）',
 'squeak':'吱吱叫',
 'oink':'哼哼（猪叫）',
 'meh':'咩（羊叫）',
 'neigh':'嘶——（马叫）',
 'tweet':'啾啾（鸟叫）',
 'cluck':'咯咯（母鸡叫）',
 'baaa':'咩——（羊叫）',
 'quack':'嘎嘎（鸭叫）',
 'ribbit':'呱呱（蛙叫）',
 'meow':'喵（猫叫）',
 'cock-a-doodle-doo':'喔喔喔（公鸡叫）',
 'skunk':'臭鼬',
 'crow':'乌鸦；啼叫',
 'toad':'蟾蜍',
 'turtle':'水龟',
 'tortoise':'陆龟',
 'trip over sth':'被……绊倒',
 'jumping up and down':'上上下下地跳',
 'fade':'褪色、变淡',
 'referee':'裁判（足球、篮球用 referee）',
 'count off':'报数',
 'bonds with its owner':'和主人建立感情',
 'belly rubs':'揉肚子',
 'roar':'轰鸣；吼叫',
 'spoiler':'尾翼（扰流板）',
 'slices':'切开、划开',
 'horsepower':'马力',
 'fight for first':'争第一',
 'hatch':'孵化',
 'brood':'一窝雏鸟',
 'waddle':'摇摇摆摆地走',
 'paddle':'划水',
 'stick':'棍子；粘',
 'cuddle':'依偎',
 'huddle':'挤成一团',
 'pile':'堆',
 'chase one another':'互相追逐',
 'cheetah':'猎豹',
 'camouflage':'伪装',
 'every few days':'每隔几天',
 'is born':'出生',
 'trots':'小跑',
 'gallops':'飞奔',
 'grains':'谷物',
 'yearlings':'一岁的小马',
 'cot':'帆布床',
 'mat':'垫子',
 'mud':'泥',
 'off':'离开、不在……上',
 'donuts':'甜甜圈（赛车原地打转的胎印）',
 'slap wheelie':'后轮特技（抬前轮跑）',
 'exercise':'锻炼',
 'is mad at':'生……的气',
 'apologizes to':'向……道歉',
 'share an apple':'分享一个苹果',
 'fluffy teddy bears':'毛茸茸的泰迪熊',
 'fish for salmon':'捕鲑鱼',
 'frown':'皱眉',
 'squirm':'扭动',
 'wiggled':'扭来扭去',
 'sit still':'坐着不动',
 'calf':'小牛；小象',
 'struggles':'挣扎、费力',
 'gives a lift':'帮一把',
 'trumpets for help':'吹号求救',
 'circles close':'围拢过来',
 'tight':'紧紧地',
 'upper lip':'上唇',
 'joey':'有袋类宝宝的统称',
 'jelly':'果冻',
 'clings':'紧紧抓住',
 'jelly bean':'软心豆粒糖',
 'pouch':'育儿袋',
 'vat':'大桶、缸',
 'ham':'火腿',
 'yam':'山药',
 'yum':'好吃',
 'amphibians with tails':'有尾巴的两栖动物',
 'shed skin':'蜕皮',
 'shade':'阴凉处',
 'grab prey':'抓住猎物',
 'poisonous snake':'毒蛇',
 'an attack':'一次攻击',
 'broad':'宽的',
 'spin':'旋转',
 'earth':'地球；泥土',
 'souvenir':'纪念品',
 'as':'当……时；作为',
 'pit':'坑；果核',
 'fit':'合身、装得下',
 'volcano':'火山',
 'vest':'背心',
 'vase':'花瓶',
 'vine':'藤',
 'growl':'低吼',
 'snap at someone':'冲某人发火',
 'by staying':'通过待着（by + doing）',
 'jumped up':'跳起来',
 'in a slump':'状态低迷',
 'lift':'举起；搭便车',
 'open a book':'打开书',
 'flip through a book':'翻书',
 'bond':'纽带；建立感情',
 'yo-yo':'溜溜球',
 'yarn':'毛线',
 'yak':'牦牛',
 'wagon':'小推车',
 'lane':'小巷、车道',
 'grasslands':'草原',
 'curl up':'蜷缩起来',
 'litter':'一窝（同胎幼崽）',
 'kittens':'小猫',
 'purr':'（猫）呼噜呼噜叫',
 'big yawn':'大打哈欠',
 'bagpipes':'风笛',
 'maracas':'沙锤',
 'harp':'竖琴',
 'xylophone':'木琴',
 'gong':'锣',
 'clarinet':'单簧管',
 'whistle':'哨子；吹哨',
 'accordion':'手风琴',
 'rainstick':'雨声筒',
 'mandolin':'曼陀林',
 'bib':'围嘴',
 'stem':'茎',
 'get on':'上去、爬上',
 'fit on':'装得下、挤得下',
 'fly':'苍蝇；飞',
 'fence':'篱笆',
 'kits':'小崽（兔、狐等）',
 'litters':'一窝窝',
 'shed':'掉（毛、皮）',
 'leap into the air':'腾空跃起',
 'fluff':'使蓬松',
 'race along tracks':'沿着赛道飞驰',
 'tires':'轮胎',
 'speed over big jumps':'飞速冲过大跳台',
 'do wild tricks':'做疯狂特技',
 'turn in circles':'原地打转',
}

# 明确丢弃：句子片段、标题、纯语法词
DROP = {
 "i like to hike", "we can hike up", "born in dens", "in the den",
 "life with the litter", "playful piglets", "kodi's slump was over",
 "a slump was over", "think a little harder", "to keep", "to be", "the best",
}

words = {}
for title, raw in items:
    s = raw.strip()
    if not s or s in ('-', '—', ')'):
        continue
    if '(' in s:
        eng, rest = s.split('(', 1)
    else:
        eng, rest = s, ''
    eng = eng.strip().strip('.').strip()
    if not re.fullmatch(r"[A-Za-z][A-Za-z \-'/]{0,34}", eng):
        continue
    if len(eng.replace(' ', '')) < 2:
        continue
    if len(eng.split()) > 4:
        continue
    key = eng.lower()
    key = re.sub(r'\s+', ' ', key)
    if key in DROP:
        continue
    # 拼写修正
    if key == 'rumpets for help':
        key = 'trumpets for help'
    if key == 'yoyo':
        key = 'yo-yo'

    zh = ZH.get(key, '')
    if key in words:
        if zh and not words[key]['zh']:
            words[key]['zh'] = zh
        if title and title not in words[key]['src']:
            words[key]['src'].append(title)
    else:
        words[key] = {'en': key, 'zh': zh, 'src': [title] if title else []}

final = [v for v in words.values() if v['zh']]
missing = [v['en'] for v in words.values() if not v['zh']]
print('保留条目:', len(final), '| 缺释义被剔除:', len(missing))
if missing:
    print('缺释义:', missing)

# ---------- 三、按课程分组 ----------
def group_of(src):
    s = ' '.join(src)
    for kw, g in [
        ('Penguin', 'Baby Penguins'), ('Hummingbird', 'Hummingbirds'), ('Rabbits', 'Rabbits'),
        ('Gum on the Rug', 'Gum on the Rug'), ('Look at My Pen', 'Look at My Pen'),
        ('Look at It Go', 'Look at It Go'), ('Kangaroos', 'Kangaroos'),
        ('Dump Trucks', 'Dump Trucks'), ('Sad Ollo', 'Sad Ollo'), ('Off the Rug', 'Off the Rug'),
        ('Animal Groups', 'Animal Groups'), ('Peck Plays a Tune', 'Peck Plays a Tune'),
        ('Igloo', 'Into the Igloo'), ('Nice Day', 'A Nice Day'), ('Mud', 'Mud'),
        ('Queen', 'The Queen’s Quilt'), ('Tigers', 'Baby Tigers'), ('Horses', 'Baby Horses'),
        ('Cars', 'Monster Cars'), ('Trucks', 'Monster Trucks'), ('Astronaut', 'Astronaut and Ant'),
        ('Elephants', 'Baby Elephants'), ('Cheetahs', 'Baby Cheetahs'), ('Dogs', 'Baby Dogs'),
        ('Ducks', 'Baby Ducks'), ('Frog', 'The Frog and the Fly'), ('Peacocks', 'Peacocks'),
        ('Red Pandas', 'Red Pandas'), ('Seeds', 'Seeds Grow'), ('Big Bed', 'The Big Bed'),
        ('Being Together', 'Being Together'), ('Play Ball', 'Play Ball'),
    ]:
        if kw.lower() in s.lower():
            return g
    return '其他'

for v in final:
    v['src'] = v['src'] or ['其他']
    v['group'] = v['src'][0]

final.sort(key=lambda x: (x['group'], x['en']))

json.dump(final, open(f'{OUT}/words.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# CSV
import csv
with open(f'{OUT}/words.csv', 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(['单词', '中文', '来源课程'])
    for v in final:
        w.writerow([v['en'], v['zh'], ' / '.join(v['src'])])

# words.js（给 HTML 用，避免 file:// 下的 fetch 限制）
js = 'window.WORDS = ' + json.dumps(final, ensure_ascii=False, indent=1) + ';\n'
open(f'{OUT}/words.js', 'w', encoding='utf-8').write(js)

# Markdown
lines = ['# 英语生词库', '',
         f'共 **{len(final)}** 条，来自 Flowus 绘本笔记里标记为「生疏」的词（代码块/加粗）。',
         '', '按课程分组，方便按主题出题。', '']
from itertools import groupby
for g, grp in groupby(final, key=lambda x: x['group']):
    items_g = list(grp)
    lines.append(f'## {g}（{len(items_g)}）')
    lines.append('')
    lines.append('| 单词 | 中文 |')
    lines.append('| --- | --- |')
    for v in items_g:
        lines.append(f"| {v['en']} | {v['zh']} |")
    lines.append('')
open(f'{OUT}/words.md', 'w', encoding='utf-8').write('\n'.join(lines))

print('已生成 words.json / words.csv / words.js / words.md')
print('分组统计:')
from collections import Counter
for k, n in Counter(v['group'] for v in final).most_common():
    print(f'  {k}: {n}')
