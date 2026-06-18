import re
with open('docs/id52/实验报告_S1-G1_ID52.md', encoding='utf-8') as f:
    lines = f.readlines()
b_lines = []
for l in lines:
    if l.startswith('## 附录'):
        break
    b_lines.append(l)

print('=== 破折号位置 ===')
for i, l in enumerate(b_lines, 1):
    if '——' in l:
        print(f'L{i}: {l.rstrip()[:100]}')
print()
print('=== 分号位置 ===')
for i, l in enumerate(b_lines, 1):
    if '；' in l and not l.strip().startswith('|') and not l.strip().startswith('```') and not l.strip().startswith('- **'):
        print(f'L{i}: {l.rstrip()[:100]}')
print()
print('=== 不是...而是位置 ===')
for i, l in enumerate(b_lines, 1):
    if re.search(r'不是.{0,30}而是', l):
        print(f'L{i}: {l.rstrip()[:120]}')
