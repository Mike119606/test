# -*- coding: utf-8 -*-
"""把 杭航信息.md 的内容写入 杭航信息聚合.doc（时间标记设为隐藏文字）"""
import re
import win32com.client

MD = r'c:\Users\应轩旸\Desktop\杭航信息.md'
DOC = r'c:\Users\应轩旸\Desktop\杭航信息聚合.doc'

with open(MD, encoding='utf-8') as f:
    content = f.read()

# 启动 WPS（个人版 Kwps.Application，失败则试专业版 WPS.Application）
app = None
for progid in ('Kwps.Application', 'WPS.Application'):
    try:
        app = win32com.client.Dispatch(progid)
        break
    except Exception:
        continue
if app is None:
    raise RuntimeError('无法启动 WPS COM 接口')

app.Visible = False
doc = app.Documents.Open(DOC)

sel = app.Selection
sel.WholeStory()
sel.Delete()
sel.HomeKey(6)  # wdStory，跳到文档开头

for raw in content.split('\n'):
    line = raw.rstrip()
    if not line.strip():
        continue
    if line.startswith('# '):
        sel.TypeText(line[2:].strip())
        sel.Font.Bold = True
        sel.Font.Size = 16
        sel.TypeParagraph()
        sel.Font.Bold = False
        sel.Font.Size = 10.5
    elif line.startswith('> '):
        sel.TypeText(line[2:].strip())
        sel.Font.Italic = True
        sel.Font.Size = 9
        sel.TypeParagraph()
        sel.Font.Italic = False
        sel.Font.Size = 10.5
    elif line.startswith('## '):
        sel.TypeParagraph()
        sel.TypeText(line[3:].strip())
        sel.Font.Bold = True
        sel.Font.Size = 12
        sel.TypeParagraph()
        sel.Font.Bold = False
        sel.Font.Size = 10.5
    elif line.startswith('- '):
        m = re.match(r'- (.*?)\s*<!--\s*([\d-]+)\s*-->\s*$', line)
        if m:
            body = m.group(1).strip()
            timemark = m.group(2).strip()
        else:
            body = line[2:].strip()
            timemark = None
        # 处理 **bold** 标记，转成 Word 加粗
        for part in re.split(r'(\*\*.*?\*\*)', body):
            if part.startswith('**') and part.endswith('**') and len(part) > 4:
                sel.Font.Bold = True
                sel.TypeText(part[2:-2])
                sel.Font.Bold = False
            elif part:
                sel.TypeText(part)
        if timemark:
            sel.Font.Hidden = True
            sel.TypeText(' [' + timemark + ']')
            sel.Font.Hidden = False
        sel.TypeParagraph()
    elif line.strip() == '---':
        continue
    else:
        sel.TypeText(line.strip())
        sel.TypeParagraph()

doc.Save()
doc.Close()
app.Quit()
print('DONE')
