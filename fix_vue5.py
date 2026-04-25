# 重新读取文件并正确地添加 el-dialog
with open('C:/Users/yangy/myfile/PAPER/moral-ABM/python/frontend/src/views/SimulationConsole.vue', 'r', encoding='utf-8') as f:
    lines = f.readlines()

el_dialog_content = [
    '    <!-- Prompt详情对话框 -->\n',
    '    <el-dialog\n',
    '      v-model="showPromptDetail"\n',
    '      title="LLM Prompt详情"\n',
    '      width="80%"\n',
    '    >\n',
    '      <div v-if="selectedPrompt">\n',
    '        <el-tabs>\n',
    '          <el-tab-pane label="System Prompt">\n',
    '            <el-input\n',
    '              type="textarea"\n',
    '              :rows="20"\n',
    '              :model-value="selectedPrompt.full_system_prompt"\n',
    '              readonly\n',
    '            />\n',
    '          </el-tab-pane>\n',
    '          <el-tab-tab-pane label="User Prompt">\n',
    '            <el-input\n',
    '              type="textarea"\n',
    '              :rows="20"\n',
    '              :model-value="selectedPrompt.full_prompt"\n',
    '              readonly\n',
    '            />\n',
    '          </el-tab-pane>\n',
    '          <el-tab-pane label="LLM响应">\n',
    '            <el-input\n',
    '              type="textarea"\n',
    '              :rows="10"\n',
    '              :model-value="JSON.stringify(selectedPrompt.full_response, null, 2)"\n',
    '              readonly\n',
    '            />\n',
    '          </el-tab-pane>\n',
    '        </el-tabs>\n',
    '        <el-descriptions style="margin-top: 10px;" :column="2" border size="small">\n',
    '          <el-descriptions-item label="智能体">\n',
    '            {{ selectedPrompt.agent_name }} (ID: {{ selectedPrompt.agent_id }})\n',
    '          </el-descriptions-item>\n',
    '          <el-descriptions-item label="阶段">\n',
    '            {{ selectedPrompt.stage }}\n',
    '          </el-descriptions-item>\n',
    '          <el-descriptions-item label="延迟">\n',
    '            {{ selectedPrompt.latency_ms }} ms\n',
    '          </el-descriptions-item>\n',
    '          <el-descriptions-item label="时间戳">\n',
    '            {{ selectedPrompt.timestamp }}\n',
    '          </el-descriptions-item>\n',
    '        </el-descriptions>\n',
    '      </div>\n',
    '      <div v-else-if="llmPrompts.length > 0">\n',
    '        <el-collapse>\n',
    '          <el-collapse-item\n',
    '            v-for="(prompt, index) in llmPrompts"\n',
    '            :key="index"\n',
    '            :title="`${prompt.agent_name} (${prompt.stage})`"\n',
    '          >\n',
    '            <el-tabs>\n',
    '              <el-tab-pane label="System Prompt">\n',
    '                <el-input\n',
    '                  type="textarea"\n',
    '                  :rows="15"\n',
    '                  :model-value="prompt.full_system_prompt"\n',
    '                  readonly\n',
    '                />\n',
    '              </el-tab-pane>\n',
    '              <el-tab-pane label="User Prompt">\n',
    '                <el-input\n',
    '                  type="textarea"\n',
    '                  :rows="15"\n',
    '                  :model-value="prompt.full_prompt"\n',
    '                  readonly\n',
    '                />\n',
    '              </el-tab-pane>\ne',
    '              <el-tab-pane label="LLM响应">\n',
    '                <el-input\n',
    '                  type="textarea"\n',
    '                  :rows="15"\n',
    '                  :model-value="JSON.stringify(prompt.full_response, null, 2)"\n',
    '                  readonly\n',
    '                />\n',
    '              </el-tab-pane>\n',
    '            </el-tabs>\n',
    '          </el-collapse-item>\n',
    '        </el-collapse>\n',
    '      </div>\n',
    '      <div v-else>\n',
    '        <el-empty description="暂无LLM Prompt数据" />\n',
    '      </div>\n',
    '    </el-dialog>\n',
]

# 找到错误的 el-dialog（在 </template> 标签前）
found_wrong_dialog = False
wrong_dialog_start = -1
wrong_dialog_end = -1

for i, line in enumerate(lines):
    if '<!-- Prompt详情对话框-->' in line:
        # 检查这个是否在正确的位置（</template> 之前）
        # 查找最近的 </template>
        recent_template = False
        for j in range(i-1, max(0, i-50), -1):
            if '</template>' in lines[j]:
                recent_template = True
                break
        if not recent_template:
            # 这是一个错误的 el-dialog
            found_wrong_dialog = True
            wrong_dialog_start = i
            # 找到对应的 </el-dialog>
            for j in range(i, min(len(lines), i+50)):
                if '</el-dialog>' in lines[j]:
                    wrong_dialog_end = j + 1
                    break
            break

if found_wrong_dialog:
    print(f'Found wrong el-dialog at lines {wrong_dialog_start+1}-{wrong_dialog_end+1}')
    # 删除错误的 el-dialog
    lines = lines[:wrong_dialog_start] + lines[wrong_dialog_end:]

# 找到最后一个 </template> 并在它之前插入 el-dialog
template_end_found = False
for i in range(len(lines) - 1, -1, -1):
    if '</template>' in lines[i]:
        print(f'Found last </template> at line {i+1}')
        # 在这里之前插入 el-dialog
        lines[i:i] = el_dialog_content + lines[i:i]
        template_end_found = True
        break

if template_end_found:
    # 写回文件
    with open('C:/Users/yangy/myfile/PAPER/moral-ABM/python/frontend/src/views/SimulationConsole.vue', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print('Fixed: el-dialog added before last </template>')
else:
    print('Could not find last </template>')
