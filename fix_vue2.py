with open('C:/Users/yangy/myfile/PAPER/moral-ABM/python/frontend/src/views/SimulationConsole.vue', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到所有 el-dialog 的行号（应该有一个在错误位置）
dialog_lines = []
for i, line in enumerate(lines):
    if '<el-dialog' in line:
        dialog_lines.append(i)

print(f'Found el-dialog at lines: {dialog_lines}')

# 找到正确的位置（</template> 之前）
for i, line in enumerate(lines):
    if line.strip() == '</template>':
        print(f'Found </template> at line {i+1}')
        # 删除错误位置的 el-dialog
        # 假设第30-122行的 el-dialog 是错误的
        if len(dialog_lines) > 0:
            # 删除从 dialog_lines[0] 到 dialog_lines[0]+91 的内容（大概是第30-122行）
            start_remove = dialog_lines[0]
            end_remove = dialog_lines[0] + 92
            print(f'Removing lines {start_remove+1} to {end_remove}')

            # 保留删除 el-dialog 之前的行和之后的新内容
            new_lines = lines[:start_remove] + lines[end_remove:]

            # 写回文件
            with open('C:/Users/yangy/myfile/PAPER/moral-ABM/python/frontend/src/views/SimulationConsole.vue', 'w', encoding='utf-8') as f:
                f.writelines(new_lines)

            print('Fixed: Removed incorrectly placed el-dialog')
            break
