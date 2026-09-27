import json
import os
import subprocess
import sys

BASE = r'c:\Users\应轩旸\Documents\trae_projects\001'
OUT = os.path.join(BASE, 'directory2.json')
TARGET = '半糖德比公会'

env = dict(os.environ)
env['CHATLOG_KEEPER_DATA_DIR'] = os.path.join(BASE, 'keeper-data')
env['PYTHONIOENCODING'] = 'utf-8'
env['CHATLOG_WECHAT_DATA_ROOT'] = r'E:\微信\微信聊天记录\xwechat_files'

with open(OUT, 'wb') as f:
    r = subprocess.run(
        [sys.executable, '-u', '-m', 'chatlog_keeper.cli', 'directory',
         '--source', 'wechat', '--data-root', r'E:\微信\微信聊天记录\xwechat_files'],
        stdout=f, stderr=subprocess.PIPE, env=env, cwd=BASE)
print('exit:', r.returncode)
if r.stderr:
    print('stderr tail:', r.stderr.decode('utf-8', 'replace')[-300:])

data = json.load(open(OUT, encoding='utf-8'))
convs = data.get('conversations', [])
groups = [c for c in convs if c.get('conversation_type') == 'group']
print('total:', len(convs), 'groups:', len(groups))

hits = [c for c in convs if TARGET in str(c.get('label', ''))]
print('hits:', len(hits))
for c in hits:
    print(json.dumps(c, ensure_ascii=False))

if not hits:
    print('-- top 15 groups by message_count --')
    for c in sorted(groups, key=lambda x: x.get('message_count', 0), reverse=True)[:15]:
        print(json.dumps(c, ensure_ascii=False))
