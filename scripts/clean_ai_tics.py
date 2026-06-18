"""Clean AI tics from S1-G1 report per Fudan style guide."""
import re

TARGET = 'docs/id52/实验报告_S1-G1_ID52.md'

with open(TARGET, 'r', encoding='utf-8') as f:
    text = f.read()

parts = text.split('## 附录')
body = parts[0]
appendix = '## 附录' + parts[1] if len(parts) > 1 else ''

# === Replace all remaining —— in body text with 。===
# But preserve within ``` code blocks and table rows (start with |)
lines = body.split('\n')
cleaned_lines = []
for line in lines:
    if line.strip().startswith('|') or line.strip().startswith('```') or line.strip().startswith('- **'):
        cleaned_lines.append(line)
    else:
        # In prose paragraphs, replace —— with 。
        # Exception: keep —— inside quoted text ""
        # Strategy: split by —— and rejoin with 。
        if '——' in line:
            # Don't replace inside image paths (![...](...))
            parts_line = line.split('![')
            new_parts = []
            for p in parts_line:
                if p.startswith('图') and '](' in p:
                    new_parts.append(p)
                else:
                    # Replace —— with 。, cleaning up double punctuation
                    p = p.replace('——', '。')
                    p = p.replace('。。', '。')
                    p = p.replace('。，', '。')
                new_parts.append(p)
            line = '!['.join(new_parts)
        cleaned_lines.append(line)

body = '\n'.join(cleaned_lines)

# === Replace 分号 with 句号 in prose (not in tables) ===
cleaned_lines2 = []
for line in body.split('\n'):
    if line.strip().startswith('|') or line.strip().startswith('```') or line.strip().startswith('- **'):
        cleaned_lines2.append(line)
    else:
        if '；' in line:
            # Only in prose paragraphs
            line = re.sub(r'(?<![|`\-#>])；', '。', line)
            line = line.replace('。。', '。')
        cleaned_lines2.append(line)

body = '\n'.join(cleaned_lines2)

# === Remove 不是...而是 patterns (1 remaining) ===
body = body.replace(
    '所产生的体系效应不是理论预期的规范秩序扩展，而是一种等级制稳定。',
    '所产生的体系效应并非理论预期中的规范秩序扩展，是一种等级制稳定。'
)

# === Final count ===
with open(TARGET, 'w', encoding='utf-8') as f:
    f.write(body + '\n' + appendix)

# Verify
with open(TARGET, 'r', encoding='utf-8') as f:
    final = f.read()
fb = final.split('## 附录')[0]
d = len(re.findall(r'——', fb))
s = len(re.findall(r'(?<![|`\-#>])；', fb))
cn = len(re.findall(r'[一-鿿]', fb))
print(f'破折号: {d} | 分号: {s} | 中文字数: {cn}')
# Also check "不是...而是"
nb = len(re.findall(r'不是[^。]{0,30}而是', fb))
print(f'不是...而是: {nb}')
PYEOF