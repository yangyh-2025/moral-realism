import re
with open('docs/id52/实验报告_S1-G1_ID52.md', encoding='utf-8') as f:
    t = f.read()
b = t.split('## 附录')[0]
print('破折号:', len(re.findall(r'——', b)))
print('分号:', len(re.findall(r'(?<![|`#-])；', b)))
print('不是而是:', len(re.findall(r'不是.{0,30}而是', b, re.DOTALL)))
print('值得注意的是:', len(re.findall(r'值得注意的是', b)))
print('与此同时:', len(re.findall(r'与此同时', b)))
print('图引用:', len(re.findall(r'!\[图', t)))
print('中文字数:', len(re.findall(r'[一-鿿]', b)))
