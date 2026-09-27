import json
import os
import subprocess
import sys

BASE = r'c:\Users\应轩旸\Documents\trae_projects\001'
OUTDIR = os.path.join(BASE, 'export')

env = dict(os.environ)
env['CHATLOG_KEEPER_DATA_DIR'] = os.path.join(BASE, 'keeper-data')
env['PYTHONIOENCODING'] = 'utf-8'
env['CHATLOG_WECHAT_DATA_ROOT'] = r'E:\微信\微信聊天记录\xwechat_files'

os.makedirs(OUTDIR, exist_ok=True)
r = subprocess.run(
    [sys.executable, '-u', '-m', 'chatlog_keeper.cli', 'wechat',
     '--days', '7', '--out', OUTDIR,
     '--data-root', r'E:\微信\微信聊天记录\xwechat_files',
     '--conversation', '47450936218@chatroom'],
    stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, cwd=BASE, timeout=600)
print('exit:', r.returncode)
out = r.stdout.decode('utf-8', 'replace')
err = r.stderr.decode('utf-8', 'replace')
print('stdout:', out[-2000:])
if err.strip():
    print('stderr:', err[-800:])

for root, dirs, files in os.walk(OUTDIR):
    for name in files:
        p = os.path.join(root, name)
        print(f'{os.path.getsize(p):>12}  {p}')
