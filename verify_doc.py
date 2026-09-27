# -*- coding: utf-8 -*-
import re
import win32com.client

DOC = r'c:\Users\应轩旸\Desktop\杭航信息聚合.doc'

app = win32com.client.Dispatch('Kwps.Application')
app.Visible = False
doc = app.Documents.Open(DOC)

rng = doc.Content
# 关键：开启包含隐藏文字
rng.TextRetrievalMode.IncludeHiddenText = True
full = rng.Text

marks = re.findall(r'\[(\d{2}-\d{2})\]', full)
print('含隐藏文字的总长度:', len(full))
print('可读出的时间标记数量:', len(marks))
print('时间标记列表:', marks)

# 再确认：默认（不含隐藏）时看不到时间
rng2 = doc.Content
rng2.TextRetrievalMode.IncludeHiddenText = False
visible = rng2.Text
print('可见文本长度:', len(visible))
print('可见文本是否含 [09-01]:', '[09-01]' in visible)

doc.Close(False)
app.Quit()
