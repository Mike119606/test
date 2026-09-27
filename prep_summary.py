import json
import os
import time

BASE = r'c:\Users\应轩旸\Documents\trae_projects\001'
SRC = os.path.join(BASE, 'export', 'wechat_messages.json')
DST = os.path.join(BASE, 'export', 'messages_compact.txt')

msgs = json.load(open(SRC, encoding='utf-8'))
msgs.sort(key=lambda m: m.get('ts', 0))

TYPE_MAP = {3: '[图片]', 34: '[语音]', 43: '[视频]', 47: '[表情包]', 48: '[位置]',
            49: '[链接/文件]', 51: '[状态]', 10000: '[系统提示]', 10002: '[撤回/系统]'}

lines = []
for m in msgs:
    t = time.strftime('%m-%d %H:%M', time.localtime(m.get('ts', 0)))
    sender = str(m.get('sender', '?')).strip()
    mt = m.get('msg_type')
    content = str(m.get('content', '') or '').replace('\n', ' ').strip()
    if mt == 1:
        if not content:
            continue
    else:
        content = TYPE_MAP.get(mt, f'[type={mt}]') + (' ' + content if content and mt in (10000, 49) else '')
    if len(content) > 150:
        content = content[:150] + '…'
    lines.append(f'[{t}] {sender}: {content}')

open(DST, 'w', encoding='utf-8').write('\n'.join(lines))
print('messages:', len(lines), '->', DST)
senders = {}
for m in msgs:
    s = str(m.get('sender', '?')).strip()
    senders[s] = senders.get(s, 0) + 1
print('top senders:', sorted(senders.items(), key=lambda x: -x[1])[:10])
if msgs:
    print('range:', time.strftime('%Y-%m-%d %H:%M', time.localtime(msgs[0]['ts'])),
          '->', time.strftime('%Y-%m-%d %H:%M', time.localtime(msgs[-1]['ts'])))
